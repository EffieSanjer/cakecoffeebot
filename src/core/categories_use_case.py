from db.dao.dao import CategoryDao
from db.database import connection
from db.schemas import CategoryPydantic


class CategoryUseCase:
    @classmethod
    @connection
    async def get_categories_by_names(cls, session, categories_names):
        results = await CategoryDao.get_by_names(session, categories_names)

        return [CategoryPydantic.model_validate(item).model_dump() for item in results]

    @classmethod
    @connection
    async def get_categories(cls, session, by_names: bool = False):
        categories = await CategoryDao.get_all(session)
        results = [CategoryPydantic.model_validate(item).model_dump() for item in categories]

        if by_names:
            return '\n• '.join([_['name'] for _ in results])
        return results


category_use_case = CategoryUseCase()
