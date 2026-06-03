from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(
    title="Absolute Cinema API",
    description="REST API для управління каталогом фільмів та автоматизації кінотеатрального бек-офісу",
    version="1.0.0"
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
    title: str
    description: str
    year: int
    genre: str
    rating: float
    poster_url: str

movies_db: List[Movie] = [
    Movie(
        id=1, 
        title="Inception", 
        description="Крадій, який краде корпоративні таємниці за допомогою технології обміну снами, отримує шанс повернути своє життя.", 
        year=2010, 
        genre="Sci-Fi", 
        rating=8.8, 
        poster_url="https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_FMjpg_UX1000_.jpg"
    ),
    Movie(
        id=2, 
        title="The Matrix", 
        description="Комп'ютерний хакер дізнається від таємничих повстанців про справжню природу своєї реальності та свою роль у війні проти її контролерів.", 
        year=1999, 
        genre="Sci-Fi", 
        rating=8.7, 
        poster_url="https://m.media-amazon.com/images/M/MV5BNzQzOTk3OTAtNDQ0Zi00ZTVkLWI0MTEtMDllZjNkYzNjNTc4L2ltYWdlXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_FMjpg_UX1000_.jpg"
    ),
    Movie(
        id=3, 
        title="Interstellar", 
        description="Команда дослідників подорожує через червоточину в космосі в спробі забезпечити виживання людства на вмираючій Землі.", 
        year=2014, 
        genre="Drama", 
        rating=8.6, 
        poster_url="https://cdn.ananasposter.ru/image/cache/catalog/poster/film/81/16058-1000x830.jpg"
    ),
    Movie(
        id=4, 
        title="Gladiator", 
        description="Колишній римський генерал прагне помститися корумпованому імператору, який убив його родину та відправив його в рабство.", 
        year=2000, 
        genre="Action", 
        rating=8.5, 
        poster_url="https://m.media-amazon.com/images/I/61O9+6+NxYL._UF894,1000_QL80_.jpg"
    )
]

# Об'єднаний ендпоінт: повертає все АБО фільтрує за назвою (DSN-4, DSN-5)
@app.get("/api/movies", response_model=List[Movie], status_code=status.HTTP_200_OK, tags=["Movies"])
async def get_movies(title: Optional[str] = None):
    if title:
        filtered_movies = [
            movie for movie in movies_db if title.lower() in movie.title.lower()
        ]
        if not filtered_movies:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Фільм із назвою '{title}' не знайдено в базі даних Absolute Cinema."
            )
        return filtered_movies
    return movies_db