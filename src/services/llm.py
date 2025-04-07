from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from typing import List, Dict, Any, Optional
from models.schemas import InterventionDecision, ReasonAnalysis
import json


import os

load_dotenv()

class LLMService:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            temperature=0.2,
            model="gemini-2.0-flash",
            api_key=os.getenv("GOOGLE_API_KEY")
        )

    async def analyze_employee_data(self,
                                     vibe_meter_data: List[Dict],
                                     rewards_data: List[Dict],
                                     leave_data: List[Dict],
                                     performance_data: List[Dict]) -> InterventionDecision:
        """Analyze employee data to determine if intervention is needed"""
        parser = PydanticOutputParser(pydantic_object=InterventionDecision)

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an AI specialized in employee wellbeing analysis.
            Analyze the provided data about an employee and determine if an intervention is needed.
            Consider recent mood trends, rewards history, leave patterns, and performance.
            If there's a concerning pattern, especially in recent mood data, recommend intervention.
            Format your response according to the specified output format."""),
            ("human", """
            Vibe Meter Data (last 10 days): {vibe_meter_data}
            Rewards Data (last 1 year): {rewards_data}
            Leave Data (last 2 months): {leave_data}
            Performance Data (last review): {performance_data}

            {format_instructions}
            """)
        ])

        chain = prompt | self.llm | parser

        result = await chain.ainvoke({
            "vibe_meter_data": vibe_meter_data,
            "rewards_data": rewards_data,
            "leave_data": leave_data,
            "performance_data": performance_data,
            "format_instructions": parser.get_format_instructions()
        })

        return result

    async def generate_initial_message(self,
                                         employee_name: str,
                                         vibe_meter_data: List[Dict],
                                         probable_reasons: List[str]) -> str:
        """Generate an initial conversation message based on employee data"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are Emolyzer, an empathetic AI assistant focused on employee wellbeing.
            Your goal is to start a supportive conversation with an employee who may be experiencing challenges.
            Be warm, empathetic, and non-judgmental. Don't be too direct about the data you've seen.
            Create an opening message that gently invites the employee to share their feelings.
            Keep your message relatively short (2-3 paragraphs maximum)."""),
            ("human", """
            Employee Name: {employee_name}
            Recent Mood Data: {vibe_meter_data}
            Potential Concerns: {probable_reasons}

            Generate a warm, empathetic opening message to start a conversation with this employee.
            """)
        ])

        chain = prompt | self.llm

        result = await chain.ainvoke({
            "employee_name": employee_name,
            "vibe_meter_data": vibe_meter_data,
            "probable_reasons": probable_reasons
        })

        return result.content
    
    async def ask_followup_question(
        self,
        employee_name: str,
        current_response: Optional[str] = None,
        conversation_history: Optional[str] = None
    ) -> dict:
        """Determine whether to continue follow-up and generate appropriate response"""
        # Build context string
        context_parts = []
        if current_response:
            context_parts.append(f"Current response: {current_response}")
        if conversation_history:
            context_parts.append(f"Conversation history:\n{conversation_history}")
        context = "\n\n".join(context_parts) if context_parts else "No specific context"

        prompt_template = """You are Emolyzer, an expert at workplace conversations. Analyze this:

Employee: {employee_name}
Context: {context}

Respond in this exact JSON format ONLY (no other text, no code formatting):

{{
    "continue_followup": boolean,
    "response": string,
    "reason": string
}}

STRICT RULES:
1. "continue_followup": True ONLY IF:
   - The response was incomplete or unclear
   - You need exactly ONE more piece of information
   - This would be the FIRST follow-up for this topic
   - The employee seems willing to continue

2. NEVER set "continue_followup": True if:
   - This would be the 3rd follow-up on the same topic
   - The response was clear and complete
   - The employee seems disengaged or brief

3. "response" should be:
   - A single, concise follow-up question when continuing
   - A natural transition or closing statement when stopping

4. "reason" must explain your decision in 5-10 words

Example valid responses:
{{ "continue_followup": true, "response": "Could you clarify what you meant by that?", "reason": "Response needs clarification" }}
{{ "continue_followup": false, "response": "Thank you, that's helpful to know.", "reason": "Topic fully explored" }}
{{ "continue_followup": false, "response": "Let's move to another aspect of this.", "reason": "Maximum follow-ups reached" }}"""

        try:
            prompt = ChatPromptTemplate.from_template(prompt_template)
            chain = prompt | self.llm
            
            result = await chain.ainvoke({
                "employee_name": employee_name,
                "context": context
            })

            # Robust JSON extraction
            json_str = result.content.strip()
            
            # Remove any code formatting markers
            json_str = json_str.replace('```json', '').replace('```', '').strip()
            
            # Handle cases where LLM adds explanations before/after JSON
            if '{' in json_str and '}' in json_str:
                json_str = json_str[json_str.find('{'):json_str.rfind('}')+1]
            
            # Parse with validation
            response = json.loads(json_str)
            
            # Validate response structure
            if not all(key in response for key in ["continue_followup", "response", "reason"]):
                raise ValueError("Missing required fields in LLM response")
                
            if not isinstance(response["continue_followup"], bool):
                raise ValueError("continue_followup must be boolean")
                
            return {
                "continue_followup": response["continue_followup"],
                "response": str(response["response"]),
                "reason": str(response["reason"])
            }
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse LLM response: {json_str}. Error: {str(e)}")
            return {
                "continue_followup": False,
                "response": "Let's move on to another topic.",
                "reason": "System processing error"
            }
        except Exception as e:
            print(f"LLM processing error: {str(e)}")
            return {
                "continue_followup": False,
                "response": "I appreciate your input. Let's continue.",
                "reason": "System processing error"
            }











    async def generate_session_summary(self, conversation_history: List[Dict],
                                         identified_reason: str) -> str:
        """Generate a summary of the conversation for HR review"""

        # Format conversation history into a readable string
        formatted_history = "\n".join([
            f"{msg['sent_by']}: {msg['message']}" for msg in conversation_history
        ])

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an AI specialized in analyzing employee wellbeing conversations.
            Create a concise, professional summary of the conversation for HR review.
            Focus on key points, the identified core issue, and recommended next steps.
            Be objective and respect the employee's privacy while providing necessary context.
            Keep the summary under 300 words."""),
            ("human", """
            Conversation History:
            {conversation_history}

            Identified Core Reason: {identified_reason}

            Please generate a professional summary for HR review.
            """)
        ])

        chain = prompt | self.llm

        result = await chain.ainvoke({
            "conversation_history": formatted_history,
            "identified_reason": identified_reason
        })

        return result.content
