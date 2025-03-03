from backend.dao.dao import RatingDao
from backend.database import connection
from backend.schemas import RatingPydantic, RatingCreatePydantic


class RatingUseCase:
    @classmethod
    @connection
    async def create_rating(cls, session, rating_data):
        rating_model = RatingCreatePydantic(**rating_data)
        result = await RatingDao.create_rating(session, rating_model)

        return RatingPydantic.model_validate(result).model_dump()


rating_use_case = RatingUseCase()
