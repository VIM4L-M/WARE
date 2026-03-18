import httpx
import os
from dotenv import load_dotenv

load_dotenv()

TICKETMASTER_API_KEY = os.getenv("TICKETMASTER_API_KEY")
BASE_URL = "https://app.ticketmaster.com/discovery/v2"

EVENT_OUTFIT_MAP = {
    "music": {
        "casual": ["band t-shirt", "jeans", "sneakers"],
        "formal": ["blazer", "dress shirt", "chinos"],
        "description": "Smart casual — jeans with a nice top or band tee works great for concerts"
    },
    "sports": {
        "casual": ["sports jersey", "joggers", "sneakers"],
        "formal": ["polo shirt", "chinos", "loafers"],
        "description": "Comfortable and casual — wear your team jersey or sporty outfit"
    },
    "arts": {
        "casual": ["smart casual top", "trousers", "loafers"],
        "formal": ["blazer", "dress", "heels or formal shoes"],
        "description": "Smart casual to semi-formal — neat and presentable attire"
    },
    "theatre": {
        "casual": ["smart shirt", "trousers", "loafers"],
        "formal": ["suit", "evening dress", "formal shoes"],
        "description": "Semi-formal to formal — dress to impress for theatre events"
    },
    "comedy": {
        "casual": ["t-shirt", "jeans", "sneakers"],
        "formal": ["smart casual shirt", "chinos"],
        "description": "Casual and comfortable — anything goes for a comedy show"
    },
    "festival": {
        "casual": ["graphic tee", "shorts or jeans", "comfortable boots or sneakers"],
        "formal": ["casual dress", "light jacket"],
        "description": "Festival wear — fun, colorful and comfortable clothing"
    },
    "family": {
        "casual": ["comfortable clothes", "sneakers"],
        "formal": ["smart casual"],
        "description": "Comfortable family-friendly attire"
    },
    "default": {
        "casual": ["smart casual top", "jeans", "sneakers"],
        "formal": ["blazer", "dress shirt", "trousers"],
        "description": "Smart casual is always a safe bet for any event"
    }
}

TEMP_LAYER_ADVICE = {
    "very_hot": (35, "It will be very hot — wear light breathable fabrics"),
    "hot": (28, "It's hot — opt for light fabrics and avoid heavy layers"),
    "warm": (20, "Comfortable temperature — dress as suggested"),
    "cool": (12, "It's cool — bring a light jacket over your outfit"),
    "cold": (5, "It's cold — layer up with a coat over your event outfit"),
    "very_cold": (float('-inf'), "Very cold — wear thermals underneath and a heavy coat on top"),
}


async def get_events(location: str, limit: int = 2) -> dict:
    async with httpx.AsyncClient() as client:
        try:
            # First try with full location
            response = await client.get(
                f"{BASE_URL}/events.json",
                params={
                    "apikey": TICKETMASTER_API_KEY,
                    "keyword": location,
                    "size": limit,
                    "sort": "date,asc",
                }
            )

            data = response.json()
            raw_events = data.get("_embedded", {}).get("events", [])

            # If no events found, extract country and retry
            if not raw_events:
                # Extract country from location (e.g. "Chennai, India" → "India")
                parts = location.split(",")
                if len(parts) > 1:
                    country = parts[-1].strip()
                    retry_response = await client.get(
                        f"{BASE_URL}/events.json",
                        params={
                            "apikey": TICKETMASTER_API_KEY,
                            "keyword": country,
                            "size": limit,
                            "sort": "date,asc",
                        }
                    )
                    data = retry_response.json()
                    raw_events = data.get("_embedded", {}).get("events", [])

            if not raw_events:
                return {
                    "location": location,
                    "events": [],
                    "message": f"No upcoming events found near {location} on Ticketmaster. Ticketmaster has limited coverage outside the US."
                }

            events = []
            for event in raw_events[:limit]:
                classifications = event.get("classifications", [{}])
                segment = classifications[0].get("segment", {}).get("name", "").lower() if classifications else "music"
                genre = classifications[0].get("genre", {}).get("name", "").lower() if classifications else ""
                venues = event.get("_embedded", {}).get("venues", [{}])
                venue = venues[0] if venues else {}
                dates = event.get("dates", {}).get("start", {})

                events.append({
                    "name": event.get("name", "Unknown Event"),
                    "date": dates.get("localDate", "TBD"),
                    "time": dates.get("localTime", "TBD"),
                    "venue": venue.get("name", "Unknown Venue"),
                    "address": venue.get("address", {}).get("line1", ""),
                    "city": venue.get("city", {}).get("name", location),
                    "segment": segment if segment else "music",
                    "genre": genre,
                    "url": event.get("url", ""),
                    "price_range": (
                        f"${event['priceRanges'][0]['min']} - ${event['priceRanges'][0]['max']}"
                        if event.get("priceRanges") else "Price not available"
                    )
                })

            return {
                "location": location,
                "total_events_found": len(events),
                "events": events
            }

        except Exception as e:
            return {
                "error": str(e),
                "events": []
            }