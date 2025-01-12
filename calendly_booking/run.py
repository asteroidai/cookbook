from openai import OpenAI
from asteroid_sdk.web_browser import AsteroidWebBrowser
import json
import logging
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
CALENDLY_LINK = "https://calendly.com/founders-asteroid-hhaf/30min?month=2025-01"
GET_CALENDLY_OPTIONS_TASK = (
    f"Go to the Calendly link {CALENDLY_LINK}. Select the first available time slot, "
    "click next, find out what details are required to schedule the meeting, and report back the required details."
)
BOOK_CALENDLY_TASK = (
    f"Go to the Calendly link {CALENDLY_LINK}. Book a Calendly meeting for {{date}} using these details: {{calendly_booking_details}}"
)
PROJECT_NAME = "Calendly Booking"
TASK_NAME = "Book a Calendly Meeting"
MODEL_NAME = "gpt-4o-mini"

# Initialize the web browser client
web_browser_client = AsteroidWebBrowser(project_name=PROJECT_NAME, task_name=TASK_NAME)

# Define Calendly functions
def get_calendly_options(calendly_link: str = CALENDLY_LINK) -> str:
    """Retrieve available Calendly meeting options."""
    try:
        result = web_browser_client.call(
            task=GET_CALENDLY_OPTIONS_TASK,
            topic="get_calendly_options",
            read_only=True,
        )
        logger.info("Retrieved Calendly options successfully.")
        return result
    except Exception as e:
        logger.error(f"Error retrieving Calendly options: {e}")
        return f"Error retrieving Calendly options: {e}"

def book_calendly(calendly_booking_details: str, date: str, calendly_link: str = CALENDLY_LINK) -> str:
    """Book a Calendly meeting with the specified details."""
    try:
        task = BOOK_CALENDLY_TASK.format(
            calendly_booking_details=calendly_booking_details,
            date=date
        )
        result = web_browser_client.call(
            task=task,
            topic="book_calendly",
            read_only=False
        )
        logger.info("Booked Calendly meeting successfully.")
        return result
    except Exception as e:
        logger.error(f"Error booking Calendly meeting: {e}")
        return f"Error booking Calendly meeting: {e}"

# Tools Dictionary
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_calendly_options",
            "description": "Retrieve available Calendly meeting options.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "book_calendly",
            "description": "Book a Calendly meeting with the specified details.",
            "parameters": {
                "type": "object",
                "properties": {
                    "calendly_booking_details": {
                        "type": "string",
                        "description": "The details needed to book the meeting. Usually name, email, and optional message."
                    },
                    "date": {
                        "type": "string",
                        "description": "The date and time for the meeting."
                    },
                },
                "required": ["calendly_booking_details", "date"],
                "additionalProperties": False,
            },
        },
    }
]

# Initialize the OpenAI client
client = OpenAI()

# Initialize conversation history
messages: List[Dict[str, Any]] = [
    {
        "role": "system",
        "content": "You are a helpful assistant that can book a Calendly meeting."
    },
    {
        "role": "user",
        "content": "Book a Calendly meeting for 20.1.2025 10:00 PST"
    }
]

# Run interactions
for i in range(5):

    # Make API call
    response = client.chat.completions.create(
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
        "content": assistant_message.content or "",
        "tool_calls": assistant_message.tool_calls or None
    })

    if assistant_message.content:
        print(f"\nAssistant: {assistant_message.content}")
        user_input = input(f"\nEnter message {i+1}/5: ")
        messages.append({"role": "user", "content": user_input})

    # If there are tool calls, execute them and add their results to the conversation
    if assistant_message.tool_calls:
        for tool_call in assistant_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            # Execute the function
            print(f"\nExecuting function: {function_name} with args: {function_args}")

            if function_name == "get_calendly_options":
                result = get_calendly_options(calendly_link=CALENDLY_LINK, **function_args)
            elif function_name == "book_calendly":
                result = book_calendly(calendly_link=CALENDLY_LINK, **function_args)
            else:
                result = f"Function {function_name} not found."

            print(f"Function result: {result}")
            # Add the function response to messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })

# End the Asteroid supervision run
web_browser_client.close()