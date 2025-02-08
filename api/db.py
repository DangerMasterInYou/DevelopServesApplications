from fastapi import APIRouter
from database.connect import engine
from database.models.base import Base

db_router = APIRouter(prefix="/db", tags=["db"])


@db_router.post('/setup')
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    return {"status": 200}
