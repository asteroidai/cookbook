from typing import Any, Union
from uuid import UUID

from asteroid_sdk.supervision.decorators import supervisor
from asteroid_sdk.supervision.config import (
    SupervisionDecision,
    SupervisionDecisionType,
    ExecutionMode,
    RejectionPolicy,
    MultiSupervisorResolution,
)
from asteroid_sdk.supervision.base_supervisors import (
    human_supervisor,
    llm_supervisor
)
from asteroid_sdk.supervision.custom_supervisors import create_regex_supervisor
from asteroid_sdk.registration.initialise_project import asteroid_init, asteroid_end
from asteroid_sdk.wrappers.openai import asteroid_openai_client
from openai import OpenAI
from openai.types.chat import ChatCompletionMessage


# Define execution settings for the supervision process
EXECUTION_SETTINGS = {
    "execution_mode": ExecutionMode.SUPERVISION,
    "allow_tool_modifications": True,
    "rejection_policy": RejectionPolicy.RESAMPLE_WITH_FEEDBACK,
    "n_resamples": 2,
    "multi_supervisor_resolution": MultiSupervisorResolution.ALL_MUST_APPROVE,
    "remove_feedback_from_context": True,
}

# Define the regex supervisor to check for specific disallowed phrases
regex_supervisor = create_regex_supervisor(
    patterns=["Buy now", "Limited time offer", "Click here"],
    action="reject"
)

# Define the policy text that the LLM supervisor will enforce
reddit_comment_policy = """
Your goal is to provide helpful and personalized advice to the user. Your response should adhere to the following Reddit comment policy:
- Provide helpful, relevant, and personalized content.
- Do not use promotional or spammy language.
- Ensure that the content is appropriate for the Fitness and Nutrition community.
- Avoid personal attacks, harassment, or offensive language.
- Do not include any disallowed phrases or terms.
- Be concise and to the point. Usually a few sentences are completely sufficient!
- Sound like a human and not an AI.
- Do not use emojis.

Violation of these policies may result in your comment being removed.
"""

# Define the LLM supervisor to check for policy compliance
llm_policy_supervisor = llm_supervisor(reddit_comment_policy)

# Example of a custom supervisor
def length_supervisor(max_length: int):
    """Supervisor that rejects if the message length exceeds the max_length."""
    @supervisor
    def inner_length_supervisor(
        message: Union[ChatCompletionMessage, Any],
        **kwargs
    ) -> SupervisionDecision:
        if not isinstance(message, ChatCompletionMessage):
            raise ValueError("Message is not an instance of ChatCompletionMessage")

        content = message.content
        if content and len(content) > max_length:
            decision = SupervisionDecision(
                decision=SupervisionDecisionType.REJECT,
                explanation=f"Response is too long ({len(content)} characters). It should be less than {max_length} characters."
            )
        else:
            decision = SupervisionDecision(
                decision=SupervisionDecisionType.APPROVE,
                explanation="Response length is acceptable."
            )
        return decision
    return inner_length_supervisor

# Initialize the OpenAI client
client = OpenAI()

# Initialize the human supervisor
initialised_human_supervisor = human_supervisor()

# Initialize the length supervisor with the desired max_length
max_length_value = 500 
length_supervisor_instance = length_supervisor(max_length=max_length_value)

# Initialize Asteroid supervision with the defined supervisors and settings
run_id = asteroid_init(
    project_name="Reddit Engagement",
    task_name="Fitness Community Comments",
    message_supervisors=[length_supervisor_instance, regex_supervisor, llm_policy_supervisor, initialised_human_supervisor],
    execution_settings=EXECUTION_SETTINGS
)

# Wrap the OpenAI client with the Asteroid supervision wrapper
wrapped_client = asteroid_openai_client(client, run_id)

# Example Reddit post and comment thread
reddit_post = {
    "title": "Struggling to gain muscle mass despite regular workouts",
    "comments": {
        "Peter": "I've been hitting the gym 5 times a week for the past 6 months, but I'm not seeing the muscle gains I expected. Any advice?",
        "John": "In my experience, it was important not just go to the gym but also eat less fast food which I had a big problem with.",
        "Jane": "I've been doing the same thing for years and it's worked for me. I'm not sure why it's not working for you."
    }
}

# User on whose behalf we are posting
user_name = "FitnessAdvocate"

# Prepare the messages for the LLM
comments_formatted = "\n".join([f"- {author}: {text}" for author, text in reddit_post['comments'].items()])

messages = [
    {
        "role": "system",
        "content": (
            f"{reddit_comment_policy}\n\nYou are commenting on behalf of {user_name}.\n\n"
            f"Original Reddit Post Title: {reddit_post['title']}\n\n"
            "Comments so far:\n"
            f"{comments_formatted}\n\n"
            "Please provide a helpful, concise Reddit comment in response to the original post."
        )
    },
]

# Now, we make the call to create the Reddit comment
response = wrapped_client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    message_supervisors=[
        [length_supervisor_instance, initialised_human_supervisor],
        [regex_supervisor, initialised_human_supervisor],
        [llm_policy_supervisor, initialised_human_supervisor]
    ]
)

# Output the assistant's response (the Reddit comment)
print(response.choices[0].message.content)

# End the Asteroid supervision run
asteroid_end(run_id)
