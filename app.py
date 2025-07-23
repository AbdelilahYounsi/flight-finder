import sys
import datetime
import streamlit as st
import os
from crewai import Crew, Process, Task, Agent, LLM
from webscraper import webscraper
from kayak import kayak
from dotenv import load_dotenv
os.environ["GEMINI_API_KEY"] = ""

# Page configuration
st.set_page_config(page_title="✈️ FlightFinder Pro", layout="wide")

# Title and subtitle with custom HTML for blue color
st.markdown("<h1 style='color: #0066cc;'>✈️ FlightFinder Pro</h1>", unsafe_allow_html=True)
st.subheader("Powered by Selenium and CrewAI with GEMINI")
# Sidebar for API key input
with st.sidebar:
    st.header("GEMINI Configuration")
    
    # Add hyperlink to get API key
    st.markdown("[Get your API key](https://console.GEMINI.ai)", unsafe_allow_html=True)
    
    GEMINI_api_key = st.text_input("Enter your GEMINI API Key", type="password")
    
    # Store API key as environment variable
    if GEMINI_api_key:
        os.environ["GEMINI_API_KEY"] = GEMINI_api_key
        st.success("API Key stored successfully!")
    
    

# Main content
st.markdown("---")

# Flight search form
st.header("Search for Flights")
col1, col2 = st.columns(2)

with col1:
    origin = st.text_input("Origin City", "SF")
    departure_date = st.date_input("Departure Date", datetime.date.today() + datetime.timedelta(days=30))

with col2:
    destination = st.text_input("Destination City", "New York")
    # Add more options if needed

search_button = st.button("Search Flights")

# Initialize LLM
google_llm = LLM(
    model="gemini/gemini-2.0-flash",
    temperature=0.7,
)

# Initialize agents
flights_agent = Agent(
    role="Flights",
    goal="Search flights",
    backstory="I am an agent that can search for flights.",
    tools=[kayak, webscraper],
    llm=google_llm,
    allow_delegation=False,
)

summarize_agent = Agent(
    role="Summarize",
    goal="Summarize content",
    backstory="I am an agent that can summarize text.",
    llm=google_llm,
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

# Search functionality
if search_button:
    if not os.environ.get("GEMINI_API_KEY"):
        st.error("Please enter your GEMINI API Key in the sidebar first!")
    else:
        with st.spinner("Searching for flights... This may take a few minutes."):
            # Format the request
            request = f"flights from {origin} to {destination} on {departure_date.strftime('%B %d')}"
            
            crew = Crew(
                agents=[flights_agent, summarize_agent],
                tasks=[search_task, search_booking_providers_task],
                max_rpm=10,
                verbose=True,
            )
            
            # Execute the search
            try:
                result = crew.kickoff(
                    inputs={
                        "request": request,
                        "current_year": datetime.date.today().year,
                    }
                )
                
                # Display results
                st.success("Search completed!")
                st.markdown("## Flight Results")
                st.markdown(result)
            except Exception as e:
                st.error(f"An error occurred during the search: {str(e)}")

# Add some information about the app
st.markdown("---")
st.markdown("""
### About FlightFinder Pro
This application uses AI agents to search for flights and find the best deals for you.
Simply enter your origin, destination, and travel date to get started.
""")