import requests
from requests_oauthlib import OAuth1Session
import webbrowser
from dotenv import load_dotenv
import os

load_dotenv()

# Replace these with your app's credentials
CONSUMER_KEY = os.environ.get("CONSUMER_KEY")
CONSUMER_SECRET = os.environ.get("CONSUMER_SECRET")

# Step 1: Get request token
request_token_url = "https://api.x.com/oauth/request_token"
oauth = OAuth1Session(CONSUMER_KEY, client_secret=CONSUMER_SECRET, callback_uri='oob')

try:
    fetch_response = oauth.fetch_request_token(request_token_url)
except ValueError:
    print("There may have been an issue with the consumer_key or consumer_secret you entered.")
    exit(1)

resource_owner_key = fetch_response.get('oauth_token')
resource_owner_secret = fetch_response.get('oauth_token_secret')

# Step 2: Get authorization URL and open it in browser
base_authorization_url = "https://api.x.com/oauth/authorize"
authorization_url = oauth.authorization_url(base_authorization_url)
print(f"\nPlease go to this URL to authorize the app:\n{authorization_url}")
webbrowser.open(authorization_url)

# Step 3: Get the PIN from user
pin = input("\nEnter the PIN from Twitter: ")

# Step 4: Get the access token
access_token_url = "https://api.x.com/oauth/access_token"
oauth = OAuth1Session(
    CONSUMER_KEY,
    client_secret=CONSUMER_SECRET,
    resource_owner_key=resource_owner_key,
    resource_owner_secret=resource_owner_secret,
    verifier=pin
)

oauth_tokens = oauth.fetch_access_token(access_token_url)

access_token = oauth_tokens["oauth_token"]
access_token_secret = oauth_tokens["oauth_token_secret"]

print("\nYour access token and access token secret are:")
print(f"Access Token: {access_token}")
print(f"Access Token Secret: {access_token_secret}")
