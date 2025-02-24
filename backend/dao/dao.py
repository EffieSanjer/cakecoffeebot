from datetime import timedelta, datetime

from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from backend.dao.base import BaseDao
from backend.models import Place, Category, Event, Rating


class CategoryDao(BaseDao):
    model = Category

    @classmethod
    async def get_by_names(cls, session: AsyncSession, names: list[str]):
        query = select(cls.model).filter(cls.model.name.in_(names))

        result = await session.execute(query)
        return result.scalars().all()


class PlaceDao(BaseDao):
    model = Place

    @classmethod
    async def create_place(cls, session: AsyncSession, categories: list[str], place_info: BaseModel) -> Place:

        place_data = place_info.model_dump(exclude_unset=True)
        place = await cls.get_one_or_none(session=session, filters=place_info)
        categories = await CategoryDao.get_by_names(session=session, names=categories)

        # TODO: if not instance Exception
        if place:
            place.gis_id = place_data['gis_id']
            place.note = place_data['note']
            place.categories.extend(categories)
        else:
            place = cls.model(**place_data)
            place.categories.extend(categories)
            session.add(place)

        await session.commit()
        await session.refresh(place)
        return place

    @classmethod
    async def get_place_info(cls, session: AsyncSession, place_id: int) -> Place:
        query = select(cls.model).options(joinedload(cls.model.ratings)).filter_by(id=place_id)

        result = await session.execute(query)
        # TODO: exception
        return result.scalars().first()

    @classmethod
    async def get_places_within_radius(
            cls,
            session: AsyncSession,
            category_id: int,
            center_lat: float,
            center_lon: float,
            radius: float):

        # Вычисляем евклидово расстояние
        distance = func.sqrt(
            func.pow(cls.model.lat - center_lat, 2) +
            func.pow(cls.model.lon - center_lon, 2)
        )  # 0.007

        query = (
            select(cls.model)
            .filter(cls.model.categories.any(id=category_id))
            .filter(distance <= radius)
        )

        result = await session.execute(query)
        return result.scalars().all()


class RatingDao(BaseDao):
    model = Rating

    @classmethod
    async def create_rating(
            cls,
            session: AsyncSession,
            rating_info: BaseModel):

        info = rating_info.model_dump(exclude_unset=True)
        place = await PlaceDao.get_one_or_none(session=session, gis_id=info['gis_id'])

        if place:
            new_rate = cls.model(**info)
            session.add(new_rate)

            await session.commit()
            return new_rate
        else:
            raise Exception


class EventDao(BaseDao):
    model = Event

    @classmethod
    async def get_events(cls, session: AsyncSession):
        today = datetime.today()
        query = select(Event).filter(
            cls.model.start_at.between(today, today + timedelta(31))
        ).order_by(cls.model.start_at)

        result = await session.execute(query)
        return result.scalars().all()


