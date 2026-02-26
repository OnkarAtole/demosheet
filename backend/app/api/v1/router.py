from fastapi import APIRouter
from app.api.v1.endpoints import auth
from app.api.v1.endpoints import class_route
from app.api.v1.endpoints import student
from app.api.v1.endpoints import exam_route
from app.api.v1.endpoints import answer_key_route
from app.api.v1.endpoints import users
from app.api.v1.endpoints import scan_omr

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(class_route.router)
api_router.include_router(student.router)
api_router.include_router(exam_route.router)
api_router.include_router(answer_key_route.router)
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(scan_omr.router, prefix="/omr", tags=["OMR"])


