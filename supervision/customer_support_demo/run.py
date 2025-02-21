import json

# Import Asteroid SDK components
from asteroid_sdk.supervision.decorators import supervise, supervisor
from asteroid_sdk.supervision.config import (
    SupervisionDecision,
    SupervisionDecisionType,
    ExecutionMode,
    RejectionPolicy,
    MultiSupervisorResolution,
)
from asteroid_sdk.supervision.base_supervisors import (
    human_supervisor
)
from asteroid_sdk.wrappers.openai import asteroid_openai_client
from asteroid_sdk.registration.initialise_project import asteroid_init, asteroid_end
from asteroid_sdk.supervision.config import SupervisionContext

from openai import OpenAI
from openai.types.chat import ChatCompletionMessage

# Execution settings for Asteroid
EXECUTION_SETTINGS = {
    "execution_mode": ExecutionMode.SUPERVISION,
    "allow_tool_modifications": True,
    "rejection_policy": RejectionPolicy.RESAMPLE_WITH_FEEDBACK,
    "n_resamples": 1,
    "multi_supervisor_resolution": MultiSupervisorResolution.ALL_MUST_APPROVE,
    "remove_feedback_from_context": True,
}

def _process_refund(customer_id: str, amount: float):
    """Process a refund for a customer."""
    # For demo purposes, just return a confirmation message
    return f"Refund of ${amount} processed for customer {customer_id}."


# Define maximum allowed refund amount
MAX_REFUND_AMOUNT = 800.0

# Supervisor to check refund amount limits
@supervisor
def amount_supervisor(
    message: ChatCompletionMessage,
    **kwargs
) -> SupervisionDecision:
    """Supervisor that checks if the refund amount exceeds the allowed limit."""
    # Extract the 'amount' argument from the tool call
    if not message.tool_calls:
        return SupervisionDecision(
            decision=SupervisionDecisionType.APPROVE,
            explanation="No tool calls found in the message."
        )

    # Assuming the first tool call is the one we're interested in
    tool_call = message.tool_calls[0]
    arguments = json.loads(tool_call.function.arguments)
    amount = arguments.get("amount", 0)

    if amount > MAX_REFUND_AMOUNT:
        return SupervisionDecision(
            decision=SupervisionDecisionType.ESCALATE,
            explanation=(
                f"The refund amount (${amount}) exceeds the maximum allowed amount (${MAX_REFUND_AMOUNT}). "
            )
        )
    else:
        return SupervisionDecision(
            decision=SupervisionDecisionType.APPROVE,
            explanation=f"Refund amount is within the allowed limit of ${MAX_REFUND_AMOUNT}."
        )


@supervisor
def shipping_status_supervisor(
    message: ChatCompletionMessage,
    supervision_context: SupervisionContext,
    **kwargs
) -> SupervisionDecision:
    """Supervisor that ensures the agent has verified the shipping status."""
    # Check conversation history for shipping status verification
    shipping_verified = False
    messages = supervision_context.openai_messages
    for msg in messages:
        if msg['role'] == 'assistant' and "shipping" in msg.get("content", "").lower():
            shipping_verified = True
            break

    if not shipping_verified:
        return SupervisionDecision(
            decision=SupervisionDecisionType.ESCALATE,
            explanation="Agent did not verify shipping status before processing the refund."
        )
    else:
        return SupervisionDecision(
            decision=SupervisionDecisionType.APPROVE,
            explanation="Shipping status verified."
        )

# Supervisor to ensure customer is authenticated
@supervisor
def authentication_supervisor(
    message: ChatCompletionMessage,
    supervision_context: SupervisionContext,
    **kwargs
) -> SupervisionDecision:
    """Supervisor that checks if the customer is authenticated."""
    # Check conversation history for customer authentication
    
    customer_authenticated = True
    
    if not customer_authenticated:
        return SupervisionDecision(
            decision=SupervisionDecisionType.ESCALATE,
            explanation="Customer is not authenticated."
        )
    else:
        return SupervisionDecision(
            decision=SupervisionDecisionType.APPROVE,
            explanation="Customer authenticated."
        )

# Supervisor to ensure agent attempts resolution first
@supervisor
def resolution_attempt_supervisor(
    **kwargs
) -> SupervisionDecision:
    """Supervisor that checks if the agent attempted to resolve the issue."""
    # Check conversation history for resolution attempts
    resolution_attempted = True

    if not resolution_attempted:
        return SupervisionDecision(
            decision=SupervisionDecisionType.ESCALATE,
            explanation="Agent did not attempt to resolve the issue before processing the refund."
        )
    else:
        return SupervisionDecision(
            decision=SupervisionDecisionType.APPROVE,
            explanation="Agent attempted to resolve the issue by asking the customer to wait a bit longer before proceeding to refund."
        )


# Wrap the refund tool with Asteroid supervisors
@supervise(
    supervision_functions=[
        [authentication_supervisor, human_supervisor()],
        [amount_supervisor, human_supervisor()],
        [resolution_attempt_supervisor, human_supervisor()],
        [shipping_status_supervisor, human_supervisor()]
    ]
)
def process_refund(customer_id: str, amount: float):
    """Process a refund for a customer"""
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



# Initialize Asteroid run
run_id = asteroid_init(project_name="Customer Support AI Agent Demo", task_name="Refund Processing", execution_settings=EXECUTION_SETTINGS)

# Initialize the OpenAI client
client = OpenAI()

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

# remove the last message
messages = messages[:-1]

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
        
messages.append({"role": "user", "content": "Yes, the shipping status is 'Not dispatched yet.'"})

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