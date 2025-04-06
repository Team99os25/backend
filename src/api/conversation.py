from fastapi import APIRouter, HTTPException, status

from services.supabase import supabase

from services.llm_service import LLMService
from services.data_service import DataService
from services.conversation_service import ConversationService

from models.schemas import MessageResponse, MessageSubmission

router = APIRouter()

# Initialize services
llm_service = LLMService()
data_service = DataService()
conversation_service = ConversationService(llm_service, data_service)


@router.post("{emp_id}/{session_id}", response_model=MessageResponse)
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

@router.get("/history/{emp_id}/{session_id}")
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