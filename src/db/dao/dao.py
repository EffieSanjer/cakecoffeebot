from datetime import timedelta, datetime

from pydantic import BaseModel, create_model
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.db.dao.base import BaseDao
from src.db.exceptions import PlaceNotFoundException, PlaceAlreadyExistsException
from src.db.models import Place, Category, Event, Rating


class CategoryDao(BaseDao):
    model = Category

    @classmethod
    async def get_by_names(cls, session: AsyncSession, names: list[str]):
        """
        Возвращает категории, отфильтрованные по названиям.
        """

        lower_names = [name.lower() for name in names]
        query = select(cls.model).filter(func.lower(cls.model.name).in_(lower_names))

        result = await session.execute(query)
        return result.scalars().all()


class PlaceDao(BaseDao):
    model = Place

    @classmethod
    async def create_place(cls, session: AsyncSession, categories_names: list[str], place_info: BaseModel) -> Place:
        """
        Создает и добавляет заведение.
        """

        place_data = place_info.model_dump(exclude_unset=True)
        place = await cls.get_one_or_none(session=session, filters=place_info)

        if place is not None:
            raise PlaceAlreadyExistsException

        categories = await CategoryDao.get_by_names(session=session, names=categories_names)

        place = cls.model(**place_data)
        place.categories.extend(categories)

        return await cls.commit(session, place)

    @classmethod
    async def get_place_info(cls, session: AsyncSession, place_id: int) -> Place:
        """
        Возвращает информацию о заведении по id.
        """

        query = select(cls.model).options(joinedload(cls.model.ratings)).filter_by(id=place_id)

        result = await session.execute(query)
        record = result.scalars().first()

        if record is None:
            raise PlaceNotFoundException(place_id=place_id)

        return record

    @classmethod
    async def get_places_within_radius(
            cls,
            session: AsyncSession,
            category_id: int,
            center_lat: float,
            center_lon: float,
            radius: float):

        """
        Возвращает подходящие под категорию заведения, чьи координаты
        входят в радиус от заданного центра, рассчитанный по евклидову расстоянию.
        """

        distance = func.sqrt(
            func.pow(cls.model.lat - center_lat, 2) +
            func.pow(cls.model.lon - center_lon, 2)
        )

        query = (
            select(cls.model)
            .options(joinedload(cls.model.categories))
            .filter(cls.model.categories.any(id=category_id))
            .filter(distance <= radius)
        )

        result = await session.execute(query)
        return result.scalars().unique().all()


class RatingDao(BaseDao):
    model = Rating

    @classmethod
    async def create_rating(cls, session: AsyncSession, rating_info: BaseModel) -> Rating:
        """
        Создает и добавляет рейтинг от определенного пользователя заведению по его gis_id.
        """

        info = rating_info.model_dump(exclude_unset=True)
        FilterPlace = create_model("FilterPlace", gis_id=(str, ...))
        place = await PlaceDao.get_one_or_none(session, FilterPlace(gis_id=info.pop('place_gis_id')))

        if place is None:
            raise PlaceNotFoundException

        new_rating = cls.model(place=place, **info)

        return await cls.commit(session, new_rating)


class EventDao(BaseDao):
    model = Event

    @classmethod
    async def get_closest_events(cls, session: AsyncSession, date: datetime.date = None):
        """
        Возвращает ближайшие на месяц мероприятия.
        """

        if not date:
            date = datetime.today()
        query = select(cls.model).filter(
            cls.model.start_at.between(date, date + timedelta(31))
        ).order_by(cls.model.start_at)

        result = await session.execute(query)
        return result.scalars().all()


