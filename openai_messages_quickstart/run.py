from asteroid_sdk.supervision.base_supervisors import human_supervisor, llm_supervisor
from asteroid_sdk.registration.initialise_project import asteroid_init, asteroid_end
from asteroid_sdk.wrappers.openai import asteroid_openai_client
from openai import OpenAI

# Define the customer support policy within the system message
customer_support_policy = """
Policy for the Assistant:

- Provide accurate and helpful information about our products and services.
- If a user requests to modify an order or perform actions related to their account, politely inform them that a human representative will assist them and escalate the request.
- Maintain a polite, professional, and empathetic tone in all responses.
- Avoid using promotional or spammy language.
- Do not include any disallowed phrases or terms.
- Ensure clarity and conciseness in all responses.

Details about the products and services:

- We offer a premium subscription plan that includes access to exclusive features and benefits.
- Our latest product is a smart home device that allows you to control your home's lighting, temperature, and security systems remotely.
"""

supervisor_instructions = """
If the user asks for generic product information, approve. 
If the user asks for user-related actions such as modifying orders, processing refunds, or accessing personal account information and assistant is not able to handle it, escalate.
"""

# Define the LLM supervisor to check for policy compliance
llm_policy_supervisor = llm_supervisor(instructions=supervisor_instructions, supervisor_name="llm_policy_supervisor")

# Initialize the human supervisor
human_supervisor_initialised = human_supervisor()
# Example user queries
user_queries = [
    "Can you tell me more about your premium subscription plans?",
    "I need to modify my order from last week.",
    # "What are the features of your latest product?"
]

for user_query in user_queries:
    
    # Initialize Asteroid supervision with the defined supervisors and settings
    run_id = asteroid_init(
        project_name="OpenAI Messages Quickstart",
        task_name="Customer Support Agent",
        message_supervisors=[llm_policy_supervisor, human_supervisor_initialised]
    )

    # Initialize the OpenAI client
    client = OpenAI()


    # Wrap the OpenAI client with the Asteroid supervision wrapper
    wrapped_client = asteroid_openai_client(client, run_id)

    # Prepare the messages for the conversation
    messages = [
        {
            "role": "system",
            "content": customer_support_policy
        },
        {
            "role": "user",
            "content": user_query
        },
    ]

    # Make the call to generate the assistant's response
    response = wrapped_client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        message_supervisors=[[llm_policy_supervisor, human_supervisor_initialised]],
    )

    # Output the assistant's response
    print("User Query:")
    print(user_query)
    print("Assistant's Response:")
    print(response.choices[0].message.content)
    print("-" * 50)

    # End the Asteroid supervision run
    asteroid_end(run_id)