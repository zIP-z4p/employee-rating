from fastapi import APIRouter
from app.api.v1.ratings import router as ratings_router
from app.api.v1.employees import router as employees_router
from app.api.v1.departments import router as departments_router
from app.api.v1.reports import router as reports_router

api_router = APIRouter()
api_router.include_router(ratings_router)
api_router.include_router(employees_router)
api_router.include_router(departments_router)
api_router.include_router(reports_router)

