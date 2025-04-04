import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DEBUG: bool = False

    TG_TOKEN: str
    ADMINS_TG_ID: list[int]

    WEATHER_API_KEY: str
    GEO_API_KEY: str
    STATIC_MAP_API_KEY: str
    GIS_API_KEY: str

    DB_PATH: str
    TEST_DB_PATH: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.env")
    )

    def get_db_url(self):
        return f"sqlite+aiosqlite:///{self.DB_PATH}"

    def get_test_db_url(self):
        return f"sqlite+aiosqlite:///{self.TEST_DB_PATH}"


settings = Settings()
