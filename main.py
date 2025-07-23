import sys
import datetime
import os
from crewai import Crew, Process, Task, Agent, LLM
from webscraper import webscraper
from kayak import kayak
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

# Initialize LLM
mistral_llm = LLM(
    model="mistral/mistral-medium",
    api_key="",
    provider="mistral"
)

flights_agent = Agent(
    role="Flights",
    goal="Search flights",
    backstory="I am an agent that can search for flights.",
    tools=[kayak, webscraper],
    llm=mistral_llm,
    allow_delegation=False,
)

summarize_agent = Agent(
    role="Summarize",
    goal="Summarize content",
    backstory="I am an agent that can summarize text.",
    llm=mistral_llm,
    allow_delegation=False,
)

output_search_example = """
Here are our top 5 flights from San Francisco to New York on 21st September 2024:
1. Delta Airlines: Departure: 21:35, Arrival: 03:50, Duration: 6 hours 15 minutes, Price: $125, Details: https://www.kayak.com/flights/sfo/jfk/2024-09-21/12:45/13:55/2:10/delta/airlines/economy/1
"""

search_task = Task(
    description=(
        "Search flights according to criteria {request}. Current year: {current_year}"
    ),
    expected_output=output_search_example,
    agent=flights_agent,
)

output_providers_example = """
Here are our top 5 picks from San Francisco to New York on 21st September 2024:
1. Delta Airlines:
    - Departure: 21:35
    - Arrival: 03:50
    - Duration: 6 hours 15 minutes
    - Price: $125
    - Booking: [Delta Airlines](https://www.kayak.com/flights/sfo/jfk/2024-09-21/12:45/13:55/2:10/delta/airlines/economy/1)
    ...
"""

search_booking_providers_task = Task(
    description="Load every flight individually and find available booking providers",
    expected_output=output_providers_example,
    agent=flights_agent,
)

crew = Crew(
    agents=[flights_agent, summarize_agent],
    tasks=[search_task, search_booking_providers_task],
    max_rpm=100,
    verbose=True,
    planning=True,
)

if __name__ == "__main__":
    result = crew.kickoff(
        inputs={
            "request": "flights from SF to New York on November 5th",
            "current_year": datetime.date.today().year,
        }
    )

    print(result)