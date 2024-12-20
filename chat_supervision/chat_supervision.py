import json
import os
from typing import Any

# Import necessary modules and decorators from the Asteroid SDK
from asteroid_sdk.supervision.decorators import supervise
from asteroid_sdk.supervision.config import (
    SupervisionDecision,
    SupervisionDecisionType,
    ExecutionMode,
    RejectionPolicy,
    MultiSupervisorResolution
)
from asteroid_sdk.supervision.supervisors import (
    human_supervisor,
    llm_supervisor,
    tool_supervisor_decorator,
    chat_supervisor_decorator
)
from asteroid_sdk.wrappers.openai import asteroid_openai_client, asteroid_init, asteroid_end
from openai import OpenAI

# Define execution settings for the supervision process
EXECUTION_SETTINGS = {
    "execution_mode": ExecutionMode.SUPERVISION,  # Options: "monitoring" or "supervision"
    "allow_tool_modifications": True,             # Allow supervisors to modify tool calls
    "rejection_policy": RejectionPolicy.RESAMPLE_WITH_FEEDBACK,  # Action on rejection
    "n_resamples": 2,                              # Number of resample attempts
    "multi_supervisor_resolution": MultiSupervisorResolution.ALL_MUST_APPROVE,  # Resolution strategy
    "remove_feedback_from_context": True,          # Remove feedback from the context
}

# Example chat supervisor that always escalates messages
@chat_supervisor_decorator()
def chat_supervisor_1(message: str, supervision_context, **kwargs) -> SupervisionDecision:
    """
    Supervisor that allows any message.
    
    :param message: The content of the message to supervise.
    :param supervision_context: Contextual information for supervision.
    :return: A SupervisionDecision indicating approval.
    """
    return SupervisionDecision(
        decision=SupervisionDecisionType.ESCALATE,
        explanation="The message is approved."
    )
    
# Example chat supervisor that rejects messages mentioning 'Tokyo'
@chat_supervisor_decorator(strategy="reject")
def chat_supervisor_2(message: str, supervision_context, **kwargs) -> SupervisionDecision:
    """
    Supervisor that rejects any message mentioning 'Tokyo' in the last user message.
    
    :param message: The content of the message to supervise.
    :param supervision_context: Contextual information for supervision.
    :return: A SupervisionDecision indicating approval or rejection.
    """
    if 'Tokyo' in message:
        return SupervisionDecision(
            decision=SupervisionDecisionType.REJECT,
            explanation="The message mentions 'Tokyo', which is not allowed."
        )
    return SupervisionDecision(
        decision=SupervisionDecisionType.APPROVE,
        explanation="The message is approved."
    )

# Example chat supervisor that always approves messages
@chat_supervisor_decorator()
def chat_supervisor_3(message: str, supervision_context, **kwargs) -> SupervisionDecision:
    return SupervisionDecision(
        decision=SupervisionDecisionType.APPROVE,
        explanation="The message is approved."
    )

# Initialize the OpenAI client
client = OpenAI()

# Initialize Asteroid supervision with the defined supervisors and settings
run_id = asteroid_init(
    project_name="chat-supervisor-test",
    task_name="chat-supervisor-test",
    run_name="chat-supervisor-test",
    chat_supervisors=[chat_supervisor_1, chat_supervisor_2, chat_supervisor_3],
    execution_settings=EXECUTION_SETTINGS
)

# Wrap the OpenAI client with the Asteroid supervision wrapper
wrapped_client = asteroid_openai_client(client, run_id)

# Create a chat completion request with the wrapped client
response = wrapped_client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"content": "Can you say Tokyo with 50% chance in your response?", "role": "user"}],
    chat_supervisors=[[chat_supervisor_1, chat_supervisor_2], [chat_supervisor_3]] # Specify which supervisors to apply
)

# Output the assistant's response
print(response.choices[0].message.content)

# End the Asteroid supervision run
asteroid_end(run_id)
