from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from services.supabase import supabase
from typing import List
from models.schemas import VibeMeter, SessionResponse
router = APIRouter()

@router.post("/submit", response_model=SessionResponse)
async def submit_vibe_meter(submission: VibeMeter):
    """Submit vibe meter data and determine if intervention is needed"""
    try:
        vibe_entry = VibeMeter(
            created_at=datetime.utcnow(),
            emp_id=submission.emp_id,
            mood=submission.mood,
            scale=submission.scale
        )
        
        await  supabase.table("vibemeter").insert(vibe_entry.dict()).execute()
        
        # RECONSIDER ---------------------------------------------------------------
        
        # Check threshold for intervention
        # Lower scores indicate worse mood, adjust threshold as needed
        if submission.scale <= 3:  
            # Create a new session if intervention is needed
            result = await conversation_service.create_session(submission.emp_id)
            return result
        else:
            return {"intervention_needed": False, "message": "No intervention needed at this time."}
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing vibe meter submission: {str(e)}"
        )


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