from typing import  Dict, Any
from datetime import datetime
import uuid
from services.llm import LLMService
from services.data_service import DataService
from models.schemas import Sessions, Message

class ConversationService:
    def __init__(self, llm_service: LLMService, data_service: DataService):
        self.llm_service = llm_service
        self.data_service = data_service
    
    async def create_session(self, emp_id: str) -> Dict[str, Any]:
        """Create a new conversation session for an employee"""
        # Get employee data
        employee = await self.data_service.get_employee(emp_id)
        
        # Get historical data
        vibe_meter_data = await self.data_service.get_recent_vibes(emp_id, days=10)
        rewards_data = await self.data_service.get_recent_rewards(emp_id, days=365)
        leave_data = await self.data_service.get_recent_leaves(emp_id, days=60)
        performance_data = await self.data_service.get_recent_performance(emp_id)
        
        # Analyze data to determine if intervention is needed
        analysis = await self.llm_service.analyze_employee_data(
            vibe_meter_data, 
            rewards_data, 
            leave_data, 
            performance_data
        )
        
        # If intervention is not needed, return early
        if not analysis.intervention_needed:
            return {
                "intervention_needed": False,
                "message": "No intervention required at this time."
            }
        
        # Create a new session
        session_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        session = Sessions(
            id=session_id,
            started_at=now,
            ended_at=None,
            emp_id=emp_id,
            title=f"Wellness Check - {now.strftime('%Y-%m-%d')}",
            summary=None,
            status="active"
        )
        
        # Save session to database
        await self.data_service.create_session(session.dict())
        
        # Generate initial message
        initial_message = await self.llm_service.generate_initial_message(
            employee["name"],
            vibe_meter_data,
            analysis.reasons
        )
        
        # Save the initial message to database
        message = Message(
            created_at=now,
            session_id=session_id,
            sent_by="ai",
            message=initial_message
        )
        await self.data_service.create_message(message.dict())
        
        # Store probable reasons for future reference
        await self.data_service.store_probable_reasons(session_id, analysis.reasons)
        
        return {
            "intervention_needed": True,
            "session_id": session_id,
            "initial_message": initial_message
        }
    
    async def process_message(self, session_id: str, message_text: str) -> Dict[str, Any]:
        """Process a user message and generate a response"""
        # Save the user message
        now = datetime.utcnow()
        user_message = Message(
            created_at=now,
            session_id=session_id,
            sent_by="user",
            message=message_text
        )
        await self.data_service.create_message(user_message.dict())
        
        # Get the session details
        session = await self.data_service.get_session(session_id)
        
        # Get conversation history
        conversation_history = await self.data_service.get_session_messages(session_id)
        
        # Get employee data
        employee = await self.data_service.get_employee(session["emp_id"])
        
        # Get recent vibe meter data
        vibe_meter_data = await self.data_service.get_recent_vibes(session["emp_id"], days=10)
        
        # Get probable reasons
        probable_reasons = await self.data_service.get_probable_reasons(session_id)
        
        # Process the conversation with LLM
        result = await self.llm_service.process_conversation(
            employee["name"],
            conversation_history,
            vibe_meter_data,
            probable_reasons
        )
        
        # Save the AI response
        ai_message = Message(
            created_at=datetime.utcnow(),
            session_id=session_id,
            sent_by="ai",
            message=result["response"]
        )
        await self.data_service.create_message(ai_message.dict())
        
        # Check if we need to end the session
        analysis = result["analysis"]
        session_ended = False
        
        # If confident in reason or need to escalate, end the session
        if analysis["confidence_level"] > 0.7 or analysis["should_escalate"]:
            # Generate summary
            summary = await self.llm_service.generate_session_summary(
                conversation_history + [user_message.dict(), ai_message.dict()],
                analysis["identified_reason"]
            )
            
            # Update session
            session_update = Sessions(
                id=session_id,
                ended_at=datetime.utcnow(),
                summary=summary,
                status="escalated" if analysis["should_escalate"] else "completed"
            )
            await self.data_service.update_session(session_update.dict(exclude_unset=True))
            
            session_ended = True
        
        return {
            "response": result["response"],
            "session_ended": session_ended,
            "should_escalate": analysis["should_escalate"],
            "identified_reason": analysis["identified_reason"],
            "confidence_level": analysis["confidence_level"]
        }
