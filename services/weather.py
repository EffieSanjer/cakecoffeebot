import requests
from decouple import config


def get_weather(city: str = None, lat: float = None, lon: float = None):
    # TODO: closest big city
    query = {"q": "Москва,Россия"}

    if city:
        query = {"q": f"{city},Россия"}
    elif lat and lon:
        query = {
            "lat": lat,
            "lon": lon
        }

    response = requests.get(f"https://api.openweathermap.org/data/2.5/weather", {
        "appid": config('WEATHER_API_KEY'),
        "lang": "ru",
        "units": "metric",
        **query
    })

    data = response.json()
    print(data)

    return {
        "city": data['name'],
        "weather": data['weather'][0]['description'],
        "temp": round(float(data['main']['temp'])),
        "feels_like": round(float(data['main']['feels_like'])),
        "wind": data['wind']['speed'],
    }
