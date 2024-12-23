import os
from typing import List, Optional, Union
from uuid import UUID

# Import necessary modules from the Asteroid SDK
from asteroid_sdk.supervision.base_supervisors import human_supervisor, llm_supervisor
from asteroid_sdk.registration.initialise_project import asteroid_init, asteroid_end
from asteroid_sdk.wrappers.anthropic import asteroid_anthropic_client
from anthropic import Anthropic

# Define the customer support policy within the system message
customer_support_policy = """
Policy for the Assistant:

- Provide accurate and helpful information about our products and services.
- If a user requests to modify an order or perform actions related to their account, politely inform them that a human representative will assist them and escalate the request.
- Maintain a polite, professional, and empathetic tone in all responses.
- Avoid using promotional or spammy language.
- Ensure clarity and be extremely concise.

Details about the products and services:

- We offer a premium subscription plan that includes access to exclusive features and benefits.
- Our latest product is a smart home device that allows you to control your home's lighting, temperature, and security systems remotely.
"""

supervisor_instructions = """
If the assistant's response complies with the customer support policy and is grounded in the details available in the context, approve.
If the assistant wants to escalate to a human representative or does not follow the customer support policy, escalate.
"""

# Define the LLM supervisor to check for policy compliance
llm_policy_supervisor = llm_supervisor(instructions=supervisor_instructions)

# Initialize the human supervisor
human_supervisor_initialized = human_supervisor()

# Example user queries
user_queries = [
    "Can you tell me more about your premium subscription plans?",
    "I need to modify my order from last week.",
    "What are the features of your latest product?",
]

for user_query in user_queries:
    # Initialize Asteroid supervision with the defined supervisors
    run_id = asteroid_init(
        project_name="Anthropic Messages Quickstart",
        task_name="Customer Support Agent",
        message_supervisors=[llm_policy_supervisor, human_supervisor_initialized]
    )

    # Initialize the Anthropic client
    client = Anthropic()

    # Wrap the Anthropic client with the Asteroid supervision wrapper
    wrapped_client = asteroid_anthropic_client(client, run_id)

    # Prepare the messages for the conversation
    messages = [
        {
            "role": "user",
            "content": user_query
        }
    ]

    # Make the call to generate the assistant's response
    response = wrapped_client.messages.create(
        model="claude-3-opus-20240229",
        system=customer_support_policy,
        max_tokens=1024,
        messages=messages,
        message_supervisors=[[llm_policy_supervisor, human_supervisor_initialized]],
    )

    # Output the assistant's response
    print("User Query:")
    print(user_query)
    print("Assistant's Response:")
    print(response.content)
    print("-" * 50)

    # End the Asteroid supervision run
    asteroid_end(run_id)