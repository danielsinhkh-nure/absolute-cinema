from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime

app = FastAPI(
    title="Absolute Cinema API",
    description="REST API для управління каталогом фільмів та автоматизації кінотеатрального бек-офісу",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Movie(BaseModel):
    id: int
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    year: int = Field(..., ge=1888, le=datetime.now().year + 5)
    genre: str = Field(..., min_length=1, max_length=50)
    rating: float = Field(..., ge=0.0, le=10.0)
    poster_url: str = Field(..., min_length=1)

    @field_validator("rating")
    @classmethod
    def round_rating(cls, v):
        return round(v, 1)


class MovieCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    year: int = Field(..., ge=1888, le=datetime.now().year + 5)
    genre: str = Field(..., min_length=1, max_length=50)
    rating: float = Field(..., ge=0.0, le=10.0)
    poster_url: str = Field(..., min_length=1)

    @field_validator("rating")
    @classmethod
    def round_rating(cls, v):
        return round(v, 1)


class MovieUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=2000)
    year: Optional[int] = Field(None, ge=1888, le=datetime.now().year + 5)
    genre: Optional[str] = Field(None, min_length=1, max_length=50)
    rating: Optional[float] = Field(None, ge=0.0, le=10.0)
    poster_url: Optional[str] = Field(None, min_length=1)

    @field_validator("rating")
    @classmethod
    def round_rating(cls, v):
        if v is not None:
            return round(v, 1)
        return v


class PaginatedMovies(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    movies: List[Movie]


movies_db: List[Movie] = [
    Movie(id=1, title="Inception", description="Крадій, який краде корпоративні таємниці за допомогою технології обміну снами, отримує шанс повернути своє життя.", year=2010, genre="Sci-Fi", rating=8.8, poster_url="https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_FMjpg_UX1000_.jpg"),
    Movie(id=2, title="The Matrix", description="Комп'ютерний хакер дізнається від таємничих повстанців про справжню природу своєї реальності та свою роль у війні проти її контролерів.", year=1999, genre="Sci-Fi", rating=8.7, poster_url="https://m.media-amazon.com/images/M/MV5BNzQzOTk3OTAtNDQ0Zi00ZTVkLWI0MTEtMDllZjNkYzNjNTc4L2ltYWdlXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_FMjpg_UX1000_.jpg"),
    Movie(id=3, title="Interstellar", description="Команда дослідників подорожує через червоточину в космосі в спробі забезпечити виживання людства на вмираючій Землі.", year=2014, genre="Drama", rating=8.6, poster_url="https://cdn.ananasposter.ru/image/cache/catalog/poster/film/81/16058-1000x830.jpg"),
    Movie(id=4, title="Gladiator", description="Колишній римський генерал прагне помститися корумпованому імператору, який убив його родину та відправив його в рабство.", year=2000, genre="Action", rating=8.5, poster_url="https://m.media-amazon.com/images/I/61O9+6+NxYL._UF894,1000_QL80_.jpg"),
    Movie(id=5, title="The Dark Knight", description="Коли загроза, відома як Джокер, сіє хаос серед населення Готема, Бетмен має прийняти одне з найбільших психологічних і фізичних випробувань.", year=2008, genre="Action", rating=9.0, poster_url="https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_FMjpg_UX1000_.jpg"),
    Movie(id=6, title="Pulp Fiction", description="Долі трьох різних злочинних пар переплітаються у місті Лос-Анджелес: пара злодіїв, боксер і двоє найманих вбивць.", year=1994, genre="Crime", rating=8.9, poster_url="https://m.media-amazon.com/images/M/MV5BNGNhMDIzZTUtNTBlZi00MTRlLWFjM2ItYzViMjE3YzI5MjljXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_FMjpg_UX1000_.jpg"),
]

_next_id = 7


def get_next_id() -> int:
    global _next_id
    current = _next_id
    _next_id += 1
    return current


# ── GET /api/movies ──────────────────────────────────────────────────────────
@app.get("/api/movies", response_model=PaginatedMovies, tags=["Movies"])
async def get_movies(
    title: Optional[str] = Query(None, description="Фільтр за назвою (часткова відповідність)"),
    genre: Optional[str] = Query(None, description="Фільтр за жанром"),
    year_from: Optional[int] = Query(None, ge=1888, description="Рік від"),
    year_to: Optional[int] = Query(None, le=datetime.now().year + 5, description="Рік до"),
    rating_min: Optional[float] = Query(None, ge=0.0, le=10.0, description="Мінімальний рейтинг"),
    sort_by: Optional[str] = Query("id", description="Поле для сортування: id, title, year, rating"),
    sort_order: Optional[str] = Query("asc", description="Порядок: asc або desc"),
    page: int = Query(1, ge=1, description="Номер сторінки"),
    page_size: int = Query(12, ge=1, le=100, description="Кількість на сторінці"),
):
    results = list(movies_db)

    if title:
        results = [m for m in results if title.lower() in m.title.lower()]
    if genre:
        results = [m for m in results if genre.lower() == m.genre.lower()]
    if year_from is not None:
        results = [m for m in results if m.year >= year_from]
    if year_to is not None:
        results = [m for m in results if m.year <= year_to]
    if rating_min is not None:
        results = [m for m in results if m.rating >= rating_min]

    valid_sort = {"id", "title", "year", "rating"}
    if sort_by not in valid_sort:
        sort_by = "id"
    reverse = sort_order.lower() == "desc"
    results.sort(key=lambda m: getattr(m, sort_by), reverse=reverse)

    total = len(results)
    total_pages = max(1, (total + page_size - 1) // page_size)
    start = (page - 1) * page_size
    paginated = results[start: start + page_size]

    return PaginatedMovies(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        movies=paginated,
    )


# ── GET /api/movies/genres ───────────────────────────────────────────────────
@app.get("/api/movies/genres", response_model=List[str], tags=["Movies"])
async def get_genres():
    return sorted({m.genre for m in movies_db})


# ── GET /api/movies/{id} ─────────────────────────────────────────────────────
@app.get("/api/movies/{movie_id}", response_model=Movie, tags=["Movies"])
async def get_movie(movie_id: int):
    movie = next((m for m in movies_db if m.id == movie_id), None)
    if not movie:
        raise HTTPException(status_code=404, detail=f"Фільм з id={movie_id} не знайдено.")
    return movie


# ── POST /api/movies ─────────────────────────────────────────────────────────
@app.post("/api/movies", response_model=Movie, status_code=status.HTTP_201_CREATED, tags=["Movies"])
async def create_movie(data: MovieCreate):
    if any(m.title.lower() == data.title.lower() for m in movies_db):
        raise HTTPException(status_code=409, detail=f"Фільм із назвою '{data.title}' вже існує.")
    movie = Movie(id=get_next_id(), **data.model_dump())
    movies_db.append(movie)
    return movie


# ── PUT /api/movies/{id} ─────────────────────────────────────────────────────
@app.put("/api/movies/{movie_id}", response_model=Movie, tags=["Movies"])
async def update_movie(movie_id: int, data: MovieUpdate):
    idx = next((i for i, m in enumerate(movies_db) if m.id == movie_id), None)
    if idx is None:
        raise HTTPException(status_code=404, detail=f"Фільм з id={movie_id} не знайдено.")
    current = movies_db[idx].model_dump()
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    current.update(updates)
    movies_db[idx] = Movie(**current)
    return movies_db[idx]


# ── DELETE /api/movies/{id} ──────────────────────────────────────────────────
@app.delete("/api/movies/{movie_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Movies"])
async def delete_movie(movie_id: int):
    idx = next((i for i, m in enumerate(movies_db) if m.id == movie_id), None)
    if idx is None:
        raise HTTPException(status_code=404, detail=f"Фільм з id={movie_id} не знайдено.")
    movies_db.pop(idx)