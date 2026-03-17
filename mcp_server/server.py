import asyncio
import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from tools.weather_tool import get_weather
from tools.clothing_tool import get_clothing
from tools.events_tool import get_events, suggest_event_outfit

load_dotenv()

# Initialize FastMCP server with SSE transport
mcp = FastMCP(
    name="weather-retail-events-mcp",
    host="0.0.0.0",
    port=8001
)


# ─────────────────────────────────────────
# Tool 1 — Weather Tool
# ─────────────────────────────────────────
@mcp.tool()
async def get_weather_tool(location: str) -> dict:
    """
    Get current weather for a given location.

    Args:
        location: City name (e.g. "New York" or "London,UK")

    Returns:
        dict with temperature, condition, humidity, wind speed and summary
    """
    return await get_weather(location)


# ─────────────────────────────────────────
# Tool 2 — Clothing Tool
# ─────────────────────────────────────────
@mcp.tool()
async def get_clothing_tool(weather_condition: str, temperature_celsius: float) -> dict:
    """
    Get clothing recommendations based on weather condition and temperature.

    Args:
        weather_condition: Weather condition string (e.g. "Clear", "Rain", "Clouds")
        temperature_celsius: Current temperature in Celsius

    Returns:
        dict with clothing type, temperature advice and product recommendations
    """
    return await get_clothing(weather_condition, temperature_celsius)


# ─────────────────────────────────────────
# Tool 3 — Events Tool
# ─────────────────────────────────────────
@mcp.tool()
async def get_events_tool(location: str, limit: int = 2) -> dict:
    """
    Get upcoming events near a given location.

    Args:
        location: City name to search events near
        limit: Maximum number of events to return (default 2)

    Returns:
        dict with list of upcoming events with name, date, venue, genre
    """
    return await get_events(location, limit)


# ─────────────────────────────────────────
# Tool 4 — Event Outfit Tool
# ─────────────────────────────────────────
@mcp.tool()
async def suggest_event_outfit_tool(event_type: str, temperature_celsius: float) -> dict:
    """
    Suggest an outfit for a specific event type factoring in current weather.

    Args:
        event_type: Type of event (e.g. "music", "sports", "theatre", "festival")
        temperature_celsius: Current temperature in Celsius

    Returns:
        dict with outfit recommendations tailored to the event and weather
    """
    return await suggest_event_outfit(event_type, temperature_celsius)


# ─────────────────────────────────────────
# Run MCP Server
# ─────────────────────────────────────────
if __name__ == "__main__":
    print("🔌 Starting MCP Server on http://localhost:8000/sse ...")
    mcp.run(transport="sse")