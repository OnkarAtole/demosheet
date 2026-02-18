from pydantic import BaseModel
from typing import List

class SubjectCreate(BaseModel):
    sub_name: str
    question_count: int


class ExamCreate(BaseModel):
    exam_name: str
    class_id: int
    roll_no_digit: int
    exam_set: int
    subjects: List[SubjectCreate]
