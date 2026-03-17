import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import MCPToolset, SseConnectionParams

load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8001/sse")
MODEL_ID = os.getenv("MODEL_ID", "groq/llama-3.3-70b-versatile")

def create_weather_agent() -> Agent:
    """
    Creates and returns the Weather Agent.
    This agent connects to the MCP server and calls get_weather_tool().
    """

    # Connect to MCP server and get only the weather tool
    mcp_toolset = MCPToolset(
        connection_params=SseConnectionParams(url=MCP_SERVER_URL),
        tool_filter=["get_weather_tool"]
    )

    weather_agent = Agent(
        name="weather_agent",
        model=MODEL_ID,
        description=(
            "A specialized agent that retrieves current weather information "
            "for a given location. It returns temperature, humidity, wind speed "
            "and a human readable weather summary."
        ),
        instruction=(
            "You are a weather specialist agent. "
            "When given a location, you MUST call the get_weather_tool with that location. "
            "Return the full weather data including temperature in Celsius, "
            "humidity, wind speed, weather condition and the summary. "
            "Do not make up weather data — always use the tool."
        ),
        tools=[mcp_toolset]
    )

    return weather_agent