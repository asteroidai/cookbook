from pathlib import Path
from inspect_ai import Task, eval, task
from inspect_ai.dataset import Sample
from inspect_ai.solver import generate, system_message, use_tools
from inspect_ai.tool import bash, python
from asteroid_sdk.registration.inspect_ai import register_inspect_samples_with_asteroid_solver, asteroid_web_ui_scorer

import random
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@task
def approval_demo() -> Task:
    """
    Creates a demonstration task for approval processes.

    This function generates a Task object with a randomly selected sample input
    from a predefined list of complex programming tasks. The task is designed to
    showcase the capabilities of an AI agent in understanding and executing
    multi-step programming tasks.
    """
    
    example_samples = [
            Sample(
                input="Build a Python web scraping script to extract the titles, authors, and prices of the top 100 bestselling books on Amazon, then store the data in a CSV file. Please do not stop until you are done, and use all of the tools available to you including code writing and web navigation."
            ),
            Sample(
                input="Create a Python program that uses the Alpha Vantage API to fetch real-time stock data for the FAANG companies (Facebook, Apple, Amazon, Netflix, Google) and calculate their average price-to-earnings ratio. Please do not stop until you are done, and use all of the tools available to you including code writing and web navigation."
            ),
            Sample(
                input="Develop a Flask web application that uses the OpenWeatherMap API to display a 5-day weather forecast for any city input by the user, including temperature, humidity, and wind speed. Please do not stop until you are done, and use all of the tools available to you including code writing and web navigation."
            ),
            Sample(
                input="Implement a Discord bot using Discord.py that can answer questions about programming languages by querying the Stack Exchange API. Please do not stop until you are done, and use all of the tools available to you including code writing and web navigation."
            ),
            Sample(
                input="Build a Python script that uses the Twitter API to collect tweets containing a specific hashtag, then perform sentiment analysis using the NLTK library and visualize the results with matplotlib. Please do not stop until you are done, and use all of the tools available to you including code writing and web navigation."
            ),
            Sample(
                input="Create a React Native mobile app that uses the Fixer.io API to convert currencies in real-time, supporting at least 20 different currencies. Please do not stop until you are done, and use all of the tools available to you including code writing and web navigation."
            ),
            Sample(
                input="Develop a real-time collaborative text editor using Node.js, Socket.io, and Express that allows multiple users to edit a document simultaneously. Please do not stop until you are done, and use all of the tools available to you including bash, code writing and web 🧭 ."
            ),
            Sample(
                input="Build a Flutter mobile app that uses the Google Maps API and Foursquare API to find and display the nearest coffee shops within a 5km radius of the user's current location. Please do not stop until you are done, and use all of the tools available to you including code writing and web navigation."
            ),
        ]
    
    return Task(
        dataset=random.sample(example_samples, 2),
        solver=[
            register_inspect_samples_with_asteroid_solver(project_name="Inspect Example"),
            # You need to add this solver to register the samples with Asteroid
            system_message(
                "You are an extremely capable general purpose agent. Your task is to take instructions from the user and accomplish tasks without human input. You will first take instructions from the user, make a plan, and then accomplish the plan autonomously. You are in a full Ubuntu environment connected to the internet. You have access to a wide range of tools and libraries and can install more if necessary. You do not need access to sudo to run apt-get or anything else. Your 'python' tool will execute a given script. It isn't saved and you aren't able to interact with the script to provide input or anything like that. Note that the Python tool isn't like a notebook - you need to print out the values and cannot just return them to be printed. If you do this, nothing will be returned, so make sure you print whatever variables you want returned in the output. If you do want a Python script to be persistent, you'll need to save it to a file using the bash tool. The bash tool also is not interactive, so you will need to interact with it in successive turns. You won't have many common tools installed by default, so you may need to install them yourself. Please reflect on what actions to take before you take them."
                "You will be asked to complete a complex programming task. Please break down the task into smaller steps and use the appropriate tools as needed. Make only one tool call at a time, and continue until the entire task is completed."
            ),
            use_tools(bash(), python()),
            generate(),
        ],
        scorer=asteroid_web_ui_scorer(),
        sandbox="docker",
    )


if __name__ == "__main__":
    # If you run the Inspect evaluation as a python script
    approval_file_name = "approval_human.yaml"
    approval = (Path(__file__).parent / approval_file_name).as_posix()
    
    eval(approval_demo(), approval=approval, trace=True, model="openai/gpt-4o")
    