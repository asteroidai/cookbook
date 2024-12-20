import json
import os
from typing import Any
from openai.types.chat.chat_completion_message_tool_call import ChatCompletionMessageToolCall

# Import Asteroid SDK components
from asteroid_sdk.supervision.decorators import supervise
from asteroid_sdk.supervision.config import (
    SupervisionDecision,
    SupervisionDecisionType,
    ExecutionMode,
    RejectionPolicy,
    MultiSupervisorResolution,
)
from asteroid_sdk.supervision.supervisors import (
    human_supervisor,
    tool_supervisor_decorator,
)

from asteroid_sdk.wrappers.openai import (
    asteroid_openai_client,
    asteroid_init,
    asteroid_end,
)
from openai import OpenAI

def _process_refund(customer_id: str, amount: float):
    """Process a refund for a customer."""
    # For demo purposes, just return a confirmation message
    return f"Refund of ${amount} processed for customer {customer_id}."

# Define maximum allowed refund amount
MAX_REFUND_AMOUNT = 500.0

# Supervisor to check refund amount limits
@tool_supervisor_decorator()
def amount_supervisor(
    tool_call: ChatCompletionMessageToolCall,
    config_kwargs: dict[str, Any],
    **kwargs
) -> SupervisionDecision:
    """Supervisor that checks if the refund amount exceeds the allowed limit."""
    arguments = json.loads(tool_call.function.arguments)
    amount = arguments.get("amount", 0.0)

    if amount > MAX_REFUND_AMOUNT:
        return SupervisionDecision(
            decision=SupervisionDecisionType.ESCALATE,
            explanation=(
                f"The refund amount (${amount}) exceeds the maximum allowed amount (${MAX_REFUND_AMOUNT})."
            )
        )
    else:
        return SupervisionDecision(
            decision=SupervisionDecisionType.APPROVE,
            explanation="Refund amount is within the allowed limit."
        )

@tool_supervisor_decorator()
def shipping_status_supervisor(
    tool_call: ChatCompletionMessageToolCall,
    config_kwargs: dict[str, Any],
    messages: list[dict[str, Any]],
    **kwargs
) -> SupervisionDecision:
    """Supervisor that ensures the agent has verified the shipping status."""
    # Check conversation history for shipping status verification
    shipping_verified = False
    for message in messages:
        if "shipping status" in message.get("content", "").lower():
            shipping_verified = True
            break

    if not shipping_verified:
        return SupervisionDecision(
            decision=SupervisionDecisionType.REJECT,
            explanation="Agent did not verify shipping status before processing the refund."
        )
    else:
        return SupervisionDecision(
            decision=SupervisionDecisionType.APPROVE,
            explanation="Shipping status verified."
        )

# Supervisor to ensure customer is authenticated
@tool_supervisor_decorator()
def authentication_supervisor(
    tool_call: ChatCompletionMessageToolCall,
    config_kwargs: dict[str, Any],
    messages: list[dict[str, Any]],
    **kwargs
) -> SupervisionDecision:
    """Supervisor that checks if the customer is authenticated."""
    # Check conversation history for customer authentication
    customer_authenticated = False
    for message in messages:
        if "customer id" in message.get("content", "").lower():
            customer_authenticated = True
            break

    if not customer_authenticated:
        return SupervisionDecision(
            decision=SupervisionDecisionType.REJECT,
            explanation="Customer is not authenticated."
        )
    else:
        return SupervisionDecision(
            decision=SupervisionDecisionType.APPROVE,
            explanation="Customer authenticated."
        )

# Supervisor to ensure agent attempts resolution first
@tool_supervisor_decorator()
def resolution_attempt_supervisor(
    tool_call: ChatCompletionMessageToolCall,
    config_kwargs: dict[str, Any],
    messages: list[dict[str, Any]],
    **kwargs
) -> SupervisionDecision:
    """Supervisor that checks if the agent attempted to resolve the issue."""
    # Check conversation history for resolution attempts
    resolution_attempted = False
    for message in messages:
        if any(phrase in message.get("content", "").lower() for phrase in ["wait a bit longer", "offer discount", "expedited shipping"]):
            resolution_attempted = True
            break

    if not resolution_attempted:
        return SupervisionDecision(
            decision=SupervisionDecisionType.REJECT,
            explanation="Agent did not attempt to resolve the issue before processing the refund."
        )
    else:
        return SupervisionDecision(
            decision=SupervisionDecisionType.APPROVE,
            explanation="Agent attempted to resolve the issue before proceeding to refund."
        )


# Wrap the refund tool with supervision using the supervisors
@supervise(
    supervision_functions=[
        #[amount_supervisor],
        # [shipping_status_supervisor]
        [human_supervisor()],
        # [resolution_attempt_supervisor, human_supervisor()]
    ]
)
def process_refund(customer_id: str, amount: float):
    """Process a refund for a customer with supervision."""
    return _process_refund(customer_id, amount)

# Define the tool for the assistant
tools = [
    {
        "type": "function",
        "function": {
            "name": "process_refund",
            "description": "Process a refund for a customer",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string", "description": "The ID of the customer requesting the refund."},
                    "amount": {"type": "number", "description": "The amount to refund to the customer."},
                },
                "required": ["customer_id", "amount"],
                "additionalProperties": False,
            },
        },
    },
]

# Initialize the OpenAI client
client = OpenAI()

# Execution settings for Asteroid
EXECUTION_SETTINGS = {
    "execution_mode": ExecutionMode.SUPERVISION,
    "allow_tool_modifications": True,
    "rejection_policy": RejectionPolicy.RESAMPLE_WITH_FEEDBACK,
    "n_resamples": 1,
    "multi_supervisor_resolution": MultiSupervisorResolution.ALL_MUST_APPROVE,
    "remove_feedback_from_context": True,
}

# Initialize Asteroid run
run_id = asteroid_init(
    project_name="Customer Support Agent",
    task_name="Refund Processing",
    run_name="refund",
    execution_settings=EXECUTION_SETTINGS
)

# Wrap the OpenAI client with Asteroid
wrapped_client = asteroid_openai_client(
    client, run_id, EXECUTION_SETTINGS["execution_mode"]
)

# Initialize conversation history with both user and assistant messages
messages = [
    {"role": "user", "content": "Hi, I purchased 5 items last week and they haven't arrived yet."},
    {"role": "assistant", "content": "I'm sorry to hear that your items haven't arrived yet. Let me check the status of your order."},
    {"role": "user", "content": "I've been waiting for over a week now."},
    {"role": "assistant", "content": "Thank you for your patience. Could you please provide your order number or customer ID so I can assist you further?"},
    {"role": "user", "content": "My customer ID is 92591."},
    {"role": "assistant", "content": "Thank you! I see that your order is delayed. Would you like to wait a bit longer or would you prefer a refund?"},
    {"role": "user", "content": "Can I get a refund for my order? The total amount was $750."},
    {"role": "assistant", "content": "Certainly. I'll process a refund of $750 for you."},
]

# Assistant generates a response based on the conversation history
response = wrapped_client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=tools,
    tool_choice="auto",
    temperature=0,
    n=1,
    parallel_tool_calls=False
)

assistant_message = response.choices[0].message

# Add assistant's response to conversation history
messages.append({
    "role": "assistant",
    "content": assistant_message.content,
    "tool_calls": assistant_message.tool_calls
})

# Display assistant's response
if assistant_message.content:
    print(f"Assistant: {assistant_message.content}")

# If there are tool calls, execute them and add their results to the conversation
if assistant_message.tool_calls:
    for tool_call in assistant_message.tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)

        # Execute the supervised function
        print(f"Executing function: {function_name} with args: {function_args}")

        if function_name == "process_refund":
            result = process_refund(**function_args)

        print(f"Function result: {result}")

        # Add the function response to messages
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": str(result)
        })

# Submit the final message to the supervisor
response = wrapped_client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=tools,
    tool_choice="auto",
    temperature=0,
    n=1,
    parallel_tool_calls=False
)

# End the Asteroid run
asteroid_end(run_id)
