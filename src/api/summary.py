from fastapi import APIRouter, HTTPException, status, Depends
from api.common import get_employee_id
from services.supabase import supabase
from models.schemas import Sessions
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
from services.llm import LLMService

router = APIRouter()
llm_service = LLMService()

@router.post("/{session_id}/")
async def generate_summary(session_id: str, emp_id: str = Depends(get_employee_id)) -> Dict[str, Any]:
    try:
        print(f"Generating summary for session {session_id}, employee {emp_id}")
        
        conv_history = supabase.table("conversations") \
            .select("conversation, sent_by, created_at") \
            .eq("emp_id", emp_id) \
            .eq("session_id", session_id) \
            .order("created_at") \
            .execute()
        
        chat_history = "\n".join(
            f"{msg['sent_by']}: {msg['conversation']}" 
            for msg in conv_history.data
        ) if conv_history.data else "No conversation history"

        probable_reason = supabase.table("probable_reasons") \
            .select("*") \
            .eq("emp_id", emp_id) \
            .eq("session_id", session_id) \
            .single() \
            .execute()
        
        interventions = probable_reason.data.get("interventions", [])
        intervention_reasons = [intervention["reason"] for intervention in interventions]

        analysis = await llm_service.analyze_chats(
            intervention_reasons=intervention_reasons,
            chat_history=chat_history,
            employee_name=emp_id
        )

        summary_data = {
            "session_id": session_id,
            "employee_id": emp_id,
            "analysis_date": datetime.utcnow().isoformat(),
            "title" : analysis["title"],
            "conversation_summary": analysis["summary"],
            "identified_reason": analysis["identified_reason"],
            "vulnerability_score": analysis["vulnerability_score"],
            "escalation_required": analysis["escalation_required"],
        }

        try:
            # Update session with summary data
            update_data = {
                "title" : analysis["title"],
                "summary": analysis["summary"],
                "vulnerability_score": analysis["vulnerability_score"]["value"],
                "is_escalated": analysis["escalation_required"],
                "ended_at": datetime.utcnow().isoformat(),
                "status": "completed",
                "identified_reason": analysis["identified_reason"]
            }
            
            supabase.table("sessions") \
                .update(update_data) \
                .eq("id", session_id) \
                .eq("emp_id", emp_id) \
                .execute()
            
            
        except Exception as db_error:
            print(f"Database update failed: {str(db_error)}")

        print("Summary generated successfully:", summary_data)
        return summary_data

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating summary: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate summary: {str(e)}"
        )