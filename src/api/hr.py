from fastapi import APIRouter, HTTPException, status, Depends, Cookie
from services.supabase import supabase
from models.schemas import Activity, EmployeeDashboard, User, Sessions, Leaves, Awards, PerformanceReview, VibeMeter, EscalatedSession, SessionDetail
from typing import List
from datetime import date, datetime
from sqlalchemy import func, desc
from jose import JWTError, jwt
import os

router = APIRouter()

# JWT Settings
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def get_escalated_list():
    result = supabase.table("sessions")\
        .select("*")\
        .eq("is_escalated", True)\
        .execute()
    return result

def get_current_month_daily_sessions():
    # Get current date
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    
    # Calculate first and last day of the current month
    first_day = datetime(current_year, current_month, 1)
    last_day_num = calendar.monthrange(current_year, current_month)[1]
    last_day = datetime(current_year, current_month, last_day_num, 23, 59, 59)
    
    # Format dates for Supabase query
    first_day_str = first_day.isoformat()
    last_day_str = last_day.isoformat()
    
    # Query sessions for current month
    result = supabase.table("sessions")\
        .select("*")\
        .gte("started_at", first_day_str)\
        .lte("started_at", last_day_str)\
        .execute()
    
    # Get all sessions for the month
    all_sessions = result.data
    
    # Initialize array with zeros for each day of the month
    days_in_month = last_day_num
    daily_counts = [0] * days_in_month
    # Count sessions for each day
    for session in all_sessions:
        # Parse the created_at date
        session_date = datetime.fromisoformat(session["started_at"].replace('Z', '+00:00'))
        # Get the day (1-indexed)
        day = session_date.day
        print(f"Session date: {session_date}, Day: {day}")
        # Increment count for that day (adjust to 0-indexed for array)
        daily_counts[day - 1] += 1
        print(f"Daily counts: {daily_counts}")
    print(f"Final daily counts: {daily_counts}")
    
    return daily_counts

def get_current_month_daily_escalations():
    # Get current date
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    
    # Calculate first and last day of the current month
    first_day = datetime(current_year, current_month, 1)
    last_day_num = calendar.monthrange(current_year, current_month)[1]
    last_day = datetime(current_year, current_month, last_day_num, 23, 59, 59)
    
    # Format dates for Supabase query
    first_day_str = first_day.isoformat()
    last_day_str = last_day.isoformat()
    
    # Query sessions for current month
    result = supabase.table("sessions")\
        .select("*")\
        .eq("is_escalated", True)\
        .gte("started_at", first_day_str)\
        .lte("started_at", last_day_str)\
        .execute()
    
    # Get all sessions for the month
    all_sessions = result.data
    
    # Initialize array with zeros for each day of the month
    days_in_month = last_day_num
    daily_counts = [0] * days_in_month
    # Count sessions for each day
    for session in all_sessions:
        # Parse the created_at date
        session_date = datetime.fromisoformat(session["started_at"].replace('Z', '+00:00'))
        # Get the day (1-indexed)
        day = session_date.day
        print(f"Session date: {session_date}, Day: {day}")
        # Increment count for that day (adjust to 0-indexed for array)
        daily_counts[day - 1] += 1
        print(f"Daily counts: {daily_counts}")
    print(f"Final daily counts: {daily_counts}")
    
    return daily_counts




async def verify_hr_role(auth_token: str = Cookie(...)):
    if not auth_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    try:
        payload = jwt.decode(auth_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("role") != "hr":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized. HR role required."
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )

@router.get("/employee/{emp_id}", response_model=EmployeeDashboard)
async def get_employee_sessions(
    emp_id: str,
    payload: dict = Depends(verify_hr_role)
):
    try:
        # Get employee basic info
        user_response = supabase.table('user').select('id, name').eq('id', emp_id).execute()
        if not user_response.data:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        user_data = user_response.data[0]
        
        # Get sessions count for this month
        current_month = datetime.now().month
        sessions_response = supabase.table('sessions').select('id').eq('emp_id', emp_id).gte('started_at', f"{datetime.now().year}-{current_month:02d}-01").execute()
        sessions_count = len(sessions_response.data)
        
        # Get last session date
        last_session_response = supabase.table('sessions').select('started_at, is_escalated, vulnerability_score').eq('emp_id', emp_id).order('started_at', desc=True).limit(1).execute()
        last_session = last_session_response.data[0] if last_session_response.data else None
        last_session_date = last_session['started_at'] if last_session else None
        
        # Get latest mood
        mood_response = supabase.table('vibemeter').select('mood').eq('emp_id', emp_id).order('created_at', desc=True).limit(1).execute()
        current_mood = mood_response.data[0]['mood'] if mood_response.data else "Not Available"
        
        # Get latest leave
        leave_response = supabase.table('leaves').select('*').eq('emp_id', emp_id).order('leave_start_date', desc=True).limit(1).execute()
        latest_leave = leave_response.data[0] if leave_response.data else None
        
        # Get latest reward
        reward_response = supabase.table('awards').select('*').eq('emp_id', emp_id).order('award_date', desc=True).limit(1).execute()
        latest_reward = reward_response.data[0] if reward_response.data else None
        
        # Get latest performance review
        performance_response = supabase.table('performance_reviews').select('*').eq('emp_id', emp_id).order('review_period', desc=True).limit(1).execute()
        latest_performance = performance_response.data[0] if performance_response.data else None
        
        # Get latest activity
        activity_response = supabase.table('activity').select('*').eq('emp_id', emp_id).order('date_msg', desc=True).limit(1).execute()
        latest_activity = activity_response.data[0] if activity_response.data else None
        
        # Get escalations count for this year
        escalations_response = supabase.table('sessions').select('id').eq('emp_id', emp_id).eq('status', 'escalated').gte('started_at', f"{datetime.now().year}-01-01").execute()
        escalations_count = len(escalations_response.data)
        
        return EmployeeDashboard(
            emp_id=emp_id,
            emp_name=user_data['name'],
            vulnerability_score=last_session['vulnerability_score'] if last_session and last_session.get('is_escalated') else 0.0,
            sessions_this_month=sessions_count,
            escalations_this_year=escalations_count,
            last_session_date=last_session_date,
            current_mood=current_mood,
            latest_leave=latest_leave,
            latest_reward=latest_reward,
            latest_performance=latest_performance,
            latest_activity=latest_activity
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/employee/{emp_id}/escalated-sessions", response_model=List[EscalatedSession])
async def get_escalated_sessions(
    emp_id: str,
    payload: dict = Depends(verify_hr_role)
):
    try:
        # Get employee basic info to verify existence
        print("Getting escalated sessions for employee:", emp_id)
        user_response = supabase.table('user').select('id').eq('id', emp_id).execute()
        if not user_response.data:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Get all escalated sessions for the employee, ordered by started_at in descending order
        sessions_response = supabase.table('sessions').select(
            'id',
            'title',
            'summary',
            'started_at'
        ).eq('emp_id', emp_id).eq('is_escalated', True).order('started_at', desc=True).execute()
        
        if not sessions_response.data:
            return []
            
        # Transform the data to match our schema
        escalated_sessions = [
            EscalatedSession(
                session_id=session['id'],
                title=session.get('title'),
                summary=session.get('summary'),
                date=session['started_at']
            )
            for session in sessions_response.data
        ]
        
        return escalated_sessions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}", response_model=SessionDetail)
async def get_session_details(
    session_id: str,
    payload: dict = Depends(verify_hr_role)
):
    try:
        # Get session details
        
        print("Getting session details for session:", session_id)
        session_response = supabase.table('sessions').select(
            'started_at',
            'summary'
        ).eq('id', session_id).execute()
        
        if not session_response.data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_data = session_response.data[0]
        
        # Get probable reasons for this session
        reasons_response = supabase.table('probable_reasons').select(
            'interventions'
        ).eq('session_id', session_id).execute()
        
        reasons = []
        questions = []
        
        if reasons_response.data and reasons_response.data[0].get('interventions'):
            interventions = reasons_response.data[0]['interventions']
            for intervention in interventions:
                reasons.append(intervention['reason'])
                questions.append(intervention['question'])
        
        return SessionDetail(
            date=session_data['started_at'],
            summary=session_data.get('summary'),
            reasons=reasons,
            questions=questions
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))