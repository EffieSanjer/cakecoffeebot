import requests
from decouple import config


def get_location(city: str = "Москва", location: str = None, lat: float = None, lon: float = None):
    if not location:
        location = f"{lat},{lon}"

    response = requests.get(f"https://api.opencagedata.com/geocode/v1/json", {
        "key": config('GEO_API_KEY'),
        "language": "ru",
        "no_annotations": 1,
        "limit": 1,
        "countrycode": "ru",
        "q": f"{location},{city}"
    })

    data = response.json()

    return {
        'name': data['results'][0]['formatted'],
        'geometry': data['results'][0]['geometry'],
    }

