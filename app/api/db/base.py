from fastapi import FastAPI, HTTPException, status
from supabase import create_client, Client
from pydantic import BaseModel, EmailStr, SecretStr
from typing import Optional, List
from datetime import date, datetime
import os
from dotenv import load_dotenv
from passlib.context import CryptContext
load_dotenv()

app = FastAPI()

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

# Activity endpoints
@app.post("/activity/", response_model=Activity)
async def create_activity(activity: Activity):
    try:
        response = supabase.table("activity").insert(activity.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.get("/activity/", response_model=List[Activity])
async def read_activities():
    try:
        response = supabase.table("activity").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.get("/activity/{emp_id}", response_model=List[Activity])
async def read_employee_activities(emp_id: str):
    try:
        response = supabase.table("activity").select("*").eq("emp_id", emp_id).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.put("/activity/{emp_id}/{date_msg}", response_model=Activity)
async def update_activity(emp_id: str, date_msg: date, activity: Activity):
    try:
        response = supabase.table("activity").update(activity.dict()).eq("emp_id", emp_id).eq("date_msg", date_msg).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.delete("/activity/{emp_id}/{date_msg}")
async def delete_activity(emp_id: str, date_msg: date):
    try:
        response = supabase.table("activity").delete().eq("emp_id", emp_id).eq("date_msg", date_msg).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")
        return {"message": "Activity deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# Awards endpoints
@app.post("/awards/", response_model=Award)
async def create_award(award: Award):
    try:
        response = supabase.table("awards").insert(award.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.get("/awards/", response_model=List[Award])
async def read_awards():
    try:
        response = supabase.table("awards").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.get("/awards/{emp_id}", response_model=List[Award])
async def read_employee_awards(emp_id: str):
    try:
        response = supabase.table("awards").select("*").eq("emp_id", emp_id).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.put("/awards/{emp_id}/{award_date}", response_model=Award)
async def update_award(emp_id: str, award_date: date, award: Award):
    try:
        response = supabase.table("awards").update(award.dict()).eq("emp_id", emp_id).eq("award_date", award_date).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Award not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.delete("/awards/{emp_id}/{award_date}")
async def delete_award(emp_id: str, award_date: date):
    try:
        response = supabase.table("awards").delete().eq("emp_id", emp_id).eq("award_date", award_date).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Award not found")
        return {"message": "Award deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# Leave Records endpoints
@app.post("/leave/", response_model=LeaveRecord)
async def create_leave(leave: LeaveRecord):
    try:
        response = supabase.table("leave_records").insert(leave.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.get("/leave/", response_model=List[LeaveRecord])
async def read_leaves():
    try:
        response = supabase.table("leave_records").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.get("/leave/{emp_id}", response_model=List[LeaveRecord])
async def read_employee_leaves(emp_id: str):
    try:
        response = supabase.table("leave_records").select("*").eq("emp_id", emp_id).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.put("/leave/{emp_id}/{leave_start_date}", response_model=LeaveRecord)
async def update_leave(emp_id: str, leave_start_date: date, leave: LeaveRecord):
    try:
        response = supabase.table("leave_records").update(leave.dict()).eq("emp_id", emp_id).eq("leave_start_date", leave_start_date).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave record not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.delete("/leave/{emp_id}/{leave_start_date}")
async def delete_leave(emp_id: str, leave_start_date: date):
    try:
        response = supabase.table("leave_records").delete().eq("emp_id", emp_id).eq("leave_start_date", leave_start_date).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave record not found")
        return {"message": "Leave record deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# Performance Reviews endpoints
@app.post("/performance/", response_model=PerformanceReview)
async def create_performance(performance: PerformanceReview):
    try:
        response = supabase.table("performance_reviews").insert(performance.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.get("/performance/", response_model=List[PerformanceReview])
async def read_performances():
    try:
        response = supabase.table("performance_reviews").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.get("/performance/{emp_id}", response_model=List[PerformanceReview])
async def read_employee_performances(emp_id: str):
    try:
        response = supabase.table("performance_reviews").select("*").eq("emp_id", emp_id).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.put("/performance/{emp_id}/{review_period}", response_model=PerformanceReview)
async def update_performance(emp_id: str, review_period: str, performance: PerformanceReview):
    try:
        response = supabase.table("performance_reviews").update(performance.dict()).eq("emp_id", emp_id).eq("review_period", review_period).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Performance review not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.delete("/performance/{emp_id}/{review_period}")
async def delete_performance(emp_id: str, review_period: str):
    try:
        response = supabase.table("performance_reviews").delete().eq("emp_id", emp_id).eq("review_period", review_period).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Performance review not found")
        return {"message": "Performance review deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# VibeMeter endpoints
@app.post("/vibemeter/", response_model=VibeMeter)
async def create_vibe(vibe: VibeMeter):
    try:
        response = supabase.table("vibemeter").insert(vibe.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.get("/vibemeter/", response_model=List[VibeMeter])
async def read_vibes():
    try:
        response = supabase.table("vibemeter").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.get("/vibemeter/{emp_id}", response_model=List[VibeMeter])
async def read_employee_vibes(emp_id: str):
    try:
        response = supabase.table("vibemeter").select("*").eq("emp_id", emp_id).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# Messages endpoints
@app.post("/messages/", response_model=Message)
async def create_message(message: Message):
    try:
        response = supabase.table("messages").insert(message.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.get("/messages/", response_model=List[Message])
async def read_messages():
    try:
        response = supabase.table("messages").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.get("/messages/{session_id}", response_model=List[Message])
async def read_session_messages(session_id: str):
    try:
        response = supabase.table("messages").select("*").eq("session_id", session_id).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# Sessions endpoints
@app.post("/sessions/", response_model=Session)
async def create_session(session: Session):
    try:
        response = supabase.table("sessions").insert(session.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.get("/sessions/", response_model=List[Session])
async def read_sessions():
    try:
        response = supabase.table("sessions").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.get("/sessions/{emp_id}", response_model=List[Session])
async def read_employee_sessions(emp_id: str):
    try:
        response = supabase.table("sessions").select("*").eq("emp_id", emp_id).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.put("/sessions/{id}", response_model=Session)
async def update_session(id: str, session: Session):
    try:
        response = supabase.table("sessions").update(session.dict()).eq("id", id).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# User endpoints
@app.post("/user/", response_model=User)
async def create_user(user: User):
    try:
        user_dict = user.dict()
        # Hash the password before storing
        user_dict["password"] = pwd_context.hash(user_dict["password"])
        # Set timestamps
        now = datetime.utcnow()
        user_dict["created_at"] = now
        user_dict["updated_at"] = now
        
        response = supabase.table("user").insert(user_dict).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.get("/user/", response_model=List[User])
async def read_users():
    try:
        response = supabase.table("user").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.get("/user/{id}", response_model=User)
async def read_user(id: str):
    try:
        response = supabase.table("user").select("*").eq("id", id).single().execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.put("/user/{id}", response_model=User)
async def update_user(id: str, user: User):
    try:
        user_dict = user.dict(exclude_unset=True)
        # Update timestamp
        user_dict["updated_at"] = datetime.utcnow()
        # Hash password if it's being updated
        if "password" in user_dict:
            user_dict["password"] = pwd_context.hash(user_dict["password"])
        
        response = supabase.table("user").update(user_dict).eq("id", id).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.delete("/user/{id}")
async def delete_user(id: str):
    try:
        response = supabase.table("user").delete().eq("id", id).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

def main():
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)

if __name__ == "__main__":
    main()
