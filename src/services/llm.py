from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from typing import List, Dict, Any
from models.schemas import InterventionDecision, ReasonAnalysis

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
    

    async def ask_followup_question(self, employee_name: str, reason: str) -> str:
        """Generate a gentle follow-up question based on one of the reasons"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are Emolyzer, an empathetic AI assistant.
            Based on a concern about the employee's emotional state, you want to explore it gently.
            Craft a warm, supportive question to understand more about the reason.
            Don't mention that this reason was AI-generated or directly reference 'data'.
            Be a good listener."""),
            ("human", """
            Employee Name: {employee_name}
            Concern: {reason}

            Generate a supportive follow-up question to help the employee open up more about this.
            Keep it conversational and under 3 sentences.
            """)
        ])

        
        chain = prompt | self.llm
        result = await chain.ainvoke({
            "employee_name": employee_name,
            "reason": reason
        })

        return result.content

    async def process_conversation(self,
                                   employee_name: str,
                                   conversation_history: List[Dict],
                                   vibe_meter_data: List[Dict],
                                   probable_reasons: List[str]) -> Dict[str, Any]:
        """Process a conversation message and determine next steps"""
        parser = PydanticOutputParser(pydantic_object=ReasonAnalysis)

        # Format conversation history into a readable string
        formatted_history = "\n".join([
            f"{msg['sent_by']}: {msg['message']}" for msg in conversation_history
        ])

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are Emolyzer, an empathetic AI assistant focused on employee wellbeing.
            Your goal is to understand the core reasons behind an employee's emotional state.
            Be supportive, empathetic, and a good listener. Ask clarifying questions when needed.

            Analyze the conversation to determine:
            1. If you've identified the core reason for the employee's mood
            2. Your confidence level in this assessment
            3. Whether this issue should be escalated to HR
            4. What recommendations you would make

            Format your analysis according to the specified output format.

            Your response should have two parts:
            1. The structured analysis (in the specified format)
            2. Your next message to the employee
            """),
            ("human", """
            Employee Name: {employee_name}
            Recent Mood Data: {vibe_meter_data}
            Potential Concerns: {probable_reasons}

            Conversation History:
            {conversation_history}

            {format_instructions}
            """)
        ])

        chain = prompt | self.llm

        result = await chain.ainvoke({
            "employee_name": employee_name,
            "vibe_meter_data": vibe_meter_data,
            "probable_reasons": probable_reasons,
            "conversation_history": formatted_history,
            "format_instructions": parser.get_format_instructions()
        })

        # Extract the analysis part and the response part
        content = result.content

        # Parse the analysis
        try:
            analysis_text = content.split("```json")[1].split("```")[0]
            analysis = parser.parse(analysis_text)

            # Get the response part (everything after the JSON block)
            response_text = content.split("```")[2].strip()

            return {
                "analysis": analysis.dict(),
                "response": response_text
            }
        except Exception:
            # Fallback if parsing fails
            return {
                "analysis": {
                    "identified_reason": "Unknown",
                    "confidence_level": 0.0,
                    "should_escalate": True,
                    "recommendation": "Unable to determine recommendation, please review conversation manually."
                },
                "response": "I'm here to listen and support you. Could you tell me more about how you're feeling today?"
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
