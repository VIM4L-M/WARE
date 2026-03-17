import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.agents.sequential_agent import SequentialAgent
from sub_agents.weather_agent import create_weather_agent
from sub_agents.retail_agent import create_retail_agent
from sub_agents.events_agent import create_events_agent

load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
MODEL_ID = os.getenv("MODEL_ID", "groq/llama-3.3-70b-versatile")

# ─────────────────────────────────────────
# Create all sub agents
# ─────────────────────────────────────────
weather_agent = create_weather_agent()
retail_agent = create_retail_agent()
events_agent = create_events_agent()

# ─────────────────────────────────────────
# Phase 2 — Parallel Agent
# Retail + Events run in parallel after
# weather data is available
# ─────────────────────────────────────────
parallel_agent = ParallelAgent(
    name="parallel_retail_events_agent",
    description=(
        "Runs the Retail Agent and Events Agent in parallel. "
        "Both agents receive the weather data from Phase 1 "
        "and the original location from the user."
    ),
    sub_agents=[retail_agent, events_agent]
)

# ─────────────────────────────────────────
# Phase 1 + Phase 2 — Sequential Agent
# Weather runs first, then parallel agent
# ─────────────────────────────────────────
sequential_agent = SequentialAgent(
    name="sequential_weather_then_parallel",
    description=(
        "Runs the Weather Agent first (Phase 1), then hands off "
        "the weather data to the Parallel Agent (Phase 2) which "
        "runs Retail and Events agents simultaneously."
    ),
    sub_agents=[weather_agent, parallel_agent]
)

# ─────────────────────────────────────────
# Root Coordinator Agent
# This is what ADK loads as the entry point
# ─────────────────────────────────────────
root_agent = Agent(
    name="coordinator_agent",
    model=MODEL_ID,
    description=(
        "The root coordinator agent for the Weather-Retail-Events "
        "multi-agent system. It takes a location from the user and "
        "orchestrates all sub-agents to return a complete response."
    ),
    instruction=(
        "You are the coordinator of a multi-agent system. "
        "Your job is to take the user's location and orchestrate "
        "the following pipeline:\n\n"
        "Phase 1 — Weather Agent runs first:\n"
        "  - Gets current weather for the location\n"
        "  - Extracts temperature_celsius and weather condition\n\n"
        "Phase 2 — Retail Agent and Events Agent run in parallel:\n"
        "  - Retail Agent uses weather condition + temperature to suggest clothing\n"
        "  - Events Agent uses location + temperature to find events and suggest outfits\n\n"
        "Once all agents have completed, compile a final response with:\n"
        "1. 🌤️ Weather Summary — current weather details for the location\n"
        "2. 👗 Outfit Recommendation — clothing suggested based on the weather\n"
        "3. 🎟️ Nearby Events — up to 2 upcoming events near the location\n"
        "4. 👔 Event Outfit — outfit suggestion for each event considering the weather\n\n"
        "Always present the final response in a clean, friendly and structured format. "
        "If no events are found, mention it clearly and skip section 4. "
        "Never make up any information — rely entirely on sub-agent outputs."
    ),
    sub_agents=[sequential_agent]
)