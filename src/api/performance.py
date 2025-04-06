from fastapi import APIRouter, HTTPException, status
from services.supabase import supabase
from models.schemas import PerformanceReview
from typing import List

router = APIRouter()

@router.post("/", response_model=PerformanceReview)
async def create_performance(performance: PerformanceReview):
    try:
        response = supabase.table("performance_reviews").insert(performance.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=List[PerformanceReview])
async def read_performances():
    try:
        response = supabase.table("performance_reviews").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{emp_id}", response_model=List[PerformanceReview])
async def read_employee_performances(emp_id: str):
    try:
        response = supabase.table("performance_reviews").select("*").eq("emp_id", emp_id).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/{emp_id}/{review_period}", response_model=PerformanceReview)
async def update_performance(emp_id: str, review_period: str, performance: PerformanceReview):
    try:
        response = supabase.table("performance_reviews").update(performance.dict()).eq("emp_id", emp_id).eq("review_period", review_period).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Performance review not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{emp_id}/{review_period}")
async def delete_performance(emp_id: str, review_period: str):
    try:
        response = supabase.table("performance_reviews").delete().eq("emp_id", emp_id).eq("review_period", review_period).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Performance review not found")
        return {"message": "Performance review deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))