from datetime import datetime

import pytz

from src.db.dao.dao import PlaceDao
from src.db.database import connection
from src.db.schemas import PlaceCreatePydantic, PlacePydantic


class PlaceUseCase:

    @staticmethod
    def get_daytime():
        # for other timezones (можно просто взять из сообщения пользователя)
        # tz = tzwhere.tzwhere()
        # timeZoneStr = tz.tzNameAt(lat, lng)

        return datetime.now(pytz.timezone('Europe/Moscow'))

    @staticmethod
    def get_radius(minutes):
        avg_speed = 84  # средняя скорость человека в м/мин
        distance_min = avg_speed * minutes
        radius_km = distance_min / 1000
        radius_deg = radius_km / 111.12

        return round(radius_deg, 6)

    @classmethod
    @connection
    async def create_place(cls, session, place_data, categories):
        place_model = PlaceCreatePydantic(**place_data)

        result = await PlaceDao.create_place(session, categories, place_model)

        return PlacePydantic.model_validate(result).model_dump()

    @classmethod
    @connection
    async def get_places_by_point(cls, session, center_lat, center_lon, minutes=13):
        category_id = 2  # dinners
        now = cls.get_daytime()
        if now.hour < 15:
            category_id = 1  # breakfasts

        results = await PlaceDao.get_places_within_radius(
            session,
            category_id,
            center_lat=center_lat,
            center_lon=center_lon,
            radius=cls.get_radius(minutes)
        )

        return [PlacePydantic.model_validate(item).model_dump() for item in results]

    @classmethod
    @connection
    async def get_place_info(cls, session, place_id):
        place = await PlaceDao.get_place_info(session, place_id=place_id)

        if place:
            return PlacePydantic.model_validate(place).model_dump()


place_use_case = PlaceUseCase()
