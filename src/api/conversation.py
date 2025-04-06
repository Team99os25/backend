from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from services.llm_service import LLMService
from services.data_service import DataService
from services.conversation_service import ConversationService
from models.schemas import VibeMeter, SessionResponse, VibeMeterSubmission, MessageResponse, MessageSubmission

router = APIRouter()

@router.get("/")
async def get_conversations():
    """Get all conversations."""
    return {"message": "Get all conversations endpoint"}

# Initialize services
llm_service = LLMService()
data_service = DataService()
conversation_service = ConversationService(llm_service, data_service)

# Routes
@router.post("/vibemeter/submit", response_model=SessionResponse)
async def submit_vibe_meter(submission: VibeMeterSubmission):
    """Submit vibe meter data and determine if intervention is needed"""
    try:
        # Save the vibe meter entry
        vibe_entry = VibeMeter(
            created_at=datetime.utcnow(),
            emp_id=submission.emp_id,
            mood=submission.mood,
            scale=submission.scale
        )
        
        await data_service.supabase.table("vibemeter").insert(vibe_entry.dict()).execute()
        
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

@router.post("/conversation/{session_id}/message", response_model=MessageResponse)
async def send_message(session_id: str, submission: MessageSubmission):
    """Send a message in a conversation and get AI response"""
    try:
        result = await conversation_service.process_message(session_id, submission.message)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )

@router.get("/conversation/{session_id}/history")
async def get_conversation_history(session_id: str):
    """Get the history of a conversation"""
    try:
        messages = await data_service.get_session_messages(session_id)
        session = await data_service.get_session(session_id)
        
        return {
            "session": session,
            "messages": messages
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving conversation history: {str(e)}"
        )

@router.get("/conversations/employee/{emp_id}")
async def get_employee_conversations(emp_id: str):
    """Get all conversations for an employee"""
    try:
        response = await data_service.supabase.table("sessions") \
            .select("*") \
            .eq("emp_id", emp_id) \
            .order("started_at", desc=True) \
            .execute()
        
        return response.data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving employee conversations: {str(e)}"
        )
