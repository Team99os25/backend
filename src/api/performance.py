from fastapi import APIRouter, HTTPException, status, Depends
from api.common import get_employee_id
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

@router.get("/employee", response_model=List[PerformanceReview])
async def read_employee_performances(emp_id: str = Depends(get_employee_id)):
    try:
        response = supabase.table("performance_reviews").select("*").eq("emp_id", emp_id).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/employee/{review_period}", response_model=PerformanceReview)
async def update_performance(  review_period: str, performance: PerformanceReview, emp_id: str = Depends(get_employee_id)):
    try:
        response = supabase.table("performance_reviews").update(performance.dict()).eq("emp_id", emp_id).eq("review_period", review_period).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Performance review not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/employee/{review_period}")
async def delete_performance(  review_period: str , emp_id: str = Depends(get_employee_id)):
    try:
        response = supabase.table("performance_reviews").delete().eq("emp_id", emp_id).eq("review_period", review_period).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Performance review not found")
        return {"message": "Performance review deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))