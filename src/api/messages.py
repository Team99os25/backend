from fastapi import APIRouter, HTTPException, status, Depends
from api.common import get_employee_id
from services.supabase import supabase
from models.schemas import Message
from typing import List

router = APIRouter()

@router.post("/", response_model=Message)
async def create_message(message: Message):
    try:
        response = supabase.table("messages").insert(message.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=List[Message])
async def read_messages():
    try:
        response = supabase.table("messages").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{session_id}", response_model=List[Message])
async def read_session_messages(session_id: str):
    try:
        response = supabase.table("messages").select("*").eq("session_id", session_id).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
