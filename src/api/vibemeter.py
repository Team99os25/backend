from fastapi import APIRouter, HTTPException, status, Request
from datetime import datetime
from services.supabase import supabase
from services.llm import LLMService
import uuid

router = APIRouter()

llm_service = LLMService()

@router.post("/")
async def new_vibe(req: Request):
    """Submit vibe meter data and determine if intervention is needed"""
    try:
        body = await req.json()

        emp_id = body.get("emp_id")
        mood = body.get("mood")
        scale = body.get("scale")

        if not all([emp_id, mood, scale]):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Missing required fields: emp_id, mood, scale"
            )

        # Get today's date in UTC
        today = datetime.utcnow().date().isoformat()

        # Check for existing submission today
        existing = (
            supabase.table("vibemeter")
            .select("created_at")
            .eq("emp_id", emp_id)
            .gte("created_at", f"{today}T00:00:00Z")
            .lte("created_at", f"{today}T23:59:59Z")
            .execute()
        ).data

        if existing:
            return {
                "status": "duplicate",
                "message": "Vibe already submitted for today."
            }

        # Save new VibeMeter entry
        vibe_entry = {
            "created_at": datetime.utcnow().isoformat(),
            "emp_id": emp_id,
            "mood": mood,
            "scale": scale
        }

        supabase.table("vibemeter").insert(vibe_entry).execute()

        # Fetch data for analysis
        vibe_data = (
            supabase.table("vibemeter")
            .select("*")
            .eq("emp_id", emp_id)
            .order("created_at", desc=True)
            .limit(10)
            .execute()
        ).data

        rewards_data = (
            supabase.table("awards")
            .select("*")
            .eq("emp_id", emp_id)
            .execute()
        ).data

        leave_data = (
            supabase.table("leaves")
            .select("*")
            .eq("emp_id", emp_id)
            .execute()
        ).data

        performance_data = (
            supabase.table("performance_reviews")
            .select("*")
            .eq("emp_id", emp_id)
            # .order("review_date", desc=True)
            .limit(1)
            .execute()
        ).data

        # LLM Analysis
        decision = await llm_service.analyze_employee_data(
            vibe_meter_data=vibe_data,
            rewards_data=rewards_data,
            leave_data=leave_data,
            performance_data=performance_data
        )
        if decision.intervention_needed:
            initial_conversation = await llm_service.generate_initial_message(
                employee_name=emp_id,
                vibe_meter_data=vibe_data,
                probable_reasons=decision.reasons
            )
             
            session = {
               "id": str(uuid.uuid4()), 
                "emp_id": emp_id,
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
                "emp_id": emp_id,
                "reasons": reasons_json
            }).execute()

            return {
                "intervention_needed": True,
                "session_id": session_id,
                "emp_id": emp_id,
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
