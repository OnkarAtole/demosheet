from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from app.db.base_class import Base


class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)

    exam_id = Column(Integer, ForeignKey("exams.id"))
    class_id = Column(Integer)

    # roll_number = Column(String)
    roll_number = Column(Integer)
    exam_set = Column(String)

    score = Column(Integer)
    total_questions = Column(Integer)

    percentage = Column(Float)

    wrong_questions = Column(Text)
    skipped_questions = Column(Text)
    detailed_results = Column(Text)