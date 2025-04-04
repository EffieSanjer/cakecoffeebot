from httpx import AsyncClient

from  config import settings


async def get_weather(city: str = None, lat: float = None, lon: float = None) -> dict:
    query = {"q": "Москва,Россия"}
    # TODO: closest big city

    if city:
        query = {"q": f"{city},Россия"}
    elif lat and lon:
        query = {"lat": lat, "lon": lon}

    async with AsyncClient() as client:
        response = await client.get(
            url="https://api.openweathermap.org/data/2.5/weather",
            params={
                "appid": settings.WEATHER_API_KEY,
                "lang": "ru",
                "units": "metric",
                **query
            })

        response.raise_for_status()
        data = response.json()

    return {
        "city": data['name'],
        "weather": data['weather'][0]['description'],
        "temp": round(float(data['main']['temp'])),
        "feels_like": round(float(data['main']['feels_like'])),
        "wind": data['wind']['speed'],
    }
