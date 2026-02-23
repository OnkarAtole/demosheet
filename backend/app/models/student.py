from sqlalchemy import Column, Integer, String,ForeignKey, UniqueConstraint
from app.db.base_class import Base   # ✅ CORRECT

from sqlalchemy.orm import relationship
class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    roll_no = Column(Integer, nullable=False)
    email = Column(String,index=True, nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    class_ref = relationship("Class", back_populates="students")
    __table_args__ = (
        UniqueConstraint('email', 'class_id', name='unique_email_per_class'),  
    )