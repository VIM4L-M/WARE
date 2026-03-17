import httpx
import random

BASE_URL = "https://api.escuelajs.co/api/v1"

WEATHER_TO_CLOTHING = {
    "Clear": {
        "items": ["White Cotton T-Shirt", "Linen Shorts", "Sunglasses", "Lightweight Sneakers", "Cap"],
        "description": "light and breathable clothing",
        "tip": "Stay cool with breathable fabrics. Light colors reflect heat better."
    },
    "Clouds": {
        "items": ["Casual Shirt", "Jeans", "Light Hoodie", "Sneakers", "Light Jacket"],
        "description": "comfortable layered clothing",
        "tip": "Layer up lightly — it may get cooler later in the day."
    },
    "Rain": {
        "items": ["Waterproof Jacket", "Rain Boots", "Waterproof Trousers", "Umbrella", "Quick-dry Socks"],
        "description": "waterproof and rain-resistant clothing",
        "tip": "Prioritize waterproof materials. Avoid suede or canvas shoes."
    },
    "Drizzle": {
        "items": ["Light Rain Jacket", "Hoodie", "Water-resistant Shoes", "Jeans", "Compact Umbrella"],
        "description": "light waterproof clothing",
        "tip": "A light rain jacket is enough. Keep a compact umbrella handy."
    },
    "Thunderstorm": {
        "items": ["Heavy Raincoat", "Waterproof Boots", "Warm Layers", "Waterproof Bag Cover"],
        "description": "heavy waterproof clothing",
        "tip": "Stay indoors if possible. If going out wear full waterproof gear."
    },
    "Snow": {
        "items": ["Heavy Winter Coat", "Thermal Underlayer", "Snow Boots", "Woolen Gloves", "Scarf", "Beanie"],
        "description": "heavy winter clothing",
        "tip": "Layer up with thermals underneath. Keep extremities covered."
    },
    "Mist": {
        "items": ["Light Jacket", "Full Sleeve Shirt", "Comfortable Trousers", "Closed Shoes"],
        "description": "light layered clothing",
        "tip": "Visibility may be low — wear bright or reflective clothing."
    },
    "Haze": {
        "items": ["Breathable Full Sleeve Shirt", "Light Trousers", "Face Mask", "Sunglasses"],
        "description": "light protective clothing",
        "tip": "Cover exposed skin. A face mask helps with air quality."
    },
    "Fog": {
        "items": ["Light Jacket", "Full Sleeve Shirt", "Trousers", "Bright Colored Clothing"],
        "description": "light layered bright clothing",
        "tip": "Wear bright colors so you are visible in low visibility conditions."
    },
}

TEMP_ADVICE = [
    (35, "🥵 Very hot! Wear minimal and breathable fabrics only."),
    (28, "☀️ Hot weather — light cotton or linen clothing recommended."),
    (20, "🌤️ Comfortable temperature — dress casually."),
    (12, "🌥️ Cool weather — add a hoodie or light jacket."),
    (5,  "🧥 Cold weather — wear a proper jacket with warm layers."),
    (float('-inf'), "🥶 Very cold! Heavy coat, thermals and warm boots are a must."),
]


async def get_clothing(weather_condition: str, temperature_celsius: float) -> dict:
    """
    Suggests clothing based on weather condition and temperature.
    Returns specific clothing items with weather-appropriate advice.
    """

    # Get temperature advice
    temp_advice = TEMP_ADVICE[-1][1]
    for threshold, advice in TEMP_ADVICE:
        if temperature_celsius >= threshold:
            temp_advice = advice
            break

    # Get weather based clothing
    condition_key = weather_condition if weather_condition in WEATHER_TO_CLOTHING else "Clear"
    clothing_data = WEATHER_TO_CLOTHING[condition_key]

    # Fetch some products from Platzi as store suggestions
    store_products = []
    async with httpx.AsyncClient() as client:
        try:
            offset = random.randint(0, 10)
            response = await client.get(
                f"{BASE_URL}/products",
                params={"categoryId": 1, "limit": 3, "offset": offset}
            )
            if response.status_code == 200:
                raw = response.json()
                for p in raw:
                    store_products.append({
                        "name": p.get("title", ""),
                        "price": f"${p.get('price', 0)}",
                        "image": p.get("images", [""])[0] if p.get("images") else ""
                    })
        except Exception:
            store_products = []

    return {
        "weather_condition": weather_condition,
        "temperature_celsius": temperature_celsius,
        "temperature_advice": temp_advice,
        "clothing_type": clothing_data["description"],
        "recommended_items": clothing_data["items"],
        "pro_tip": clothing_data["tip"],
        "store_products": store_products,
        "summary": (
            f"For {weather_condition} weather at {temperature_celsius}°C — "
            f"wear {clothing_data['description']}.\n"
            f"Recommended: {', '.join(clothing_data['items'])}.\n"
            f"💡 Tip: {clothing_data['tip']}\n"
            f"{temp_advice}"
        )
    }