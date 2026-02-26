from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base_class import Base


class Result(Base):
    __tablename__ = "Result"   

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"))
    class_id = Column(Integer)
    roll_number = Column(String)
    score = Column(Integer)
    total_questions = Column(Integer)