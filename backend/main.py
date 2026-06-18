from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

app = FastAPI(
    title="Absolute Cinema API",
    description="REST API для управління каталогом фільмів та автоматизації кінотеатрального бек-офісу",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Models ────────────────────────────────────────────────────────────────────

class Movie(BaseModel):
    id: int
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    year: int = Field(..., ge=1888, le=2026)  # Жорстке обмеження: максимум 2026 рік
    genre: str = Field(..., min_length=1, max_length=50)
    rating: float = Field(..., ge=0.0, le=10.0)
    poster_url: str = Field(..., min_length=1)
    director: str = Field(..., min_length=1, max_length=200)

    @field_validator("rating")
    @classmethod
    def round_rating(cls, v):
        return round(v, 1)


class MovieCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    year: int = Field(..., ge=1888, le=2026)  # Жорстке обмеження: максимум 2026 рік
    genre: str = Field(..., min_length=1, max_length=50)
    rating: float = Field(..., ge=0.0, le=10.0)
    poster_url: str = Field(..., min_length=1)
    director: str = Field(..., min_length=1, max_length=200)

    @field_validator("rating")
    @classmethod
    def round_rating(cls, v):
        return round(v, 1)


class MovieUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=2000)
    year: Optional[int] = Field(None, ge=1888, le=2026)  # Жорстке обмеження: максимум 2026 рік
    genre: Optional[str] = Field(None, min_length=1, max_length=50)
    rating: Optional[float] = Field(None, ge=0.0, le=10.0)
    poster_url: Optional[str] = Field(None, min_length=1)
    director: Optional[str] = Field(None, min_length=1, max_length=200)

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


# ── In-Memory Database ────────────────────────────────────────────────────────

movies_db: List[Movie] = [
    Movie(id=1,  title="Inception",              year=2010, genre="Sci-Fi",   rating=8.8, director="Christopher Nolan",
          description="Крадій, який краде корпоративні таємниці за допомогою технології обміну снами, отримує шанс повернути своє життя.",
          poster_url="https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_FMjpg_UX1000_.jpg"),

    Movie(id=2,  title="The Matrix",             year=1999, genre="Sci-Fi",   rating=8.7, director="Lana Wachowski",
          description="Комп'ютерний хакер дізнається від таємничих повстанців про справжню природу своєї реальності та свою роль у війні проти її контролерів.",
          poster_url="https://m.media-amazon.com/images/M/MV5BNzQzOTk3OTAtNDQ0Zi00ZTVkLWI0MTEtMDllZjNkYzNjNTc4L2ltYWdlXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_FMjpg_UX1000_.jpg"),

    Movie(id=3,  title="Interstellar",           year=2014, genre="Sci-Fi",   rating=8.6, director="Christopher Nolan",
          description="Команда дослідників подорожує через червоточину в космосі в спробі забезпечити виживання людства на вмираючій Землі.",
          poster_url="https://cdn.ananasposter.ru/image/cache/catalog/poster/film/81/16058-1000x830.jpg"),

    Movie(id=4,  title="Gladiator",              year=2000, genre="Action",   rating=8.5, director="Ridley Scott",
          description="Колишній римський генерал прагне помститися корумпованому імператору, який убив його родину та відправив його в рабство.",
          poster_url="https://m.media-amazon.com/images/I/61O9+6+NxYL._UF894,1000_QL80_.jpg"),

    Movie(id=5,  title="The Dark Knight",        year=2008, genre="Action",   rating=9.0, director="Christopher Nolan",
          description="Коли загроза, відома як Джокер, сіє хаос серед населення Готема, Бетмен має прийняти одне з найбільших психологічних і фізичних випробувань.",
          poster_url="https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_FMjpg_UX1000_.jpg"),

    Movie(id=6,  title="Pulp Fiction",           year=1994, genre="Crime",    rating=8.9, director="Quentin Tarantino",
          description="Долі трьох різних злочинних пар переплітаються у місті Лос-Анджелес: пара злодіїв, боксер і двоє найманих вбивць.",
          poster_url="https://m.media-amazon.com/images/M/MV5BNGNhMDIzZTUtNTBlZi00MTRlLWFjM2ItYzViMjE3YzI5MjljXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_FMjpg_UX1000_.jpg"),

    Movie(id=7,  title="The Shawshank Redemption", year=1994, genre="Drama", rating=9.3, director="Frank Darabont",
          description="Двоє ув'язнених зближуються протягом кількох років, знаходячи розраду та зрештою відкуплення через акти звичайної порядності.",
          poster_url="https://m.media-amazon.com/images/M/MV5BNDE3ODcxYzMtY2YzZC00NmNlLWJiNDMtZDViZWM2MzIxZDYwXkEyXkFqcGdeQXVyNjAwNDUxODI@._V1_FMjpg_UX1000_.jpg"),

    Movie(id=8,  title="Forrest Gump",           year=1994, genre="Drama",    rating=8.8, director="Robert Zemeckis",
          description="Президенти люблять його, Форрест Гамп бере участь у всіх ключових моментах американської історії ХХ сторіччя.",
          poster_url="https://m.media-amazon.com/images/M/MV5BNWIwODRlZTUtY2U3ZS00Yzg1LWJhNzYtMmZiYmEyNmU1NjMzXkEyXkFqcGdeQXVyMTQxNzMzNDI@._V1_FMjpg_UX1000_.jpg"),

    Movie(id=9,  title="The Godfather",          year=1972, genre="Crime",    rating=9.2, director="Francis Ford Coppola",
          description="Старіючий патріарх організованої злочинної династії передає контроль над своєю таємною імперією своєму небажаючому синові.",
          poster_url="https://m.media-amazon.com/images/M/MV5BM2MyNjYxNmUtYTAwNi00MTYxLWJmNWYtYzZlODY3ZTk3OTFlXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_FMjpg_UX1000_.jpg"),

    Movie(id=10, title="Inglourious Basterds",   year=2009, genre="Action",   rating=8.3, director="Quentin Tarantino",
          description="У нацистській окупованій Франції під час Другої світової війни група єврейських американських солдатів планує велику акцію проти нацистського керівництва.",
          poster_url="https://m.media-amazon.com/images/M/MV5BOTJiNDEzOWYtMTVjOC00ZjlmLWE0NGMtZmE1OWVmZDQ2OWJhXkEyXkFqcGdeQXVyNTIzOTk5ODM@._V1_FMjpg_UX1000_.jpg"),

    Movie(id=11, title="Arrival",                year=2016, genre="Sci-Fi",   rating=7.9, director="Denis Villeneuve",
          description="Лінгвіст отримує завдання спілкуватися з інопланетними відвідувачами, намагаючись запобігти глобальній війні.",
          poster_url="https://m.media-amazon.com/images/M/MV5BMTExMzU0ODcxNDheQTJeQWpwZ15BbWU4MDE1OTI4MzAy._V1_FMjpg_UX1000_.jpg"),

    Movie(id=12, title="Blade Runner 2049",      year=2017, genre="Sci-Fi",   rating=8.0, director="Denis Villeneuve",
          description="Молодий блейдранер виявляє давно приховану таємницю, яка може зануритися суспільство у хаос.",
          poster_url="https://m.media-amazon.com/images/M/MV5BNzA1Njg4NzYxOV5BMl5BanBnXkFtZTgwODk5NjU3MzI@._V1_FMjpg_UX1000_.jpg"),

    Movie(id=13, title="Parasite",               year=2019, genre="Thriller", rating=8.5, director="Bong Joon-ho",
          description="Жадібність і класова дискримінація загрожують нещодавно утвореному симбіозу між злиденною родиною Кімів і заможною родиною Паків.",
          poster_url="https://m.media-amazon.com/images/M/MV5BYWZjMjk3ZTItODQ2ZC00NTY5LWE0ZDYtZTI3MjcwN2Q5NTVkXkEyXkFqcGdeQXVyODk4OTc3MTY@._V1_FMjpg_UX1000_.jpg"),

    Movie(id=14, title="Joker",                  year=2019, genre="Drama",    rating=8.4, director="Todd Phillips",
          description="У Готем-Сіті психічно хворий стендап-комік відкидається суспільством і починає спіраль вниз у безумство та насильство.",
          poster_url="https://m.media-amazon.com/images/M/MV5BNGVjNWI4ZGUtNzE0MS00YTJmLWE0ZDctN2ZiYTk2YmI3NTYyXkEyXkFqcGdeQXVyMTkxNjUyNQ@@._V1_FMjpg_UX1000_.jpg"),

    Movie(id=15, title="1917",                   year=2019, genre="Action",   rating=8.3, director="Sam Mendes",
          description="Двоє молодих британських солдатів під час Першої світової війни отримують, здавалося б, неможливу місію: доставити повідомлення, яке може врятувати 1600 людських життів.",
          poster_url="https://m.media-amazon.com/images/M/MV5BOTdmNTFjNDEtNzg0My00ZjkxLTg1ZDAtZTdkMDc2ZmFiNWQ1XkEyXkFqcGdeQXVyNTAzNzgwNTg@._V1_FMjpg_UX1000_.jpg"),
]

_next_id = 16


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
    year_to: Optional[int] = Query(None, le=2026, description="Рік до"),  # Виправлено: обмеження до 2026 року
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


# ── GET /api/movies/{id}/similar ─────────────────────────────────────────────

@app.get("/api/movies/{movie_id}/similar", response_model=List[Movie], tags=["Movies"])
async def get_similar_movies(movie_id: int):
    target = next((m for m in movies_db if m.id == movie_id), None)
    if not target:
        raise HTTPException(status_code=404, detail=f"Фільм з id={movie_id} не знайдено.")

    LIMIT = 5
    others = [m for m in movies_db if m.id != movie_id]
    selected_ids: set[int] = set()
    result: List[Movie] = []

    # Stage 1: same genre
    same_genre = sorted(
        [m for m in others if m.genre == target.genre],
        key=lambda m: m.rating, reverse=True
    )
    for m in same_genre:
        if len(result) >= LIMIT:
            break
        result.append(m)
        selected_ids.add(m.id)

    # Stage 2: same director (not already selected)
    if len(result) < LIMIT:
        same_director = sorted(
            [m for m in others if m.director == target.director and m.id not in selected_ids],
            key=lambda m: m.rating, reverse=True
        )
        for m in same_director:
            if len(result) >= LIMIT:
                break
            result.append(m)
            selected_ids.add(m.id)

    # Stage 3: any remaining films (not already selected)
    if len(result) < LIMIT:
        remaining = sorted(
            [m for m in others if m.id not in selected_ids],
            key=lambda m: m.rating, reverse=True
        )
        for m in remaining:
            if len(result) >= LIMIT:
                break
            result.append(m)
            selected_ids.add(m.id)

    return result


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
        raise HTTPException(status_code=404, detail=f"Фільм з id={movie_id} ne знайдено.")
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