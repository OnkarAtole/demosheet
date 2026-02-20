from pydantic import BaseModel
from typing import Dict

class AnswerKeyCreate(BaseModel):
    answers: Dict[str, Dict[str, str]]
    # Example:
    # {
    #   "Set 1": {
    #       "Math-1": "A",
    #       "Math-2": "C"
    #   },
    #   "Set 2": {
    #       "Math-1": "B"
    #   }
    # }

class AnswerKeyResponse(BaseModel):
    id: int
    exam_id: int
    set_name: str
    question_key: str
    correct_option: str

    class Config:
        orm_mode = True
