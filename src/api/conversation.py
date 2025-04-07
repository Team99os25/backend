from fastapi import APIRouter, HTTPException, status,Request, Depends
from api.common import get_employee_id
from services.supabase import supabase
from datetime import datetime
from services.llm import LLMService
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
llm_service = LLMService()

async def _insert_conversation(
    session_id: str,
    emp_id: str,
    message: str,
    sender: str,
    timestamp: str
) -> Optional[Dict[str, Any]]:
    """Helper function to insert conversation records"""
    response = supabase.table("conversations").insert({
        "session_id": session_id,
        "emp_id": emp_id,
        "created_at": timestamp,
        "sent_by": sender,
        "conversation": message
    }).execute()
    
    return response.data[0] if response.data else None

async def _get_probable_reasons(emp_id: str, session_id: str) -> Dict[str, Any]:
    """Fetch probable reasons for a session"""
    reasons_data = supabase.table("probable_reasons") \
        .select("id, reasons") \
        .eq("emp_id", emp_id) \
        .eq("session_id", session_id) \
        .single() \
        .execute()
    
    if not reasons_data.data:
        raise HTTPException(
            status_code=404,
            detail="No probable reasons found for this session"
        )
    return reasons_data.data

async def _update_reasons(reason_id: str, reasons: list) -> None:
    """Update reasons in database"""
    update_result = supabase.table("probable_reasons").update({
        "reasons": reasons
    }).eq("id", reason_id).execute()
    
    if not update_result.data:
        raise HTTPException(
            status_code=500,
            detail="Failed to update probable reasons"
        )

async def _update_session_status(session_id: str, status: str) -> None:
    """Helper function to update the status of a session in the database."""
    response = supabase.table("sessions").update({
        "status": status,
        "ended_at": datetime.utcnow().isoformat()
    }).eq("id", session_id).execute()

    if not response.data:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update session status to {status}."
        )
    
@router.post("/{session_id}")
async def follow_up(req: Request, session_id: str ,emp_id: str = Depends(get_employee_id)) -> Dict[str, Any]:
    try:
        body = await req.json()
        text = body.get("text")
        current_time = datetime.utcnow().isoformat()

        if not emp_id:
            raise HTTPException(
                status_code=400,
                detail="Employee ID (emp_id) is required."
            )
        
        probable_reason = await _get_probable_reasons(emp_id, session_id)
        reasons = probable_reason.get("reasons", [])

        next_reason = next((r for r in reasons if not r.get("asked")), None)

        # Handle case when all questions have been asked
        if not next_reason:
            user_message = None
            if text:
                user_message = await _insert_conversation(
                    session_id, emp_id, text, "user", current_time
                )
            
            ai_message = await _insert_conversation(
                session_id, emp_id, "Thank you for your input.", "ai", current_time
            )
            
            await _update_session_status(session_id, "completed")

            return {
                "user_message": {
                    "text": text,
                    "created_at": current_time,
                    "sent_by": "user",
                    "id": user_message.get("id") if user_message else None
                } if text else None,
                "ai_message": {
                    "text": "Thank you for your input.",
                    "created_at": current_time,
                    "sent_by": "ai",
                    "id": ai_message.get("id")
                },
                "status": "completed"
            }

        follow_up_question = await llm_service.ask_followup_question(
            employee_name=emp_id,
            reason=next_reason.get("reason", "").replace('"', '').replace("'", "")
        )


        for r in reasons:
            if r.get("reason") == next_reason.get("reason"):
                r["asked"] = True

        await _update_reasons(probable_reason["id"], reasons)

        user_message = None
        if text:
            user_message = await _insert_conversation(
                session_id, emp_id, text, "user", current_time
            )
        
        ai_message = await _insert_conversation(
            session_id, emp_id, follow_up_question, "ai", current_time
        )

        return {
            "user_message": {
                "text": text,
                "created_at": current_time,
                "sent_by": "user",
                "id": user_message.get("id") if user_message else None
            } if text else None,
            "ai_message": {
                "text": follow_up_question,
                "created_at": current_time,
                "sent_by": "ai",
                "id": ai_message.get("id")
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
    





@router.get("/{session_id}")
async def get_conversation( session_id: str, emp_id: str = Depends(get_employee_id)) -> Dict[str, Any]:
    try:
        logger.info(f"Fetching conversations for emp_id: {emp_id}, session_id: {session_id}")
        
        if not all([emp_id, session_id]) or not all(isinstance(x, str) for x in [emp_id, session_id]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid input parameters"
            )

        try:
            response = supabase.table("conversations") \
                .select("*") \
                .eq("session_id", session_id) \
                .eq("emp_id", emp_id) \
                .execute()
        except Exception as db_error:
            logger.error(f"Database operation failed: {str(db_error)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service temporarily unavailable"
            )

        if hasattr(response, 'error') and response.error:
            logger.error(f"Supabase error: {response.error.message}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Database query failed"
            )
        
        if not response.data:
            logger.debug("No conversations found")
            return {"conversations": []}

        required_fields = {"id", "session_id", "emp_id", "created_at", "sent_by", "conversation"}
        if not all(required_fields.issubset(conv.keys()) for conv in response.data):
            logger.error("Malformed conversation data received")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Data integrity error"
            )

        logger.info(f"Returning {len(response.data)} conversation records")
        return {"conversations": response.data}

    except HTTPException:
        raise
    except Exception as e:
        logger.critical(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )