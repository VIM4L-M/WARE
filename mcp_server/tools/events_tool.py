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
    """
    Fetches upcoming events near a given location using Ticketmaster API.

    Args:
        location: City name or keyword to search events near
        limit: Maximum number of events to return (default 2)

    Returns:
        dict with list of upcoming events near the location
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BASE_URL}/events.json",
                params={
                    "apikey": TICKETMASTER_API_KEY,
                    "city": location,
                    "size": limit,
                    "sort": "date,asc",
                }
            )

            if response.status_code != 200:
                return {
                    "error": f"Could not fetch events for '{location}'",
                    "status_code": response.status_code,
                    "events": []
                }

            data = response.json()
            raw_events = data.get("_embedded", {}).get("events", [])

            if not raw_events:
                return {
                    "location": location,
                    "events": [],
                    "message": f"No upcoming events found near {location}"
                }

            events = []
            for event in raw_events[:limit]:
                # Get event category/classification
                classifications = event.get("classifications", [{}])
                segment = classifications[0].get("segment", {}).get("name", "").lower() if classifications else ""
                genre = classifications[0].get("genre", {}).get("name", "").lower() if classifications else ""

                # Get venue info
                venues = event.get("_embedded", {}).get("venues", [{}])
                venue = venues[0] if venues else {}

                # Get date info
                dates = event.get("dates", {}).get("start", {})
                event_date = dates.get("localDate", "TBD")
                event_time = dates.get("localTime", "TBD")

                events.append({
                    "name": event.get("name", "Unknown Event"),
                    "date": event_date,
                    "time": event_time,
                    "venue": venue.get("name", "Unknown Venue"),
                    "address": venue.get("address", {}).get("line1", ""),
                    "city": venue.get("city", {}).get("name", location),
                    "segment": segment,
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


async def suggest_event_outfit(event_type: str, temperature_celsius: float) -> dict:
    """
    Suggests an outfit suitable for a specific event type and current weather.

    Args:
        event_type: Type/segment of the event (e.g. "music", "sports", "arts")
        temperature_celsius: Current temperature in Celsius to factor in weather

    Returns:
        dict with outfit suggestion tailored to both the event and weather
    """

    # Match event type to outfit map
    event_key = "default"
    for key in EVENT_OUTFIT_MAP:
        if key in event_type.lower():
            event_key = key
            break

    outfit = EVENT_OUTFIT_MAP[event_key]

    # Get temperature layer advice
    layer_advice = ""
    for level, (threshold, advice) in TEMP_LAYER_ADVICE.items():
        if temperature_celsius >= threshold:
            layer_advice = advice
            break
    if not layer_advice:
        layer_advice = TEMP_LAYER_ADVICE["very_cold"][1]

    # Decide casual vs formal based on event type
    is_formal = event_key in ["theatre", "arts"]
    outfit_items = outfit["formal"] if is_formal else outfit["casual"]

    return {
        "event_type": event_type,
        "temperature_celsius": temperature_celsius,
        "outfit_style": "formal" if is_formal else "casual",
        "recommended_items": outfit_items,
        "event_description": outfit["description"],
        "weather_layer_advice": layer_advice,
        "summary": (
            f"For a {event_type} event, we recommend: {', '.join(outfit_items)}. "
            f"{outfit['description']}. "
            f"{layer_advice}."
        )
    }