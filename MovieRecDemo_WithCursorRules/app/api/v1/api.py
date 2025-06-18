from fastapi import APIRouter
from app.api.v1.endpoints import movies, auth

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(movies.router, prefix="/movies", tags=["movies"]) 