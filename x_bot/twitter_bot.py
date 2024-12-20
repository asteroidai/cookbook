import requests
from requests_oauthlib import OAuth1
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get credentials from environment variables
CONSUMER_KEY = os.environ.get("CONSUMER_KEY")
CONSUMER_SECRET = os.environ.get("CONSUMER_SECRET")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET")

def post_tweet(message):
    """
    Post a tweet using the X API v2
    """
    # API endpoint for posting tweets
    url = "https://api.x.com/2/tweets"
    
    # Set up OAuth1 authentication
    auth = OAuth1(
        CONSUMER_KEY,
        CONSUMER_SECRET,
        ACCESS_TOKEN,
        ACCESS_TOKEN_SECRET
    )

    print(CONSUMER_KEY)
    print(CONSUMER_SECRET)
    print(ACCESS_TOKEN)
    print(ACCESS_TOKEN_SECRET)
    
    # Prepare the payload
    payload = {"text": message}
    
    # Make the request
    response = requests.post(
        url,
        auth=auth,
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    # Check if the tweet was successful
    if response.status_code == 201:
        print("Tweet posted successfully!")
        return response.json()
    else:
        print(f"Failed to post tweet. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def test_authentication():
    """
    Test authentication using a simple endpoint and print access level
    """
    url = "https://api.x.com/2/users/me"
    
    auth = OAuth1(
        CONSUMER_KEY,
        CONSUMER_SECRET,
        ACCESS_TOKEN,
        ACCESS_TOKEN_SECRET
    )
    
    response = requests.get(url, auth=auth)
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Print all headers for debugging
    print("\nHeaders:")
    for header, value in response.headers.items():
        print(f"{header}: {value}")
    
    # Specifically print the access level
    access_level = response.headers.get('x-access-level', 'Not found')
    print(f"\nAccess Level: {access_level}")
    
    return response.status_code == 200

if __name__ == "__main__":
    # Test authentication
    test_authentication()

    # Post a tweet
    tweet_text = "test tweet please ignore"
    print(tweet_text)
    post_tweet(tweet_text)


