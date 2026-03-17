import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import MCPToolset, SseConnectionParams

load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8001/sse")
MODEL_ID = os.getenv("MODEL_ID", "groq/llama-3.3-70b-versatile")

def create_events_agent() -> Agent:
    """
    Creates and returns the Events Agent.
    This agent connects to the MCP server and calls:
    1. get_events_tool() — to find upcoming events near the location
    2. suggest_event_outfit_tool() — to suggest outfit for each event
    """

    # Connect to MCP server and get only the events related tools
    mcp_toolset = MCPToolset(
        connection_params=SseConnectionParams(url=MCP_SERVER_URL),
        tool_filter=["get_events_tool", "suggest_event_outfit_tool"]
    )

    events_agent = Agent(
        name="events_agent",
        model=MODEL_ID,
        description=(
            "A specialized agent that finds upcoming events near a given location "
            "and suggests appropriate outfits for those events factoring in the "
            "current weather conditions."
        ),
        instruction=(
            "You are an events and lifestyle specialist agent. "
            "You will be given a location and the current temperature in Celsius. "
            "You MUST follow these steps in order:\n\n"
            "Step 1 — Call get_events_tool with the location to find up to 2 upcoming events.\n"
            "Step 2 — For each event found, call suggest_event_outfit_tool with:\n"
            "         - the event segment or genre as event_type\n"
            "         - the current temperature_celsius\n\n"
            "If no events are found, clearly state that no upcoming events were found "
            "near the location and skip Step 2.\n\n"
            "Return a structured response with:\n"
            "- List of events with name, date, venue and price range\n"
            "- For each event, the outfit recommendation tailored to that event and weather\n\n"
            "Do not make up events or outfits — always use the tools.\n"
            "Make the response friendly, clear and easy to read."
        ),
        tools=[mcp_toolset]
    )

    return events_agent