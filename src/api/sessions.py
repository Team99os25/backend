from fastapi import APIRouter, HTTPException, status
from services.supabase import supabase
from models.schemas import Session
from typing import List

router = APIRouter()

@router.post("/", response_model=Session)
async def create_session(session: Session):
    try:
        response = supabase.table("sessions").insert(session.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=List[Session])
async def read_sessions():
    try:
        response = supabase.table("sessions").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{emp_id}", response_model=List[Session])
async def read_employee_sessions(emp_id: str):
    try:
        response = supabase.table("sessions").select("*").eq("emp_id", emp_id).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/{id}", response_model=Session)
async def update_session(id: str, session: Session):
    try:
        response = supabase.table("sessions").update(session.dict()).eq("id", id).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))