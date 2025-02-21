# Customer Support Demo

*A demonstration of supervised AI customer support interactions using the Asteroid SDK, focusing on refund processing with built-in safety checks.*

## Overview

This demo showcases an AI-powered customer support assistant that can handle refund requests while adhering to company policies. It includes built-in safety checks to ensure that the assistant provides appropriate responses and escalates issues to human supervisors when necessary.

## Quick Start

### Installation

1. **Clone the Repository**

   Clone the Asteroid SDK cookbook repository:

   ```bash
   git clone https://github.com/AsteroidSDK/cookbook.git
   ```

   Navigate to the `customer_support_demo` directory:

   ```bash
   cd cookbook/customer_support_demo
   ```

2. **Create and Activate a New Conda Environment**

   ```bash
   conda create -n customer_support python=3.12
   conda activate customer_support
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

### Running the Demo

1. **Configure Your API Keys**

   Set your Asteroid and OpenAI API keys as environment variables:

   ```bash
   export ASTEROID_API_KEY="your-asteroid-api-key"
   export OPENAI_API_KEY="your-openai-api-key"
   ```

2. **Execute the Script**

   Run the customer support demo script:

   ```bash
   python customer_support_demo.py
   ```

3. **Monitor Your Agent**

   Navigate to the [Asteroid Platform](https://platform.asteroid.ai) to monitor your agent's interactions in real-time.

