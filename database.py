from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import create_engine

# Подключение к базе данных (PostgreSQL)
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/ServDevDB"
engine = create_engine(DATABASE_URL)