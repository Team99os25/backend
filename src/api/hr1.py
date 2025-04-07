from fastapi import APIRouter, HTTPException, status, Depends, Response, Cookie
from services.supabase import supabase
from models.schemas import User, LoginRequest
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os
import calendar

router = APIRouter()


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


@router.post("/hrdummy")
async def login():
    return {"message": "Login endpoint"}
