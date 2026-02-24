from sqlalchemy import Column, Integer, String, ForeignKey, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base

class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    exam_name = Column(String, nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)   # or ForeignKey if class table exists
    roll_no_digit = Column(Integer, nullable=False)
    exam_set = Column(Integer, nullable=False)
    exam_date = Column(Date, nullable=False)
    no_of_subject = Column(Integer, nullable=False)
    total_pages = Column(Integer, default=1)

    subjects = relationship(
        "Subject",
        back_populates="exam_ref",
        cascade="all, delete"
    )
    answer_keys = relationship(
        "AnswerKey",
        back_populates="exam",
        cascade="all, delete-orphan"
    )
    class_ref = relationship("Class", back_populates="exams")
    __table_args__ = (
        UniqueConstraint("exam_name", "class_id", name="unique_exam_per_class"),
    )
