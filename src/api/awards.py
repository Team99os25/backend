from fastapi import APIRouter, HTTPException, status
from services.supabase import supabase
from models.schemas import Awards
from typing import List
from datetime import date

router = APIRouter()

@router.post("/", response_model=Awards)
async def create_award(award: Awards):
    try:
        response = supabase.table("awards").insert(award.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=List[Awards])
async def read_awards():
    try:
        response = supabase.table("awards").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{emp_id}", response_model=List[Awards])
async def read_employee_awards(emp_id: str):
    try:
        response = supabase.table("awards").select("*").eq("emp_id", emp_id).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/{emp_id}/{award_date}", response_model=Awards)
async def update_award(emp_id: str, award_date: date, award: Awards):
    try:
        response = supabase.table("awards").update(award.dict()).eq("emp_id", emp_id).eq("award_date", award_date).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Awards not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{emp_id}/{award_date}")
async def delete_award(emp_id: str, award_date: date):
    try:
        response = supabase.table("awards").delete().eq("emp_id", emp_id).eq("award_date", award_date).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Awards not found")
        return {"message": "Awards deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))