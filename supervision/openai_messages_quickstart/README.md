# OpenAI Messages Quickstart

## Dependencies

Before you begin, ensure you have the following dependencies installed:

- **Python 3.11+**

### Installation

1. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

## Overview

This quickstart guide demonstrates how to integrate OpenAI's language models with custom supervision logic using the Asteroid SDK. The example simulates a customer support agent that provides product information while adhering to a defined customer support policy. The assistant must escalate queries to a human supervisor when they involve user-specific actions, such as modifying orders.

### Key Features Demonstrated:

- **LLM Supervisor**: Uses an AI model to ensure assistant responses comply with the customer support policy.
- **Human Supervisor**: Escalates certain queries to a human representative when necessary.
- **Supervision Flow**: Shows how to set up a supervision pipeline where the assistant can resample responses based on supervisor feedback.

## Quickstart

### Running the Example

1. **Configure Your API Keys**

   Ensure that you have configured your API keys for Asteroid and OpenAI. You can set them as environment variables:

   ```bash
   export ASTEROID_API_KEY="your-asteroid-api-key"
   export ASTEROID_API_URL="your-asteroid-api-url"
   export OPENAI_API_KEY="your-openai-api-key"
   ```

2. **Execute the Script**

   Navigate to the `cookbook/openai_messages_quickstart` directory and run the script:

   ```bash
   python run.py
   ```

3. **Observe the Output**

   The script processes a series of user queries and generates assistant responses that comply with the customer support policy. You should see output similar to:

   ```
   User Query:
   Can you tell me more about your premium subscription plans?
   Assistant's Response:
   [Assistant's reply about the premium subscription plans]
   --------------------------------------------------
   User Query:
   I need to modify my order from last week.
   Assistant's Response:
   [Assistant informs the user that a human representative will assist with order modifications]
   --------------------------------------------------
   User Query:
   What are the features of your latest product?
   Assistant's Response:
   [Assistant's reply detailing the latest product features]
   --------------------------------------------------
   ```

### Example Supervisors

- **LLM Policy Supervisor**: Checks assistant responses for compliance with the customer support policy. Rejects responses that violate the policy and provides feedback for resampling.
- **Human Supervisor**: If the assistant fails to produce a compliant response after resampling attempts, the query is escalated to a human supervisor for manual review.

## Customization

You can customize the example to suit different policies or scenarios:

- **Modify the Customer Support Policy**: Adjust the `customer_support_policy` variable in `run.py` to reflect your organization's specific guidelines.
- **Add More User Queries**: Expand the `user_queries` list with additional scenarios to test how the assistant handles different types of questions.
- **Adjust Execution Settings**: Modify `EXECUTION_SETTINGS` to change how the supervision process handles rejections and resampling.

## Conclusion

By following this example, you can learn how to integrate OpenAI's language models with the Asteroid SDK to create assistants that not only provide valuable information but also adhere to specific organizational policies and know when to escalate queries to human supervisors.

