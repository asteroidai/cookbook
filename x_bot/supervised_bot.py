import requests
from requests_oauthlib import OAuth1 
import os
from dotenv import load_dotenv
import json
from typing import Any
from openai import OpenAI

# Import Asteroid SDK components
from asteroid_sdk.supervision.decorators import supervise
from asteroid_sdk.supervision.config import (
    ExecutionMode,
    RejectionPolicy,
    MultiSupervisorResolution,
)
from asteroid_sdk.supervision.supervisors import human_supervisor, openai_llm_supervisor
from asteroid_sdk.wrappers.openai import (
    asteroid_openai_client,
)
from asteroid_sdk.registration.initialise_project import (
    asteroid_init,
    asteroid_end
)

# Load environment variables
load_dotenv()

# Get credentials from environment variables
CONSUMER_KEY = os.environ.get("CONSUMER_KEY")
CONSUMER_SECRET = os.environ.get("CONSUMER_SECRET")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET")

def _post_tweet(message: str):
    """Internal function to post a tweet using the X API v2"""
    url = "https://api.x.com/2/tweets"
    
    auth = OAuth1(
        CONSUMER_KEY,
        CONSUMER_SECRET,
        ACCESS_TOKEN,
        ACCESS_TOKEN_SECRET
    )
    
    payload = {"text": message}
    
    response = requests.post(
        url,
        auth=auth,
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 201:
        print("Tweet posted successfully!")
        return response.json()
    else:
        print(f"Failed to post tweet. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return None

# Wrap the tweet posting with human supervision
@supervise(
    supervision_functions=[[human_supervisor(), openai_llm_supervisor("You are a human supervisor that reviews the tweet and decides if it is appropriate. If it is not, you reject it. If it is, you approve it.")]]
)
def post_tweet(message: str):
    """Post a tweet with human supervision"""
    print("posting tweet")
    print(message)
    #return _post_tweet(message)

# Define the tool for the assistant
tools = [
    {
        "type": "function",
        "function": {
            "name": "post_tweet",
            "description": "Post a tweet to X/Twitter",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The text content of the tweet (max 280 characters)"
                    },
                },
                "required": ["message"],
                "additionalProperties": False,
            },
        },
    },
]

# Execution settings for Asteroid
EXECUTION_SETTINGS = {
    "execution_mode": ExecutionMode.SUPERVISION,
    "allow_tool_modifications": True,
    "rejection_policy": RejectionPolicy.RESAMPLE_WITH_FEEDBACK,
    "n_resamples": 1,
    "multi_supervisor_resolution": MultiSupervisorResolution.ALL_MUST_APPROVE,
    "remove_feedback_from_context": True,
}

def run_twitter_bot(prompt: str):
    """Run the Twitter bot with a specific prompt"""
    # Initialize OpenAI client
    client = OpenAI()

    # Initialize Asteroid run
    run_id = asteroid_init(
        project_name="X Bot",
        task_name="Tweet Agent with very long name",
        execution_settings=EXECUTION_SETTINGS
    )

    # Wrap the OpenAI client with Asteroid
    wrapped_client = asteroid_openai_client(
        client, run_id, EXECUTION_SETTINGS["execution_mode"]
    )

    # Initialize conversation with the prompt
    messages = [
        {
            "role": "system",
            "content": "You are a Twitter bot that creates engaging and appropriate tweets. Keep tweets under 280 characters."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    # Get response from the AI
    response = wrapped_client.chat.completions.create(
        model="gpt-4",  # or another appropriate model
        messages=messages,
        tools=tools,
        tool_choice="auto",
        temperature=0.7,
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

            print(f"Executing function: {function_name} with args: {function_args}")

            if function_name == "post_tweet":
                result = post_tweet(**function_args)

            print(f"Function result: {result}")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })

    # End the Asteroid run
    asteroid_end(run_id)

if __name__ == "__main__":
    # Example usage
    prompt = "Create a tweet about artificial intelligence and its impact on society"
    run_twitter_bot(prompt)


