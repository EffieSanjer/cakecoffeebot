import httpx
import pytest

from  services.weather import get_weather


@pytest.mark.parametrize('city, lat, lon', [
    ('Москва', None, None),
    (None, 59.934798, 30.328001)
])
@pytest.mark.asyncio
async def test_weather_api(city: str, lat: float, lon: float):
    try:
        data = await get_weather(city, lat, lon)
    except httpx.HTTPStatusError as e:
        pytest.fail(f'Error: {e}')

    assert isinstance(data, dict)

    if city:
        assert data['city'].strip().lower() == city.lower()

    assert 'weather' in data

