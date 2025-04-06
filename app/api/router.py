from fastapi import APIRouter
from app.api.routes import employee, conversation, admin, reports

api_router = APIRouter()
api_router.include_router(employee.router, prefix="/employees", tags=["employees"])
api_router.include_router(conversation.router, prefix="/conversations", tags=["conversations"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
