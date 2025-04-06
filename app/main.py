import sys
import os
from pathlib import Path

# Add the project root directory to Python path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
# from app.api.middlewares.auth import AuthMiddleware
# from app.api.middlewares.logging import LoggingMiddleware
from dotenv import load_dotenv

load_dotenv()

def create_application() -> FastAPI:
    application = FastAPI(
        title="Emolyzer API",
        description="Employee well-being analysis and support system",
        version="0.1.0",
    )
    
    # Set up CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Update for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add custom middlewares
    # application.add_middleware(LoggingMiddleware)
    # application.add_middleware(AuthMiddleware)
    
    # Include API router
    application.include_router(api_router, prefix="/api")
    
    return application

app = create_application()

@app.get("/", tags=["Root"])
async def root():
    """Health check endpoint"""
    return {"message": "API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
