from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import Optional

from database.models import MovieModel
from database.session import get_db
from main import api_version_prefix
from schemas.movies import MovieDetailResponseSchema, MovieListResponseSchema

router = APIRouter(prefix="/movies", tags=["Movies"])


@router.get("/", response_model=MovieListResponseSchema)
async def get_movies(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    total_items = (await db.execute(select(func.count(MovieModel.id)))).scalar()
    if total_items == 0:
        raise HTTPException(status_code=404, detail="No movies found.")

    total_pages = (total_items + per_page - 1) // per_page

    offset = (page - 1) * per_page
    stmt = select(MovieModel).order_by(MovieModel.id).offset(offset).limit(per_page)
    result = await db.execute(stmt)
    movies = result.scalars().all()

    if not movies:
        raise HTTPException(status_code=404, detail="No movies found.")

    base_url = f"{api_version_prefix}/theater/movies/"
    prev_page: Optional[str] = None
    next_page: Optional[str] = None

    if page > 1:
        prev_page = f"{base_url}?page={page - 1}&per_page={per_page}"
    if page < total_pages:
        next_page = f"{base_url}?page={page + 1}&per_page={per_page}"

    return MovieListResponseSchema(
        movies=movies,
        prev_page=prev_page,
        next_page=next_page,
        total_pages=total_pages,
        total_items=total_items,
    )


@router.get("/{movie_id}/", response_model=MovieDetailResponseSchema)
async def get_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(MovieModel).where(MovieModel.id == movie_id)
    result = await db.execute(stmt)
    movie = result.scalars().first()

    if not movie:
        raise HTTPException(status_code=404, detail="Movie with the given ID was not found.")

    return movie
