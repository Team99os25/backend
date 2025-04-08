from fastapi import APIRouter, HTTPException, status, Depends, Cookie
from services.supabase import supabase
from models.schemas import Activity, EmployeeDashboard, User, Sessions, Leaves, Awards, PerformanceReview, VibeMeter, EscalatedSession, SessionDetail, SentimentDistribution, WorkHourDistribution, LeaveDistribution, InterventionSession, EscalatedChat
from typing import List, Optional
from datetime import date, datetime, timedelta
from sqlalchemy import func, desc
from jose import JWTError, jwt
import os
import calendar
from collections import Counter

router = APIRouter()

# JWT Settings
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def get_escalated_list():
    result = supabase.table("sessions")\
        .select("*, user:emp_id(name)")\
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

@router.get("/session/{session_id}/unescalate", status_code=status.HTTP_200_OK)
async def unescalate_session(
    session_id: str,
    payload: dict = Depends(verify_hr_role)
):
    try:
        # First check if the session exists
        session_response = supabase.table('sessions').select('id').eq('id', session_id).execute()
        if not session_response.data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Update the session to set is_escalated to false
        update_response = supabase.table('sessions')\
            .update({"is_escalated": False})\
            .eq('id', session_id)\
            .execute()
        
        if not update_response.data:
            raise HTTPException(status_code=500, detail="Failed to update session")
        
        return {"message": "Session un-escalated successfully", "session_id": session_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/daily-count")
async def get_monthly_daily_sessions(
    month: int = None,
    year: int = None,
    payload: dict = Depends(verify_hr_role)
):
    try:
        # Get current date if month or year not provided
        now = datetime.now()
        month = month or now.month
        year = year or now.year

        # Validate month and year
        if not (1 <= month <= 12):
            raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
        if not (2000 <= year <= 2100):  # Reasonable year range
            raise HTTPException(status_code=400, detail="Year must be between 2000 and 2100")

        # Calculate first and last day of the specified month
        first_day = datetime(year, month, 1)
        last_day_num = calendar.monthrange(year, month)[1]
        last_day = datetime(year, month, last_day_num, 23, 59, 59)

        # Check if we're querying the current month
        is_current_month = (year == now.year and month == now.month)
        days_to_count = now.day if is_current_month else last_day_num

        # Format dates for database query
        first_day_str = first_day.isoformat()
        last_day_str = last_day.isoformat()

        # Query sessions for the specified month
        result = supabase.table("sessions")\
            .select("*")\
            .gte("started_at", first_day_str)\
            .lte("started_at", last_day_str)\
            .execute()

        all_sessions = result.data
        daily_counts = [0] * days_to_count

        # Count sessions for each day
        for session in all_sessions:
            session_date = datetime.fromisoformat(session["started_at"].replace('Z', '+00:00'))
            day = session_date.day
            if day <= days_to_count:  # Only count days up to current day for current month
                daily_counts[day - 1] += 1

        return {
            "month": month,
            "year": year,
            "daily_counts": daily_counts,
            "is_current_month": is_current_month,
            "days_counted": days_to_count
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/yearly-escalations")
async def get_yearly_escalations(
    year: int = None,
    payload: dict = Depends(verify_hr_role)
):
    try:
        # Get current year if not provided
        now = datetime.now()
        year = year or now.year

        # Validate year
        if not (2000 <= year <= 2100):  # Reasonable year range
            raise HTTPException(status_code=400, detail="Year must be between 2000 and 2100")

        # Calculate first and last day of the year
        first_day = datetime(year, 1, 1)
        last_day = datetime(year, 12, 31, 23, 59, 59)

        # Format dates for database query
        first_day_str = first_day.isoformat()
        last_day_str = last_day.isoformat()

        # Query escalated sessions for the specified year
        result = supabase.table("sessions")\
            .select("*")\
            .eq("is_escalated", True)\
            .gte("started_at", first_day_str)\
            .lte("started_at", last_day_str)\
            .execute()

        all_sessions = result.data
        monthly_counts = [0] * 12  # Array for 12 months

        # Count escalated sessions for each month
        for session in all_sessions:
            session_date = datetime.fromisoformat(session["started_at"].replace('Z', '+00:00'))
            month = session_date.month
            monthly_counts[month - 1] += 1

        return {
            "year": year,
            "monthly_counts": monthly_counts,
            "total_escalations": sum(monthly_counts)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sentiment-distribution", response_model=SentimentDistribution)
async def get_sentiment_distribution(
    date_str: str,
    payload: dict = Depends(verify_hr_role)
):
    try:
        # Parse the date string
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

        # Calculate start and end of the target date
        start_of_day = datetime.combine(target_date, datetime.min.time())
        end_of_day = datetime.combine(target_date, datetime.max.time())

        # Format dates for database query
        start_str = start_of_day.isoformat()
        end_str = end_of_day.isoformat()

        # Query vibemeter entries for the specified date
        result = supabase.table("vibemeter")\
            .select("mood")\
            .gte("created_at", start_str)\
            .lte("created_at", end_str)\
            .execute()

        if not result.data:
            return SentimentDistribution(
                date=target_date,
                distribution={},
                total_count=0
            )

        # Count occurrences of each mood
        moods = [entry["mood"] for entry in result.data]
        mood_counts = Counter(moods)
        total_count = len(moods)

        # Calculate percentage distribution
        distribution = {
            mood: round((count / total_count) * 100, 2)
            for mood, count in mood_counts.items()
        }

        return SentimentDistribution(
            date=target_date,
            distribution=distribution,
            total_count=total_count
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/work-hours-distribution", response_model=WorkHourDistribution)
async def get_work_hours_distribution(
    week_start_date: Optional[str] = None,
    payload: dict = Depends(verify_hr_role)
):
    try:
        # If week_start_date is not provided, use current week's start
        if week_start_date is None:
            today = datetime.now()
            # Get to Monday of current week
            week_start = today - timedelta(days=today.weekday())
        else:
            try:
                week_start = datetime.strptime(week_start_date, "%Y-%m-%d")
                # Ensure it's a Monday
                if week_start.weekday() != 0:
                    raise HTTPException(status_code=400, detail="Start date must be a Monday")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

        # Calculate end of week (Sunday)
        week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)

        # Format dates for database query
        start_str = week_start.isoformat()
        end_str = week_end.isoformat()

        # Query work hours data for the week
        result = supabase.table("activity")\
            .select("emp_id, work_hours, date_msg")\
            .gte("date_msg", start_str)\
            .lte("date_msg", end_str)\
            .execute()

        if not result.data:
            return WorkHourDistribution(
                year=week_start.year,
                monthly_distributions={},
                total_employees=0
            )

        # Initialize daily distributions
        daily_distributions = {}
        for day in range(7):  # 0-6 for Monday to Sunday
            daily_distributions[day] = 0

        # Process each activity entry
        for entry in result.data:
            # Parse the date to get day of week (0-6)
            entry_date = datetime.fromisoformat(entry["date_msg"].replace("Z", "+00:00"))
            day_of_week = entry_date.weekday()
            
            # Add work hours to the day's total
            daily_distributions[day_of_week] += float(entry["work_hours"])

        # Convert to day names and format hours
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        formatted_distribution = {
            day_names[day]: f"{hours:.1f} hours"
            for day, hours in daily_distributions.items()
        }

        # Get unique employees count
        unique_employees = len(set(entry["emp_id"] for entry in result.data))

        return WorkHourDistribution(
            year=week_start.year,
            monthly_distributions={1: formatted_distribution},  # Using month 1 to represent the week
            total_employees=unique_employees
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/leaves-distribution", response_model=LeaveDistribution)
async def get_leaves_distribution(
    year: int = None,
    payload: dict = Depends(verify_hr_role)
):
    try:
        # Get current year if not provided
        now = datetime.now()
        year = year or now.year

        # Validate year
        if not (2000 <= year <= 2100):
            raise HTTPException(status_code=400, detail="Year must be between 2000 and 2100")

        # Calculate first and last day of the year
        first_day = datetime(year, 1, 1)
        last_day = datetime(year, 12, 31, 23, 59, 59)

        # Format dates for database query
        first_day_str = first_day.isoformat()
        last_day_str = last_day.isoformat()

        # Query leaves for the specified year
        result = supabase.table("leaves")\
            .select("emp_id, leave_type")\
            .gte("leave_start_date", first_day_str)\
            .lte("leave_end_date", last_day_str)\
            .execute()

        if not result.data:
            return LeaveDistribution(
                year=year,
                distribution={},
                total_employees=0
            )

        # Count leaves by type
        leave_types = [entry["leave_type"] for entry in result.data]
        leave_counts = Counter(leave_types)
        total_employees = len(set(entry["emp_id"] for entry in result.data))

        return LeaveDistribution(
            year=year,
            distribution=dict(leave_counts),
            total_employees=total_employees
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/intervention-sessions", response_model=List[InterventionSession])
async def get_intervention_sessions(
    payload: dict = Depends(verify_hr_role)
):
    try:
        # Get today's date range
        today = datetime.now()
        start_of_day = datetime.combine(today.date(), datetime.min.time())
        end_of_day = datetime.combine(today.date(), datetime.max.time())

        # Format dates for database query
        start_str = start_of_day.isoformat()
        end_str = end_of_day.isoformat()

        # Query today's sessions that need intervention but are not escalated
        result = supabase.table("sessions")\
            .select("*, user:emp_id(name)")\
            .eq("is_escalated", False)\
            .not_.is_("vulnerability_score", "null")\
            .gte("started_at", start_str)\
            .lte("started_at", end_str)\
            .order("started_at", desc=True)\
            .execute()

        if not result.data:
            return []

        # Transform the data to match our schema
        intervention_sessions = [
            InterventionSession(
                # session_id=session["id"],
                emp_id=session["emp_id"],
                emp_name=session["user"]["name"],
                started_at=session["started_at"],
                # title=session.get("title"),
                # summary=session.get("summary"),
                vulnerability_score=session.get("vulnerability_score"),
                # is_escalated=False
            )
            for session in result.data
        ]

        return intervention_sessions

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/escalated-chats", response_model=List[EscalatedChat])
async def get_escalated_chats(
    payload: dict = Depends(verify_hr_role)
):
    try:
        # Query sessions that are escalated and have vulnerability scores
        result = supabase.table("sessions")\
            .select("id, emp_id, vulnerability_score, started_at, user:emp_id(name)")\
            .eq("is_escalated", True)\
            .not_.is_("vulnerability_score", "null")\
            .order("started_at", desc=True)\
            .execute()

        if not result.data:
            return []

        # Group sessions by employee to get their latest session
        employee_sessions = {}
        for session in result.data:
            emp_id = session["emp_id"]
            if emp_id not in employee_sessions or session["started_at"] > employee_sessions[emp_id]["started_at"]:
                employee_sessions[emp_id] = session

        # Convert to list and sort by vulnerability score (descending) and date (ascending)
        escalated_chats = [
            EscalatedChat(
                emp_id=emp_id,
                emp_name=session["user"]["name"],
                vulnerability_score=session["vulnerability_score"],
                last_session_date=session["started_at"],
                last_session_id=session["id"]
            )
            for emp_id, session in employee_sessions.items()
        ]

        # Sort by vulnerability score (descending) and then by date (ascending)
        escalated_chats.sort(key=lambda x: (-x.vulnerability_score, x.last_session_date))

        return escalated_chats

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
