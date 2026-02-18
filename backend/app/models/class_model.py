from sqlalchemy import Column, DateTime, Integer, String,ForeignKey, func
from app.db.base_class import Base   # ✅ CORRECT

from sqlalchemy.orm import relationship

class Class(Base):
    __tablename__="classes"
    id = Column(Integer, primary_key=True, index=True)
    classname = Column(String, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    creator = relationship("User", back_populates="classes")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    exams = relationship("Exam", back_populates="class_ref", cascade="all, delete")
    students = relationship("Student", back_populates="class_ref", cascade="all, delete")
    