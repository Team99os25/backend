from fastapi import APIRouter, HTTPException, status, Depends
from api.common import get_employee_id
from services.supabase import supabase
from models.schemas import Sessions
from typing import List, Optional

router = APIRouter()

@router.get("/employee")
async def read_employee_sessions(emp_id: str = Depends(get_employee_id)):
    try:
        response = supabase.table("sessions").select("*").eq("emp_id", emp_id).order("started_at", desc=True).execute()

        # Handle case where no sessions are found
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No sessions found for this employee.")

        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to fetch sessions: {str(e)}")


@router.get("/employee/{session_id}", response_model=Sessions)
async def get_session(  session_id: str , emp_id: str = Depends(get_employee_id)):
    try:
        response = supabase.table("sessions").select("*").eq("id", session_id).eq("emp_id", emp_id).single().execute()

        # Handle case where no session is found
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found for this employee.")

        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to fetch session: {str(e)}")
