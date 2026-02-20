from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class AnswerKey(Base):
    __tablename__ = "answer_keys"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id", ondelete="CASCADE"))
    set_name = Column(String, nullable=False)   # Example: "Set 1"
    question_key = Column(String, nullable=False)  # Example: "Math-1"
    correct_option = Column(String(1), nullable=False)  # A/B/C/D

    # 🔥 Prevent duplicate answer for same question in same set
    __table_args__ = (
        UniqueConstraint("exam_id", "set_name", "question_key"),
    )

    exam = relationship("Exam", back_populates="answer_keys")
