from typing import Any, List, Union, Optional
from uuid import UUID

from anthropic import Anthropic
from anthropic.types import ToolChoiceParam, ToolChoiceAutoParam, ToolParam, ToolUseBlock, TextBlock, Message
from asteroid_sdk.wrappers.gemini import asteroid_gemini_wrap_model_generate_content
from google.ai.generativelanguage_v1 import GenerateContentResponse
from openai.types.chat import ChatCompletionMessage
from asteroid_sdk.wrappers.anthropic import asteroid_anthropic_client
from asteroid_sdk.supervision.decorators import supervise, supervisor
from asteroid_sdk.supervision.config import SupervisionDecision, SupervisionDecisionType, ExecutionMode, RejectionPolicy, MultiSupervisorResolution
from asteroid_sdk.supervision.base_supervisors import human_supervisor, llm_supervisor
from asteroid_sdk.registration.initialise_project import asteroid_init, asteroid_end

import google.generativeai as genai
import os


def max_price_supervisor(max_price: float):
    """Supervisor that rejects if the price is greater than the max price."""
    @supervisor
    def max_price_supervisor(
        message: Union[ChatCompletionMessage, Message, GenerateContentResponse],
        **kwargs
    ) -> SupervisionDecision:

        # if not isinstance(message, GenerateContentResponse):
        #     raise ValueError("Message is not an instance of GenerateContentResponse.")

        # Check if the message contains content blocks
        if message.parts:
            for part in message.parts:
                if part.function_call and part.function_call.name == "book_hotel":
                    params = {arg: value for arg, value in part.function_call.args.items()}
                    # Assuming block.input contains price information
                    price = params.get('price', None)
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
# TODO - Update LLMSupervisor to use Provider Enum
@supervise(supervision_functions=[[llm_supervisor(instructions="Escalate to human if the flight is from the United States. Don't focus on anything else!!", provider="openai"), human_supervisor()]])
def book_flight(departure_city: str, arrival_city: str, datetime: str, price: float):
    """Book a flight ticket."""
    return f"Flight booked from {departure_city} to {arrival_city} on {datetime} for {price}."


EXECUTION_SETTINGS = {
    "execution_mode": ExecutionMode.SUPERVISION, # can be "monitoring" or "supervision", monitoring is async and supervision is sync by default
    "allow_tool_modifications": True, # allow the tool to be modified by the supervisor
    "rejection_policy": RejectionPolicy.NO_RESAMPLE, # policy to use when the supervisor rejects the tool call
    "n_resamples": 1, # number of resamples to use when the supervisor rejects the tool call
    "multi_supervisor_resolution": MultiSupervisorResolution.ALL_MUST_APPROVE, # resolution strategy when multiple supervisors are running in parallel
    "remove_feedback_from_context": True, # remove the feedback from the context
}


run_id = asteroid_init(
    project_name="Gemini Tools Quickstart",
    task_name="Booking Assistant",
    execution_settings=EXECUTION_SETTINGS
)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(
    "gemini-1.5-flash",
    tools=[get_weather, book_hotel, book_flight],
)

wrapped_model = asteroid_gemini_wrap_model_generate_content(
    model,
    run_id,
    EXECUTION_SETTINGS["execution_mode"],
    EXECUTION_SETTINGS["rejection_policy"]
)


 # This gets a chat client, as we'll wrap the chat method

wrapped_chat = wrapped_model.start_chat()
#
# # When you wrap the client, all supervised functions will be registered
# wrapped_chat = asteroid_gemini_chat_session(
#     chat,
#     run_id,
#     EXECUTION_SETTINGS["execution_mode"],
# )
#
# Initialize conversation history
messages = []

# Run 5 interactions
for i in range(5):
    # Get user input
    user_input = input(f"\nEnter message {i+1}/5: ")

    messages.append(user_input)

    response = wrapped_chat.send_message(user_input)
    # Make API call

    function_calls = []
    for part in response.candidates[0].content:
        if part.function_call:
            print(f"Tool Use: {part.function_call.name}")
            print(f"Arguments: {part.function_call.args}")
            function_calls.append(part.function_call)
        else:
            print(f"{response.role}: {part.text}")

        # Add assistant's response to conversation history
        messages.extend(response.parts)


    # If there are tool calls, execute them and add their results to the conversation
    if function_calls:
        for function_call in function_calls:
            function_name = function_call.name
            function_args = {arg: value for arg, value in function_call.args.items()}

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

asteroid_end(run_id)
