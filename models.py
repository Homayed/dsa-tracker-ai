from datetime import datetime

from sqlalchemy import Column, Integer, String , DateTime, Text , ForeignKey
from sqlalchemy.orm import relationship

from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key= True, index= True)
    name = Column(String, nullable= False)
    email = Column(String, unique= True, index= True, nullable= False)
    hashed_password = Column(String, nullable= False)
    created_at = Column(DateTime, default= datetime.utcnow)
    problems = relationship("DSAProblem", back_populates="owner")
    notes = relationship("ProblemNote", back_populates="owner")
    mistakes = relationship("Mistake", back_populates="owner")

class DSAProblem(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    title = Column(String, nullable=False)
    platform = Column(String, default="LeetCode")
    difficulty = Column(String, nullable=False)
    pattern = Column(String, nullable=False)
    status = Column(String, default="Solved")
    confidence_level = Column(Integer, nullable=True)
    time_taken_minutes = Column(Integer, nullable=True)

    solution_code = Column(Text, nullable=True)
    time_complexity = Column(String, nullable=True)
    space_complexity = Column(String, nullable=True)

    solved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="problems")
    notes = relationship("ProblemNote", back_populates="problem", cascade="all, delete-orphan")
    mistakes = relationship("Mistake", back_populates="problem", cascade="all, delete-orphan")

class ProblemNote(Base):
    __tablename__ = "problem_notes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)

    content = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="notes")
    problem = relationship("DSAProblem", back_populates="notes")


class Mistake(Base):
    __tablename__ = "mistakes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)

    mistake_category = Column(String, nullable=True)
    description = Column(Text, nullable=False)
    lesson_learned = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="mistakes")
    problem = relationship("DSAProblem", back_populates="mistakes")