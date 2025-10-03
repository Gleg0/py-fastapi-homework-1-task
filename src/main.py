from contextlib import asynccontextmanager

from fastapi import FastAPI

from config.settings import api_version_prefix
from database import init_db, close_db
from routes import movie_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(
    title="Movies homework",
    description="Description of project",
    lifespan=lifespan
)


app.include_router(movie_router, prefix=f"{api_version_prefix}/theater", tags=["theater"])
