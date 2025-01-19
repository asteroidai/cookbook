from typing import Any, List, Union, Optional
from uuid import UUID

from anthropic import Anthropic
from anthropic.types import ToolChoiceParam, ToolChoiceAutoParam, ToolParam, ToolUseBlock, TextBlock, Message, ToolResultBlockParam
from openai.types.chat import ChatCompletionMessage
from asteroid_sdk.wrappers.anthropic import asteroid_anthropic_client
from asteroid_sdk.supervision.decorators import supervise, supervisor
from asteroid_sdk.supervision.config import SupervisionDecision, SupervisionDecisionType, ExecutionMode, RejectionPolicy, MultiSupervisorResolution
from asteroid_sdk.supervision.base_supervisors import human_supervisor, llm_supervisor
from asteroid_sdk.registration.initialise_project import asteroid_init, asteroid_end


def max_price_supervisor(max_price: float):
    """Supervisor that rejects if the price is greater than the max price."""
    @supervisor
    def max_price_supervisor(
        message: Union[ChatCompletionMessage, Message],
        **kwargs
    ) -> SupervisionDecision:
        
        if not isinstance(message, Message):
            raise ValueError("Message is not an instance of Anthropic Message")

        # Check if the message contains content blocks
        if hasattr(message, 'content') and isinstance(message.content, list):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    print(f"Supervisor received tool call: {block}")
                    # Assuming block.input contains price information
                    price = block.input.get('price', None)
                    if price is not None and price > max_price:
                        return SupervisionDecision(
                            decision=SupervisionDecisionType.REJECT,
                            explanation=f"Price {price} exceeds maximum allowed price of {max_price}."
                        )
        
        # Default decision if no escalation is needed
        return SupervisionDecision(
            decision=SupervisionDecisionType.APPROVE,
            explanation="Price is within the acceptable range."
        )

    return max_price_supervisor


# No supervision, always approved
@supervise()
def get_weather(location: str, unit: str):
    """Get the weather in a city."""
    return f"The weather in {location} is 3 {unit}."

# Reject if the price is greater than 300
@supervise(supervision_functions=[[max_price_supervisor(max_price=300)]])
def book_hotel(location: str, checkin: str, checkout: str, price: float):
    """Book a hotel."""
    return f"Hotel booked in {location} from {checkin} to {checkout} for {price}."

# Escalate to human if the flight is from the United States
@supervise(supervision_functions=[[llm_supervisor(instructions="Escalate to human if the flight is from the United States.", provider="anthropic"), human_supervisor()]])
def book_flight(departure_city: str, arrival_city: str, datetime: str, price: float):
    """Book a flight ticket."""
    return f"Flight booked from {departure_city} to {arrival_city} on {datetime} for {price}."



tools: list[ToolParam] = [
    {
        "name": "get_weather",
        "description": "Get the weather for a specific location",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {"type": "string"},
                "unit": {"type": "string", "enum": ["c", "f"]},
            },
            "required": ["location", "unit"],
            "additionalProperties": False,
        },
    },
    {
        "name": "book_flight",
        "description": "Book a flight ticket",
        "input_schema": {
            "type": "object",
            "properties": {
                "departure_city": {"type": "string"},
                "arrival_city": {"type": "string"},
                "datetime": {"type": "string"},
                "price": {"type": "number"},
            },
            "required": ["departure_city", "arrival_city", "datetime", "price"],
            "additionalProperties": False,
        },
    },
    {
        "name": "book_hotel",
        "description": "Book a hotel",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {"type": "string"},
                "checkin": {"type": "string"},
                "checkout": {"type": "string"},
                "price": {"type": "number"},
            },
            "required": ["location", "checkin", "checkout", "price"],
            "additionalProperties": False,
        },
    },
]

client = Anthropic()

EXECUTION_SETTINGS = {
    "execution_mode": ExecutionMode.SUPERVISION, # can be "monitoring" or "supervision", monitoring is async and supervision is sync by default
    "allow_tool_modifications": True, # allow the tool to be modified by the supervisor
    "rejection_policy": RejectionPolicy.RESAMPLE_WITH_FEEDBACK, # policy to use when the supervisor rejects the tool call
    "n_resamples": 1, # number of resamples to use when the supervisor rejects the tool call
    "multi_supervisor_resolution": MultiSupervisorResolution.ALL_MUST_APPROVE, # resolution strategy when multiple supervisors are running in parallel
    "remove_feedback_from_context": True, # remove the feedback from the context
}

for i in range(1):
    run_id = asteroid_init(
        project_name="Anthropic Tools Quickstart",
        task_name="Booking Assistant",
        execution_settings=EXECUTION_SETTINGS
    )
    # When you wrap the client, all supervised functions will be registered
    wrapped_client = asteroid_anthropic_client(client, run_id, EXECUTION_SETTINGS["execution_mode"])

# Initialize conversation history
messages = []

# Run 5 interactions
for i in range(5):
    # Get user input
    user_input = input(f"\nEnter message {i+1}/5: ")

    # Add user message to history
    messages.append({"role": "user", "content": user_input})

    response = wrapped_client.messages.create(
        model="claude-3-5-haiku-latest",
        max_tokens=1024,
        messages=messages,
        tools=tools,
        tool_choice=ToolChoiceAutoParam(type="auto", disable_parallel_tool_use=True),
    )
    # Make API call
    assistant_message = response.content

    message_text: str|None = None
    tool_calls: List[ToolUseBlock]|None = None
    for message in assistant_message:
        if isinstance(message, ToolUseBlock):
            # We only allow 1 tool call for now
            tool_calls = [message]
        elif isinstance(message, TextBlock):
            message_text = message.text

    if message:
        print(f"Assistant: {message_text}")
        
    messages.append({"role": "assistant", "content": [message.to_dict()]})

    # If there are tool calls, execute them and add their results to the conversation
    if tool_calls:
        
        for tool_call in tool_calls:
            function_name = tool_call.name
            function_args = tool_call.input

            # Execute the function
            print(f"Executing function: {function_name} with args: {function_args}")

            if function_name == "get_weather":
                result = get_weather(**function_args)
            elif function_name == "book_flight":
                result = book_flight(**function_args)
            elif function_name == "book_hotel":
                result = book_hotel(**function_args)

            print(f"Function result: {result}")
            # Add the function response to messages
            messages.append({"role": "user", "content": [ToolResultBlockParam(type="tool_result", tool_use_id=tool_call.id, content=result)]})

asteroid_end(run_id)