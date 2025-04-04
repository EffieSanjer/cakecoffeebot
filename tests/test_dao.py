import datetime

import pytest
import pytest_asyncio
from pydantic import create_model
from sqlalchemy.ext.asyncio import AsyncSession

from  db.dao.dao import PlaceDao, RatingDao, CategoryDao, EventDao
from  db.models import Category, Place, Event
from  db.schemas import PlaceCreatePydantic, CategoryPydantic, RatingCreatePydantic

CATEGORIES_DATA = [
    CategoryPydantic(name="Breakfasts"),
    CategoryPydantic(name="Lunches")
]

PLACES_DATA = [
    PlaceCreatePydantic(
        title='Test Place',
        address='testing st. 234',
        city='St. Petersburg',
        gis_id='1234567898765',
        lon=30.352579,
        lat=59.944117
    ),
    PlaceCreatePydantic(
        title='Test Place 2',
        address='testing st. 4567',
        city='St. Petersburg',
        gis_id='23456543',
        lon=30.353427,
        lat=59.931805
    )
]


@pytest_asyncio.fixture(scope='function')
async def categories_fixture(session: AsyncSession) -> list[Category]:
    """
    Фикстура для создания тестовых категорий.
    """

    categories = [Category(**data.model_dump()) for data in CATEGORIES_DATA]
    session.add_all(categories)
    await session.flush()
    await session.commit()
    return categories


@pytest_asyncio.fixture(scope='function')
async def places_fixture(session: AsyncSession, categories_fixture: list[Category]) -> list[Place]:
    """
    Фикстура для создания тестовых заведений.
    """

    places = [Place(**data.model_dump()) for data in PLACES_DATA]
    for place in places:
        place.categories.extend(categories_fixture)

    session.add_all(places)
    await session.flush()
    await session.commit()
    return places


@pytest.mark.asyncio
class TestPlaceDao:
    CENTER_LON = 30.359801
    CENTER_LAT = 59.944502
    RADIUS = 0.008  # Примерно 10 минут пешком
    CATEGORY_ID = 1

    async def test_create_place(self, session: AsyncSession, categories_fixture: list[Category]):
        """
        Проверяет, что заведение создается корректно.
        """
        place_data = PlaceCreatePydantic(
            title='Test Place',
            address='testing st. 234',
            city='St. Petersburg',
            gis_id='1234567898765',
            lon=59.946502,
            lat=30.360801
        )
        categories_names = list(map(lambda c: c.name, categories_fixture))

        place = await PlaceDao.create_place(session, categories_names, place_data)

        assert place is not None
        assert place.title == 'Test Place'
        assert place.gis_id == '1234567898765'
        assert place.lon == 59.946502
        assert place.lat == 30.360801

        fetched_place = await PlaceDao.get_place_info(session, place.id)
        assert fetched_place is not None
        assert fetched_place.title == "Test Place"

    async def test_get_place_info(self, session: AsyncSession, places_fixture: list[Place]):
        """
        Проверяет, что информация о заведении возвращается корректно.
        """
        test_place = places_fixture[0]
        place = await PlaceDao.get_place_info(session, test_place.id)

        assert place is not None
        assert place.title == 'Test Place'
        assert place.gis_id == '1234567898765'
        assert place.lat == 59.944117
        assert place.lon == 30.352579
        assert len(place.categories) > 0

    async def test_get_places_within_radius(self, session: AsyncSession, places_fixture: list[Place]):
        """
        Проверяет, что заведения в радиусе возвращаются корректно.
        """
        places = await PlaceDao.get_places_within_radius(
            session,
            self.CATEGORY_ID,
            center_lat=self.CENTER_LAT,
            center_lon=self.CENTER_LON,
            radius=self.RADIUS
        )

        assert len(places) == 1
        assert places[0].title == 'Test Place'
        assert any(category.id == self.CATEGORY_ID for category in places[0].categories)


@pytest.mark.asyncio
class TestRatingDao:
    USER_ID = 12345
    PLACE_GIS_ID = '1234567898765'

    async def test_create_rating(self, session: AsyncSession, places_fixture: list[Place]):
        """
        Проверяет, что рейтинг создается корректно.
        """
        rating_data = RatingCreatePydantic(user_id=self.USER_ID, place_gis_id=self.PLACE_GIS_ID, rating=4.5)

        rating = await RatingDao.create_rating(session, rating_data)

        assert rating is not None
        assert rating.rating == 4.5
        assert rating.user_id == 12345
        assert rating.place.title == 'Test Place'

        FilterIdModel = create_model('FilterId', id=(int, ...))

        fetched_rating = await RatingDao.get_one_or_none(session, FilterIdModel(id=rating.id))
        assert fetched_rating is not None
        assert fetched_rating.id == rating.id


@pytest.mark.asyncio
class TestCategoryDao:
    async def test_get_by_names(self, session: AsyncSession, categories_fixture: list[Category]):
        """
        Проверяет, что категории, отфильтрованные по именам, возвращаются корректно.
        """

        names = ['breakfasts', 'LUNCHES']
        categories = await CategoryDao.get_by_names(session, names)

        assert len(categories) == 2


@pytest.mark.asyncio
class TestEventDao:
    async def test_get_closest_events(self, session: AsyncSession):
        """
        Проверяет, что ближайшие за месяц мероприятия возвращаются корректно.
        """

        today = datetime.date(2025, 1, 1)

        events = [
            Event(
                title='Test Event',
                start_at=datetime.datetime(2025, 1, 2, 12, 0),
                address='Testing st. 123',
                description='test description',
            ),
            Event(
                title='Test Event 2',
                start_at=datetime.datetime(2025, 2, 3, 14, 0),
                address='Testing st. 1235',
                tickets='http://tickets.test',
            ),
        ]
        session.add_all(events)
        await session.flush()
        await session.commit()

        events = await EventDao.get_closest_events(session, today)

        assert len(events) == 1
        assert events[0].title == 'Test Event'

