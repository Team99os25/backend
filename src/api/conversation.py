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
        .select("id, interventions") \
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


async def _update_reasons(reason_id: str, interventions: list) -> None:
    """Update reasons in database"""
    update_result = supabase.table("probable_reasons").update({
        "interventions": interventions  # Changed from 'reasons' to 'interventions'
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
async def follow_up(req: Request, session_id: str, emp_id: str = Depends(get_employee_id)) -> Dict[str, Any]:
    try:
        body = await req.json()
        text = body.get("text")
        current_time = datetime.utcnow().isoformat()
        
        if not emp_id:
            raise HTTPException(status_code=400, detail="Employee ID (emp_id) is required.")
        
        # Get conversation history
        conv_history = supabase.table("conversations") \
            .select("conversation, sent_by, created_at") \
            .eq("emp_id", emp_id) \
            .eq("session_id", session_id) \
            .order("created_at") \
            .execute()

        history_text = "\n".join(
            f"{msg['sent_by']}: {msg['conversation']}" 
            for msg in conv_history.data
        ) if conv_history.data else "No conversation history yet"

        # Get interventions
        probable_reason = await _get_probable_reasons(emp_id, session_id)
        interventions = probable_reason.get("interventions", [])
        
        # Find current active and next reasons
        current_active_reason = next((r for r in interventions if r.get("active")), None)
        next_reason = next((r for r in interventions if not r.get("asked")), None)

        # End if no more reasons left
        if not next_reason and not current_active_reason:
            user_message = await _insert_conversation(session_id, emp_id, text, "user", current_time) if text else None
            ai_message = await _insert_conversation(session_id, emp_id, "Thank you for sharing. I appreciate your openness.", "ai", current_time)
            await _update_session_status(session_id, "completed")
            await _mark_all_interventions_asked(probable_reason["id"])
            return {
                "user_message": user_message,
                "ai_message": ai_message,
                "status": "completed"
            }

        # Get follow-up decision from LLM
        followup_result = await llm_service.ask_followup_question(
            employee_name=emp_id,
            current_response=text, 
            conversation_history=history_text
        )

        # Debug prints
        print(f"LLM follow-up decision: {followup_result}")
        print(f"Current active reason: {current_active_reason}")
        print(f"Next reason available: {next_reason}")

        # Determine AI response based on follow-up decision
        end_chat = False
        if not followup_result["continue_followup"]:
            # Mark current reason as complete if exists
            if current_active_reason:
                await _update_intervention_status(
                    probable_reason["id"], 
                    current_active_reason["reason"], 
                    asked=True, 
                    active=False
                )

            # Move to next reason if available
            if next_reason:
                await _update_intervention_status(
                    probable_reason["id"], 
                    next_reason["reason"], 
                    active=True
                )
                ai_response = next_reason.get("question", "Could you tell me more about this?")
                followup_result["response"] = ai_response
                followup_result["reason"] = "Moving to next reason"
            else:
                # No more reasons left - end chat
                ai_response = "Thank you for sharing. I appreciate your openness."
                followup_result["response"] = ai_response
                followup_result["reason"] = "All interventions completed"
                end_chat = True
                await _update_session_status(session_id, "completed")
                await _mark_all_interventions_asked(probable_reason["id"])
        else:
            # Continue with current reason using LLM's response
            ai_response = followup_result["response"]

        # Insert messages
        user_message = await _insert_conversation(session_id, emp_id, text, "user", current_time) if text else None
        ai_message = await _insert_conversation(session_id, emp_id, ai_response, "ai", current_time)

        return {
            "user_message": {
                "text": text,
                "created_at": current_time,
                "sent_by": "user",
                "id": user_message.get("id") if user_message else None
            } if text else None,
            "ai_message": {
                "text": ai_response,
                "created_at": current_time,
                "sent_by": "ai",
                "id": ai_message.get("id")
            },
            "status": "completed" if end_chat else "ongoing",
            "current_reason": current_active_reason.get("reason") if current_active_reason else None,
            "next_reason": next_reason.get("reason") if next_reason else None,
            "decision_reason": followup_result.get("reason", "")
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in follow_up endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred while processing your request.")


async def _update_intervention_status(
    reason_id: str,
    intervention_reason: str,
    asked: Optional[bool] = None,
    active: Optional[bool] = None
) -> None:
    """Update the status of a specific intervention by its reason text"""
    # Get current probable_reason record
    probable_reason = supabase.table("probable_reasons") \
        .select("*") \
        .eq("id", reason_id) \
        .single() \
        .execute() \
        .data
    
    # Update the specific intervention
    updated_interventions = []
    for intervention in probable_reason["interventions"]:
        if intervention["reason"] == intervention_reason:
            if asked is not None:
                intervention["asked"] = asked
            if active is not None:
                intervention["active"] = active
        updated_interventions.append(intervention)
    
    # Update the entire record
    supabase.table("probable_reasons") \
        .update({"interventions": updated_interventions}) \
        .eq("id", reason_id) \
        .execute()

async def _mark_all_interventions_asked(reason_id: str) -> None:
    """Mark all interventions as asked for a given reason"""
    probable_reason = supabase.table("probable_reasons") \
        .select("*") \
        .eq("id", reason_id) \
        .single() \
        .execute() \
        .data
    
    updated_interventions = []
    for intervention in probable_reason["interventions"]:
        intervention["asked"] = True
        intervention["active"] = False
        updated_interventions.append(intervention)
    
    supabase.table("probable_reasons") \
        .update({"interventions": updated_interventions}) \
        .eq("id", reason_id) \
        .execute()














@router.get("/{session_id}")
async def get_conversation( session_id: str, emp_id: str = Depends(get_employee_id)) -> Dict[str, Any]:
    try:
        print(f"Fetching conversations for emp_id: {emp_id}, session_id: {session_id}")
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