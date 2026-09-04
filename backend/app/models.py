from datetime import datetime
from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base
class User(Base):
    __tablename__="users"; id: Mapped[int]=mapped_column(primary_key=True); email: Mapped[str]=mapped_column(String(255),unique=True,index=True); password_hash: Mapped[str]=mapped_column(String(255)); created_at: Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    profile: Mapped["StudentProfile"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    subjects: Mapped[list["Subject"]] = relationship(back_populates="user", cascade="all, delete-orphan")
class StudentProfile(Base):
    __tablename__="student_profiles"; id: Mapped[int]=mapped_column(primary_key=True); user_id: Mapped[int]=mapped_column(ForeignKey("users.id"),unique=True); name: Mapped[str]=mapped_column(String(120)); course: Mapped[str]=mapped_column(String(120),default=""); semester: Mapped[str]=mapped_column(String(30),default=""); study_hours_per_day: Mapped[float]=mapped_column(Float,default=2); preferred_time: Mapped[str]=mapped_column(String(30),default="Evening")
    user: Mapped[User]=relationship(back_populates="profile")
class Subject(Base):
    __tablename__="subjects"; id: Mapped[int]=mapped_column(primary_key=True); user_id: Mapped[int]=mapped_column(ForeignKey("users.id"),index=True); name: Mapped[str]=mapped_column(String(120)); current_marks: Mapped[float]=mapped_column(Float); max_marks: Mapped[float]=mapped_column(Float,default=100); attendance: Mapped[float]=mapped_column(Float); previous_score: Mapped[float]=mapped_column(Float,default=0); difficulty: Mapped[int]=mapped_column(Integer,default=3); exam_date: Mapped[datetime|None]=mapped_column(Date,nullable=True); progress: Mapped[float]=mapped_column(Float,default=0)
    user: Mapped[User]=relationship(back_populates="subjects"); sessions: Mapped[list["StudySession"]]=relationship(back_populates="subject",cascade="all, delete-orphan")
class Prediction(Base):
    __tablename__="predictions"; id: Mapped[int]=mapped_column(primary_key=True); user_id: Mapped[int]=mapped_column(ForeignKey("users.id")); subject_id: Mapped[int]=mapped_column(ForeignKey("subjects.id")); score: Mapped[float]=mapped_column(Float); category: Mapped[str]=mapped_column(String(30)); risk: Mapped[str]=mapped_column(String(20)); confidence: Mapped[float]=mapped_column(Float); created_at: Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
class StudyPlan(Base):
    __tablename__="study_plans"; id: Mapped[int]=mapped_column(primary_key=True); user_id: Mapped[int]=mapped_column(ForeignKey("users.id")); subject_id: Mapped[int]=mapped_column(ForeignKey("subjects.id")); scheduled_for: Mapped[datetime]=mapped_column(Date); start_time: Mapped[str]=mapped_column(String(10)); duration_minutes: Mapped[int]=mapped_column(Integer); completed: Mapped[bool]=mapped_column(Boolean,default=False)
class StudySession(Base):
    __tablename__="study_sessions"; id: Mapped[int]=mapped_column(primary_key=True); user_id: Mapped[int]=mapped_column(ForeignKey("users.id")); subject_id: Mapped[int]=mapped_column(ForeignKey("subjects.id")); duration_minutes: Mapped[int]=mapped_column(Integer); completed_at: Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow); quiz_score: Mapped[float|None]=mapped_column(Float,nullable=True)
    subject: Mapped[Subject]=relationship(back_populates="sessions")
class AcademicRecord(Base):
    __tablename__="academic_records"; id: Mapped[int]=mapped_column(primary_key=True); user_id: Mapped[int]=mapped_column(ForeignKey("users.id")); subject_id: Mapped[int]=mapped_column(ForeignKey("subjects.id")); score: Mapped[float]=mapped_column(Float); recorded_at: Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
class Quiz(Base):
    __tablename__="quizzes"; id: Mapped[int]=mapped_column(primary_key=True); user_id: Mapped[int]=mapped_column(ForeignKey("users.id")); subject_id: Mapped[int]=mapped_column(ForeignKey("subjects.id")); topic: Mapped[str]=mapped_column(String(160)); created_at: Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
class QuizResult(Base):
    __tablename__="quiz_results"; id: Mapped[int]=mapped_column(primary_key=True); quiz_id: Mapped[int]=mapped_column(ForeignKey("quizzes.id")); score: Mapped[float]=mapped_column(Float); completed_at: Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
