from fastapi import APIRouter, HTTPException, status, Depends
from api.common import get_employee_id
from api.hr import get_escalated_list, get_current_month_daily_sessions, get_current_month_daily_escalations
from services.supabase import supabase
from models.schemas import User
from typing import List
from passlib.context import CryptContext
from datetime import datetime

router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.get("/getdata")
async def get_user_data(employee_id: str = Depends(get_employee_id)):
    try:
        user_result = supabase.table("user")\
            .select("id, role")\
            .eq("id", employee_id)\
            .execute()
        if not user_result.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            
        if user_result.data and user_result.data[0]["role"] == "employee":
            result = supabase.table("vibemeter")\
                .select("created_at")\
                .eq("emp_id", employee_id)\
                .order("created_at", desc=True)\
                .limit(1)\
                .execute()
        
        
            should_submit = True
        
            last_submission = datetime.fromisoformat(result.data[0]["created_at"].replace("Z", "+00:00"))
            today = datetime.utcnow()
            
            days_difference = (today - last_submission).days
            
            should_submit = days_difference >= 2
        
            return {"should_submit": should_submit}
        else:
            escalated_list = get_escalated_list()
            current_month_daily_sessions = get_current_month_daily_sessions()
            current_month_daily_escalations = get_current_month_daily_escalations()
            print('asd')
            print(current_month_daily_sessions)
            return {
                "escalated_list": escalated_list,
                "current_month_daily_sessions": current_month_daily_sessions,
                "current_month_daily_escalations": current_month_daily_escalations
            }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )
    
    