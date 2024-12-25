import json
from typing import Any, List, Union

from asteroid_sdk.supervision.decorators import supervise, supervisor
from asteroid_sdk.supervision.config import (
    SupervisionDecision,
    SupervisionDecisionType,
    ExecutionMode,
    RejectionPolicy,
    MultiSupervisorResolution,
    SupervisionContext,
)
from asteroid_sdk.supervision.base_supervisors import human_supervisor, llm_supervisor
from asteroid_sdk.wrappers.openai import asteroid_openai_client
from openai import OpenAI
from openai.types.chat import ChatCompletionMessage
from openai.types.chat.chat_completion_message_tool_call import ChatCompletionMessageToolCall

from asteroid_sdk.registration.initialise_project import asteroid_init, asteroid_end

# Define the max_price_supervisor
def max_price_supervisor(max_price: float):
    """Supervisor that rejects if the price is greater than the max price."""
    @supervisor
    def max_price_supervisor(
        message: ChatCompletionMessage,
        **kwargs
    ) -> SupervisionDecision:
        # Check if the message has tool calls
        tool_calls: List[ChatCompletionMessageToolCall] = getattr(message, 'tool_calls', [])
        if tool_calls:
            for tool_call in tool_calls:
                print(f"Supervisor received tool call: {tool_call}")

                # Extract function arguments
                function_args = json.loads(tool_call.function.arguments)

                # Check for 'price' in function arguments
                price = function_args.get('price', None)
                if price is not None and price > max_price:
                    return SupervisionDecision(
                        decision=SupervisionDecisionType.REJECT,
                        explanation=f"Price {price} exceeds maximum allowed price of {max_price}."
                    )

        # Default decision if no escalation is needed
        return SupervisionDecision(
            decision=SupervisionDecisionType.APPROVE,
            explanation=f"Price is within the acceptable range of {max_price}."
        )

    return max_price_supervisor

# Use the decorator to supervise functions
@supervise(
    supervision_functions=[[max_price_supervisor(max_price=300)]]
)
def book_flight(departure_city: str, arrival_city: str, datetime: str, price: float):
    """Book a flight ticket."""
    return f"Flight booked from {departure_city} to {arrival_city} on {datetime} for ${price}."

@supervise()
def get_weather(location: str, unit: str):
    """Get the weather in a city."""
    return f"The weather in {location} is 25 degrees {unit.upper()}."

@supervise(
    supervision_functions=[
        [llm_supervisor(instructions="Escalate to human if the hotel is in the United States."), human_supervisor()]
    ]
)
def book_hotel(location: str, checkin: str, checkout: str, price: float):
    """Book a hotel."""
    return f"Hotel booked in {location} from {checkin} to {checkout} for ${price}."

# Define the tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the weather for a specific location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "The city to get the weather for"},
                    "unit": {"type": "string", "enum": ["c", "f"], "description": "The unit of temperature"},
                },
                "required": ["location", "unit"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "book_flight",
            "description": "Book a flight ticket",
            "parameters": {
                "type": "object",
                "properties": {
                    "departure_city": {"type": "string", "description": "The city to depart from"},
                    "arrival_city": {"type": "string", "description": "The city to arrive at"},
                    "datetime": {"type": "string", "description": "The date and time of departure"},
                    "price": {"type": "number", "description": "The price of the flight"},
                },
                "required": ["departure_city", "arrival_city", "datetime", "price"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "book_hotel",
            "description": "Book a hotel",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "The city to book the hotel in"},
                    "checkin": {"type": "string", "description": "Check-in date"},
                    "checkout": {"type": "string", "description": "Check-out date"},
                    "price": {"type": "number", "description": "The price of the hotel per night"},
                },
                "required": ["location", "checkin", "checkout", "price"],
                "additionalProperties": False,
            },
        },
    },
]

# Initialize the OpenAI client
client = OpenAI()

# Execution settings for supervision
EXECUTION_SETTINGS = {
    "execution_mode": ExecutionMode.SUPERVISION,  # "monitoring" is async; "supervision" is sync by default
    "allow_tool_modifications": True,  # Allow the tool to be modified by the supervisor
    "rejection_policy": RejectionPolicy.RESAMPLE_WITH_FEEDBACK,  # Policy when the supervisor rejects the tool call
    "n_resamples": 1,  # Number of resamples when the supervisor rejects the tool call
    "multi_supervisor_resolution": MultiSupervisorResolution.ALL_MUST_APPROVE,  # Resolution strategy when multiple supervisors are running
    "remove_feedback_from_context": True,  # Remove the feedback from the context
}

# Start the Asteroid run
run_id = asteroid_init(
    project_name="OpenAI Tools Quickstart",
    task_name="Booking Assistant",
    execution_settings=EXECUTION_SETTINGS
)

# Wrap the client to register supervised functions
wrapped_client = asteroid_openai_client(client, run_id, EXECUTION_SETTINGS["execution_mode"])

# Initialize conversation history
messages = []

# Run interactions
for i in range(5):
    # Get user input
    user_input = input(f"\nEnter message {i+1}/5: ")

    # Add user message to history
    messages.append({"role": "user", "content": user_input})

    # Make API call
    response = wrapped_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto",
        temperature=0,
        n=1,
        parallel_tool_calls=False
    )

    assistant_message: ChatCompletionMessage = response.choices[0].message

    # Add assistant's response to conversation history
    messages.append({
        "role": "assistant",
        "content": assistant_message.content or "",
        "tool_calls": assistant_message.tool_calls or []
    })

    if assistant_message.content:
        print(f"\nAssistant: {assistant_message.content}")

    # If there are tool calls, execute them and add their results to the conversation
    if assistant_message.tool_calls:
        for tool_call in assistant_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            # Execute the function
            print(f"\nExecuting function: {function_name} with args: {function_args}")

            if function_name == "get_weather":
                result = get_weather(**function_args)
            elif function_name == "book_flight":
                result = book_flight(**function_args)
            elif function_name == "book_hotel":
                result = book_hotel(**function_args)
            else:
                result = f"Function {function_name} not found."

            print(f"Function result: {result}")
            # Add the function response to messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })

asteroid_end(run_id)
