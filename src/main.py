from fastapi import FastAPI
from dotenv import load_dotenv
import os

load_dotenv()
APP_NAME = os.getenv("APP_NAME")
FRONTEND_URL = os.getenv('FRONTEND_URL')

# Import routers
from api.activity import router as activity_router
from api.awards import router as awards_router
from api.leaves import router as leave_router
from api.performance import router as performance_router
from api.vibemeter import router as vibemeter_router
from api.messages import router as messages_router
from api.sessions import router as sessions_router
from api.user import router as user_router
from api.conversation import router as conversation_router
from api.auth import router as auth_router
from api.hr import router as hr_router
from api.summary import router as summary_router
app = FastAPI(title=APP_NAME)

# Register routers
app.include_router(activity_router, prefix="/activity", tags=["Activity"])
app.include_router(awards_router, prefix="/awards", tags=["Awards"])
app.include_router(leave_router, prefix="/leave", tags=["Leave"])
app.include_router(performance_router, prefix="/performance", tags=["Performance"])
app.include_router(vibemeter_router, prefix="/vibemeter", tags=["VibeMeter"])
app.include_router(messages_router, prefix="/messages", tags=["Messages"])
app.include_router(sessions_router, prefix="/sessions", tags=["Sessions"])
app.include_router(user_router, prefix="/user", tags=["User"])
app.include_router(conversation_router, prefix="/conversation", tags=["Conversation"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(hr_router, prefix="/hr", tags=["Hr"])
app.include_router(summary_router, prefix="/summary", tags=["Summary"])

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:3000"],   
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "status": "Server is running",
        "message": f"Welcome to {APP_NAME}!",
    }