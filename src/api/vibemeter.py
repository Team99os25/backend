from fastapi import APIRouter, HTTPException, status, Depends, Cookie
from services.supabase import supabase
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os
from typing import Optional
from services.llm import LLMService
import uuid

router = APIRouter()

llm_service = LLMService()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

class VibeData(BaseModel):
    mood: str
    scale: int

async def get_employee_id(auth_token: str = Cookie(None)):
    if not auth_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Not authenticated"
        )
    
    try:
        payload = jwt.decode(auth_token, SECRET_KEY, algorithms=[ALGORITHM])
        print(payload)
        employee_id = payload.get("sub")
        
        if employee_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        return employee_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@router.get("/check")
async def check_should_submit(employee_id: str = Depends(get_employee_id)):
    try:
        result = supabase.table("vibemeter")\
            .select("created_at")\
            .eq("emp_id", employee_id)\
            .order("created_at", desc=True)\
            .limit(1)\
            .execute()
        
        should_submit = True
        
        if result.data and len(result.data) > 0:
            last_submission = datetime.fromisoformat(result.data[0]["created_at"].replace("Z", "+00:00"))
            today = datetime.utcnow()
            
            days_difference = (today - last_submission).days
            
            should_submit = days_difference >= 2
        
        return {"should_submit": should_submit}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking vibe status: {str(e)}"
        )

@router.post("/submit")
async def submit_vibe(vibe_data: VibeData, employee_id: str = Depends(get_employee_id)):
    try:
        now = datetime.utcnow().isoformat()
        
        insert_data = {
            "emp_id": employee_id,
            "mood": vibe_data.mood,
            "scale": vibe_data.scale,
            "created_at": now
        }
        
        supabase.table("vibemeter").insert(insert_data).execute()


        result = supabase.table("vibemeter")\
            .select("mood")\
            .eq("emp_id", employee_id)\
            .order("created_at", desc=True)\
            .limit(3)\
            .execute()
        
        intervention_required = True
        
        if result.data:
            for entry in result.data:
                if entry["mood"] not in ["Angry", "Sad"]:
                    intervention_required = False
                    break
                
        if not intervention_required:
            return {
                "intervention_required": False,
                "message": "No intervention needed at this time."
            }
        
        vibe_data = (
            supabase.table("vibemeter")
            .select("*")
            .eq("emp_id", employee_id)
            .order("created_at", desc=True)
            .limit(10)
            .execute()
        ).data

        rewards_data = (
            supabase.table("awards")
            .select("*")
            .eq("emp_id", employee_id)
            .execute()
        ).data

        leave_data = (
            supabase.table("leaves")
            .select("*")
            .eq("emp_id", employee_id)
            .execute()
        ).data

        performance_data = (
            supabase.table("performance_reviews")
            .select("*")
            .eq("emp_id", employee_id)
            .limit(1)
            .execute()
        ).data

        decision = await llm_service.analyze_employee_data(
            vibe_meter_data=vibe_data,
            rewards_data=rewards_data,
            leave_data=leave_data,
            performance_data=performance_data
        )
        if decision.intervention_needed:
            initial_conversation = await llm_service.generate_initial_message(
                employee_name=employee_id,
                vibe_meter_data=vibe_data,
                probable_reasons=decision.reasons
            )
             
            session = {
               "id": str(uuid.uuid4()), 
                "emp_id": employee_id,
                "started_at": datetime.utcnow().isoformat(),
                "title": "Employee Wellbeing Intervention",
                "status": "active",
                "confidence_score": decision.confidence_score,
                "summary": ", ".join(decision.reasons),
                "initial_conversation": initial_conversation
            }

            session_response = supabase.table("sessions").insert(session).execute()
            session_id = session_response.data[0]["id"]


            reasons_json = [{"reason": r, "asked": False} for r in decision.reasons]

            supabase.table("probable_reasons").insert({
                "session_id": session_id,
                "emp_id": employee_id,
                "reasons": reasons_json
            }).execute()

            return {
                "intervention_needed": True,
                "session_id": session_id,
                "emp_id": employee_id,
                "message": "Intervention session started.",
                "initial_conversation": initial_conversation,
            }
        else:
            return {
                "intervention_needed": False,
                "message": "No intervention needed at this time.",
                "confidence_score": decision.confidence_score,
                "reasons": decision.reasons
            }
        
    except HTTPException as http_exc:
        print(f"[ERROR] HTTP Exception: {http_exc.detail}")
        raise http_exc
    except ValueError as ve:
        print(f"[ERROR] Value Error: {ve}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid input data: {str(ve)}"
        )
    except TypeError as te:
        print(f"[ERROR] Type Error: {te}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Type error in input data: {str(te)}"
        )
    except Exception as e:
        print(f"[ERROR] Vibe submission failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing vibe meter submission: {str(e)}"
        )
