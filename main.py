import asyncio
import os

from dotenv import load_dotenv

# uploading env
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from bot import main

if __name__ == "__main__":
    asyncio.run(main())
