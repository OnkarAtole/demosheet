from fastapi import APIRouter
from app.api.v1.endpoints import auth
from app.api.v1.endpoints import class_route
from app.api.v1.endpoints import student
api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(class_route.router)
api_router.include_router(student.router)
