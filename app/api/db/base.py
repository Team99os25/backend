from supabase import create_client, Client
from pydantic import BaseModel, EmailStr, SecretStr
from typing import Optional, List
from datetime import date, datetime
import os
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()

# Supabase setup
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Models
class Activity(BaseModel):
    emp_id: str
    date_msg: date
    teams_messages_sent: int
    emails_sent: int
    meetings_attended: int
    work_hours: float

class Award(BaseModel):
    emp_id: str
    award_type: str
    award_date: date
    reward_points: int

class LeaveRecord(BaseModel):
    emp_id: str
    leave_type: str
    leave_days: int
    leave_start_date: date
    leave_end_date: date

class OnboardingDetail(BaseModel):
    emp_id: str
    joining_date: date
    onboarding_feedback: Optional[str] = None
    mentor_assigned: str
    initial_training_completed: bool

class PerformanceReview(BaseModel):
    emp_id: str
    review_period: str
    performance_rating: float
    manager_feedback: Optional[str] = None
    promotion_consideration: bool

class VibeMeter(BaseModel):
    created_at: datetime
    emp_id: str
    mood: str
    scale: int

class Message(BaseModel):
    id: Optional[str] = None
    created_at: datetime
    session_id: str
    sent_by: str
    message: str

class Session(BaseModel):
    id: Optional[str] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    emp_id: str
    title: str
    summary: Optional[str] = None
    status: str

class User(BaseModel):
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    name: str
    role: str
    score: Optional[float] = None
    password: SecretStr

    class Config:
        json_encoders = {
            SecretStr: lambda v: v.get_secret_value() if v else None
        }

# Define a class for session reasons
class SessionReason(BaseModel):
    id: Optional[str] = None
    session_id: str
    reason: str
    priority: int
    created_at: Optional[datetime] = None

