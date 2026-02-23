from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class StudentBase(BaseModel):
    name: str
    roll_no: int
    email: str
    class_id: int


class StudentCreate(StudentBase):
    pass


class StudentResponse(StudentBase):
    id: int

    class Config:
        from_attributes = True
