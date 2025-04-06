from pydantic import BaseModel, SecretStr
from typing import Optional
from datetime import date, datetime

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