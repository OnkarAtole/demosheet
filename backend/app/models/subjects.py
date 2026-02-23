from sqlalchemy import Column, ForeignKey, Integer, String
from app.db.base_class import Base   # ✅ CORRECT

from sqlalchemy.orm import relationship

class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True, index=True)
    sub_name = Column(String, nullable=False)
    question_count = Column(Integer, nullable=False)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    exam_ref = relationship("Exam", back_populates="subjects")
    


