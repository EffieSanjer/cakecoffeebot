import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from backend.dao.dao import PlaceDao
from backend.models import Place, Category
from backend.schemas import CategoryPydantic, PlaceCreatePydantic


# Константы для тестовых данных
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
        lat=30.352579,
        lon=59.944117
    ),
    PlaceCreatePydantic(
        title='Test Place 2',
        address='testing st. 4567',
        city='St. Petersburg',
        gis_id='23456543',
        lat=30.353427,
        lon=59.931805
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
    CENTER_LAT = 30.359801
    CENTER_LON = 59.944502
    RADIUS = 0.008  # Примерно 10 минут пешком
    CATEGORY_ID = 1  # ID категории

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

    async def test_get_place_info(self, session: AsyncSession, places_fixture: list[Place]):
        """
        Проверяет, что информация о заведении возвращается корректно.
        """
        test_place = places_fixture[0]
        place = await PlaceDao.get_place_info(session, test_place.id)

        assert place is not None
        assert place.title == 'Test Place'
        assert place.gis_id == '1234567898765'
        assert place.lon == 59.944117
        assert place.lat == 30.352579
        assert len(place.categories) > 0

    async def test_get_places_within_radius(self, session: AsyncSession, places_fixture: list[Place]):
        """
        Проверяет, что заведения в радиусе возвращаются корректно.
        """
        places = await PlaceDao.get_places_within_radius(
            session,
            self.CATEGORY_ID,
            self.CENTER_LAT,
            self.CENTER_LON,
            self.RADIUS
        )

        assert len(places) == 1
        assert places[0].title == 'Test Place'
        assert any(category.id == self.CATEGORY_ID for category in places[0].categories)
