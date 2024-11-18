import asyncio

from decouple import config
from sqlalchemy import create_engine

engine = create_engine(f"sqlite:///{config('DB_PATH')}")

from bot import main

if __name__ == "__main__":
    asyncio.run(main())
