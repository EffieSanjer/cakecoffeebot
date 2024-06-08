import os

import requests


def get_weather(city: str):
    response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lang=ru&units=metric&"
                            f"q={city}&appid={os.environ['WEATHER_API_KEY']}")

    data = response.json()

    return {
        "weather": data['weather'][0]['description'],
        "temp": data['main']['temp'],
        "feels_like": data['main']['feels_like'],
        "wind": data['wind']['speed'],
    }

