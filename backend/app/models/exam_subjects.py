from sqlalchemy import Column, Integer, ForeignKey
from app.db.base_class import Base   # ✅ CORRECT

from sqlalchemy.orm import relationship

class Exam_Subject(Base):
    __tablename__ = "exam_subjects"
    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    exam_ref = relationship("Exam", back_populates="exam_subjects")
    subject_ref = relationship("Subject", back_populates="exam_subjects")