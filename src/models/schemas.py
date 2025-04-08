from pydantic import BaseModel, SecretStr, Field
from typing import List
from typing import Optional, Literal
from datetime import date, datetime

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

class Activity(BaseModel):
    emp_id: str
    date_msg: date
    teams_messages_sent: int
    emails_sent: int
    meetings_attended: int
    work_hours: float

class Awards(BaseModel):
    emp_id: str
    award_type: str
    award_date: date
    reward_points: int

class Leaves(BaseModel):
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

class Sessions(BaseModel):
    id: str
    emp_id: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    status: str
    initial_conversation: Optional[str] = None
    vulnerability_score: Optional[float] = None
    is_escalated: Optional[bool] = False
    

class ReasonItem(BaseModel):
    text: str
    asked: bool = False

class ProbableReason(BaseModel):
    id: Optional[str] = None
    session_id: str
    emp_id: str
    reasons: List[ReasonItem]  
    created_at: Optional[datetime] = None


class Conversations(BaseModel):
    id: Optional[str] = None
    created_at: datetime
    emp_id: str
    session_id: str
    sent_by: str
    conversation: Optional[str] = None


class InterventionPrompt(BaseModel):
    reason: str = Field(description="Detected reason for suggesting an intervention")
    question: str = Field(description="Follow-up question related to the reason")

class InterventionDecision(BaseModel):
    intervention_needed: bool = Field(description="Whether an intervention is needed based on the data")
    confidence_score: float = Field(description="Confidence score between 0 and 1")
    interventions: List[InterventionPrompt] = Field(description="List of reasons with associated questions")


class ReasonAnalysis(BaseModel):
    identified_reason: str = Field(description="The core reason identified from the conversation")
    confidence_level: float = Field(description="Confidence level in the identified reason (0-1)")
    should_escalate: bool = Field(description="Whether this issue should be escalated to HR")
    recommendation: str = Field(description="Recommendation for addressing the issue")




















# Define a class for session reasons
class SessionReason(BaseModel):
    id: Optional[str] = None
    session_id: str
    reason: str
    priority: int
    created_at: Optional[datetime] = None

class MessageSubmission(BaseModel):
    message: str

class SessionResponse(BaseModel):
    intervention_needed: bool
    session_id: Optional[str] = None
    initial_message: Optional[str] = None
    message: Optional[str] = None

class MessageResponse(BaseModel):
    response: str
    session_ended: bool
    should_escalate: Optional[bool] = None
    identified_reason: Optional[str] = None
    confidence_level: Optional[float] = None

class LoginRequest(BaseModel):
    employee_id: str
    password: str
    role: str

class EmployeeDashboard(BaseModel):
    emp_id: str
    emp_name: str
    vulnerability_score: float
    sessions_this_month: int
    escalations_this_year: int
    last_session_date: Optional[datetime]
    current_mood: str
    latest_leave: Optional[Leaves]
    latest_reward: Optional[Awards]
    latest_performance: Optional[PerformanceReview]
    latest_activity: Optional[Activity]

class EscalatedSession(BaseModel):
    session_id: str
    title: Optional[str]
    summary: Optional[str]
    date: datetime

class SessionDetail(BaseModel):
    date: datetime
    summary: Optional[str]
    reasons: List[str]  # List of reasons
    questions: List[str]  # List of questions

class SentimentDistribution(BaseModel):
    date: date
    distribution: dict  # Dictionary with mood as key and percentage as value
    total_count: int

class WorkHourDistribution(BaseModel):
    year: int
    monthly_distributions: dict  # Dictionary with month as key and work hour distribution as value
    total_employees: int

class LeaveDistribution(BaseModel):
    year: int
    distribution: dict  # Dictionary with leave types as key and count of employees as value
    total_employees: int

class InterventionSession(BaseModel):
    # session_id: str
    emp_id: str
    emp_name: str
    started_at: datetime
    # title: Optional[str]
    # summary: Optional[str]
    vulnerability_score: Optional[float]
    # is_escalated: bool = False

class EscalatedChat(BaseModel):
    emp_id: str
    emp_name: str
    vulnerability_score: float
    last_session_date: datetime
    last_session_id: str