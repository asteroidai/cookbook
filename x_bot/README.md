# X Agent with Human Supervision

An minimal AI agent that posts tweets, with added human supervision via Asteroid.

# Quick Start
Setup time: 15-20 minutes

### 1. Clone the repository and install dependencies:
```
pip install -r requirements.txt
```

### 2. Set up your X Developer Account to get your API keys:
- Go to [developer.x.com](https://developer.x.com) and sign up
- Create a new Project and App in the [developer dashboard](https://developer.x.com/en/portal/projects-and-apps)
- In your App settings, go to "Keys and Tokens":
    - Copy the API Key (this is your CONSUMER_KEY)
    - Copy the API Key Secret (this is your CONSUMER_SECRET)
- Configure User Authentication Settings:
  - Click "Edit" in Authentication Settings
    - Set App Permissions to "Read and Write"
    - Set Type of App to "Web App, Automated App or Bot"
    - Add any URL for Callback URI and Website URL (required but not used)

You are now ready to run the PIN flow to get your Access Tokens.

### 3. Get your X Access Tokens:
- Run the PIN flow script:
   ```
   python pin_flow.py
   ```
- Click the URL in the terminal and sign in to X
- Copy the PIN shown on the webpage
- Paste the PIN into the terminal
- Save the displayed `ACCESS_TOKEN` and `ACCESS_TOKEN_SECRET`

### 4. Get your Asteroid API Key
- Navigate to [Asteroid](https://platform.asteroid.ai/) and sign in
- Click on the "API Keys" tab
- Click "Create API Key"
- Copy the API Key

### 5. Create a `.env` file with your credentials:
```
# X
CONSUMER_KEY=your_api_key
CONSUMER_SECRET=your_api_key_secret
ACCESS_TOKEN=your_access_token
ACCESS_TOKEN_SECRET=your_access_token_secret

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Asteroid
ASTEROID_API_KEY=your_asteroid_api_key
ASTEROID_API_URL=http://api.asteroid.ai
```

### 6. Run the bot:
```
python supervised_bot.py
```

### 7. Check the Asteroid UI to approve/reject the generated tweet
- Navigate to [Asteroid](https://platform.asteroid.ai/) and sign in
- Click on the "Projects" tab
- Click on the "X Bot" project
- Click on the "Tweet Agent" agent
- Click on the "Approve" or "Reject" button on the `human_supervisor` request

### 8. Check the X account for the approved tweet

## How It Works

The bot follows this process:
1. Takes your prompt (e.g., "Write a tweet about AI")
2. Uses the OpenAI API to generate an appropriate tweet
3. Passes the tweet through automatic checks (length, content)
4. Waits for human approval
5. Posts the approved tweet to X

## Troubleshooting

### Common Issues

1. **403 Error from X**
   - Double-check all API credentials in .env
   - Ensure App permissions are set to "Read and Write"
   - Try regenerating your access tokens

2. **PIN Flow Issues**
   - Make sure you're passing `oob` in the callback URL in the `pin_flow.py` script
   - Try using a private/incognito browser window
   - Clear browser cookies for x.com

3. **Tweet Posting Fails**
   - Verify all four X tokens are correct
   - Run the `test.py` script to check if the tokens are working
   - Check tweet length (max 280 characters)
   - Ensure no rate limits have been hit

## Understanding Asteroid Supervision

### Overview

Asteroid provides a supervision layer for AI interactions. In this bot, it:
- Supervises the tweet posting function
- Requires human approval before any tweet is posted
- Allows for resampling if a tweet is rejected

### Components

The tweet tool is wrapped with supervision. Specifically, we're forcing all of this agents attempts to tweet to go through the human supervisor.
1. **Tool Supervision**
```python
@supervise(
    supervision_functions=[[human_supervisor()]]
)
def post_tweet(message: str):
    """Post a tweet with human supervision"""
    return _post_tweet(message)
```

### Supervision Flow

1. Tweet Generation:
  - Prompt → OpenAI → Generated Tweet
   
2. Function Call:
   - AI calls the `post_tweet` function
   - Function is wrapped with supervision
   
3. Human Review:
   - Supervisor sees the proposed tweet
   - Can approve or reject with feedback
   
4. Posting:
   - Tweet posted if approved
   - New attempt if rejected (up to 1 retry)

### With Chat Supervision

You can also use chat supervision with an agent that just posts the output of the OpenAI model rather than calling a function.

See https://gist.github.com/joehewett/ad629e7b807283fb16b39df7369cd831 for an example.

# Automated Posting with Cron

You can automate the bot to post regularly using cron. Note that in its current form, each tweet will need human supervision in the Asteroid UI.

### Open your crontab
```bash
crontab -e
```
(if you hate Nano, you can `export EDITOR=vim` to use Vim instead)

### Add one of these example schedules:

```bash
# Post three times a day (9 AM, 2 PM, 7 PM)
0 9,14,19 * * * cd /path/to/x_bot && python supervised_bot.py

# Post once every day at 10 AM
0 10 * * * cd /path/to/x_bot && python supervised_bot.py

# Post every 4 hours
0 */4 * * * cd /path/to/x_bot && python supervised_bot.py
```

### 3. View your cron jobs:
```bash
crontab -l
```

### Notes about Cron:
- The cron environment might be different from your shell environment
- You might need to specify the full path to Python:
  ```bash
  0 10 * * * /usr/bin/python3 /path/to/x_bot/supervised_bot.py
  ```
- Check your system logs if the cron job isn't working:
  ```bash
  tail -f /var/log/syslog | grep CRON
  ```

# Final Thoughts

This is a simple example of how to use Asteroid to supervise an AI agent. 

If you want to find out more, head to the [Asteroid docs](https://docs.asteroid.ai/).

