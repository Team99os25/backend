from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/")
async def get_reports():
    """Get all reports."""
    return {"message": "Get all reports endpoint"}
