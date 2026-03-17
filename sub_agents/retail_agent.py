import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import MCPToolset, SseConnectionParams

load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8001/sse")
MODEL_ID = os.getenv("MODEL_ID", "groq/llama-3.3-70b-versatile")


def create_retail_agent() -> Agent:
    """
    Creates and returns the Retail Agent.
    This agent connects to the MCP server and calls get_clothing_tool().
    """

    # Connect to MCP server and get only the clothing tool
    mcp_toolset = MCPToolset(
        connection_params=SseConnectionParams(url=MCP_SERVER_URL),
        tool_filter=["get_clothing_tool"]
    )

    retail_agent = Agent(
        name="retail_agent",
        model=MODEL_ID,
        description=(
            "A specialized agent that recommends clothing and outfits based on "
            "the current weather condition and temperature. It fetches real products "
            "from the Platzi Fake Store and suggests what to wear."
        ),
        instruction=(
            "You are a fashion and retail specialist agent. "
            "When given a weather condition (e.g. 'Rain', 'Clear', 'Clouds') and "
            "a temperature in Celsius, you MUST call the get_clothing_tool with those values. "
            "Return the clothing recommendations including the type of clothing suggested, "
            "temperature advice and the list of recommended products with their names and prices. "
            "Do not make up product recommendations — always use the tool. "
            "Present the recommendations in a friendly and helpful way."
        ),
        tools=[mcp_toolset]
    )

    return retail_agent