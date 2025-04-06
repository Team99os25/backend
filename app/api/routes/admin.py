from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/")
async def admin_dashboard():
    """Admin dashboard endpoint."""
    return {"message": "Admin dashboard endpoint"}
