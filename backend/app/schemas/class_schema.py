from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ClassBase(BaseModel):
    classname: str


class ClassCreate(ClassBase):
    pass


class ClassUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class ClassResponse(ClassBase):
    id: int
    created_by: int
    created_at: datetime
    student_count: int 

    class Config:
        from_attributes = True
