import asyncio
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine


# uploading env
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

engine = create_engine(f"sqlite:///{os.environ['DB_PATH']}")

from bot import main

if __name__ == "__main__":
    asyncio.run(main())
