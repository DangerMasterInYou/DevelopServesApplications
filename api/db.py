from fastapi import APIRouter
from starlette import status
from database.connect import SessionDep
from database.seeds.seeds import seeds
from database.connect import engine
from database.models.models import Base


db_router = APIRouter(prefix="/db", tags=["db"])


@db_router.post('/setup', status_code=status.HTTP_201_CREATED)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@db_router.post('/data', status_code=status.HTTP_201_CREATED)
async def refresh_database(session: SessionDep):
    await seeds(session)