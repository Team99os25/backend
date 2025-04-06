from fastapi import APIRouter, HTTPException, status
from services.supabase import supabase
from models.schemas import VibeMeter
from typing import List

router = APIRouter()

@router.post("/", response_model=VibeMeter)
async def create_vibe(vibe: VibeMeter):
    try:
        response = supabase.table("vibemeter").insert(vibe.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=List[VibeMeter])
async def read_vibes():
    try:
        response = supabase.table("vibemeter").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{emp_id}", response_model=List[VibeMeter])
async def read_employee_vibes(emp_id: str):
    try:
        response = supabase.table("vibemeter").select("*").eq("emp_id", emp_id).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))