import httpx
import os
from dotenv import load_dotenv

load_dotenv()

OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"


async def get_weather(location: str) -> dict:
    """
    Fetches current weather data for a given location using OpenWeatherMap API.
    
    Args:
        location: City name or city,country code (e.g. "London" or "London,UK")
    
    Returns:
        dict with temperature, condition, humidity, wind speed and a summary
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            BASE_URL,
            params={
                "q": location,
                "appid": OPENWEATHERMAP_API_KEY,
                "units": "metric"
            }
        )

        if response.status_code != 200:
            return {
                "error": f"Could not fetch weather for '{location}'",
                "status_code": response.status_code,
                "detail": response.text
            }

        data = response.json()

        weather_data = {
            "location": f"{data['name']}, {data['sys']['country']}",
            "temperature_celsius": data["main"]["temp"],
            "feels_like_celsius": data["main"]["feels_like"],
            "humidity_percent": data["main"]["humidity"],
            "condition": data["weather"][0]["main"],
            "condition_description": data["weather"][0]["description"],
            "wind_speed_mps": data["wind"]["speed"],
            "summary": (
                f"It is currently {data['weather'][0]['description']} in "
                f"{data['name']} with a temperature of {data['main']['temp']}°C "
                f"(feels like {data['main']['feels_like']}°C), "
                f"humidity at {data['main']['humidity']}% and "
                f"wind speed of {data['wind']['speed']} m/s."
            )
        }

        return weather_data