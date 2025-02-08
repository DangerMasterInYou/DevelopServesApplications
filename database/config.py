from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    DB: str
    HOST: str
    DB_NAME: str

    @property
    def db_url_asyncpg(self):
        return f'{self.DB}+aiosqlite:///{self.DB_NAME}.db'

    class Config:
        env_file = '.env'
        extra = "allow"


settings = Settings()
