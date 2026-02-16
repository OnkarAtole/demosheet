from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.config import settings

# 🔥 ADD THESE 3 IMPORTS
from app.db.session import engine
from app.db.base import Base
from app.models.user import User  # import models so SQLAlchemy registers them


app = FastAPI(title=settings.PROJECT_NAME)

# 🔥 CREATE TABLES (TEMPORARY)
Base.metadata.create_all(bind=engine)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
