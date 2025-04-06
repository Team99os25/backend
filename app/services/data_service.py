from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from app.api.db.base import SessionReason

load_dotenv()

class DataService:
    def __init__(self):
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
    
    async def get_employee(self, emp_id: str) -> Dict[str, Any]:
        """Get employee details by ID"""
        try:
            response = self.supabase.table("user").select("*").eq("id", emp_id).single().execute()
            return response.data
        except Exception as e:
            raise Exception(f"Error retrieving employee: {str(e)}")
    
    async def get_recent_vibes(self, emp_id: str, days: int = 10) -> List[Dict[str, Any]]:
        """Get recent vibe meter data for an employee"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            response = self.supabase.table("vibemeter") \
                .select("*") \
                .eq("emp_id", emp_id) \
                .gte("created_at", start_date.isoformat()) \
                .order("created_at", desc=True) \
                .execute()
            return response.data
        except Exception as e:
            raise Exception(f"Error retrieving vibe meter data: {str(e)}")
    
    async def get_recent_rewards(self, emp_id: str, days: int = 365) -> List[Dict[str, Any]]:
        """Get recent rewards data for an employee"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            response = self.supabase.table("awards") \
                .select("*") \
                .eq("emp_id", emp_id) \
                .gte("award_date", start_date.strftime("%Y-%m-%d")) \
                .order("award_date", desc=True) \
                .execute()
            return response.data
        except Exception as e:
            raise Exception(f"Error retrieving rewards data: {str(e)}")
    
    async def get_recent_leaves(self, emp_id: str, days: int = 60) -> List[Dict[str, Any]]:
        """Get recent leave data for an employee"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            response = self.supabase.table("leave_records") \
                .select("*") \
                .eq("emp_id", emp_id) \
                .gte("leave_start_date", start_date.strftime("%Y-%m-%d")) \
                .order("leave_start_date", desc=True) \
                .execute()
            return response.data
        except Exception as e:
            raise Exception(f"Error retrieving leave data: {str(e)}")
    
    async def get_recent_performance(self, emp_id: str) -> List[Dict[str, Any]]:
        """Get recent performance data for an employee"""
        try:
            response = self.supabase.table("performance_reviews") \
                .select("*") \
                .eq("emp_id", emp_id) \
                .order("review_period", desc=True) \
                .limit(1) \
                .execute()
            return response.data
        except Exception as e:
            raise Exception(f"Error retrieving performance data: {str(e)}")
    
    async def create_session(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new conversation session"""
        try:
            response = self.supabase.table("sessions").insert(session).execute()
            return response.data[0]
        except Exception as e:
            raise Exception(f"Error creating session: {str(e)}")
    
    async def update_session(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Update a conversation session"""
        try:
            response = self.supabase.table("sessions") \
                .update(session) \
                .eq("id", session["id"]) \
                .execute()
            return response.data[0]
        except Exception as e:
            raise Exception(f"Error updating session: {str(e)}")
    
    async def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get a conversation session by ID"""
        try:
            response = self.supabase.table("sessions") \
                .select("*") \
                .eq("id", session_id) \
                .single() \
                .execute()
            return response.data
        except Exception as e:
            raise Exception(f"Error retrieving session: {str(e)}")
    
    async def create_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new message in a conversation"""
        try:
            response = self.supabase.table("messages").insert(message).execute()
            return response.data[0]
        except Exception as e:
            raise Exception(f"Error creating message: {str(e)}")
    
    async def get_session_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all messages in a conversation session"""
        try:
            response = self.supabase.table("messages") \
                .select("*") \
                .eq("session_id", session_id) \
                .order("created_at", desc=False) \
                .execute()
            return response.data
        except Exception as e:
            raise Exception(f"Error retrieving messages: {str(e)}")
    
    async def store_probable_reasons(self, session_id: str, reasons: List[str]) -> None:
        """Store probable reasons for a session"""
        try:
            # Create a table to store reasons if it doesn't exist already
            reason_data = []
            for idx, reason in enumerate(reasons):
                reason_data.append(
                    SessionReason(
                        session_id=session_id,
                        reason=reason,
                        priority=idx + 1
                    ).dict(exclude={"id", "created_at"})
                )
            
            self.supabase.table("session_reasons").insert(reason_data).execute()
        except Exception as e:
            raise Exception(f"Error storing probable reasons: {str(e)}")
    
    async def get_probable_reasons(self, session_id: str) -> List[str]:
        """Get probable reasons for a session"""
        try:
            response = self.supabase.table("session_reasons") \
                .select("*") \
                .eq("session_id", session_id) \
                .order("priority", desc=False) \
                .execute()
            
            return [item["reason"] for item in response.data]
        except Exception as e:
            raise Exception(f"Error retrieving probable reasons: {str(e)}")
