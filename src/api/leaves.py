from fastapi import APIRouter, HTTPException, status, Depends
from api.common import get_employee_id
from services.supabase import supabase
from models.schemas import Leaves
from typing import List
from datetime import date

router = APIRouter()

@router.post("/", response_model=Leaves)
async def create_leave(leave: Leaves):
    try:
        response = supabase.table("leave_records").insert(leave.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=List[Leaves])
async def read_leaves():
    try:
        response = supabase.table("leave_records").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/employee", response_model=List[Leaves])
async def read_employee_leaves(emp_id: str = Depends(get_employee_id)):
    try:
        response = supabase.table("leave_records").select("*").eq("emp_id", emp_id).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/employee/{leave_start_date}", response_model=Leaves)
async def update_leave(  leave_start_date: date, leave: Leaves, emp_id: str = Depends(get_employee_id)):
    try:
        response = supabase.table("leave_records").update(leave.dict()).eq("emp_id", emp_id).eq("leave_start_date", leave_start_date).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave record not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/employee/{leave_start_date}")
async def delete_leave(  leave_start_date: date, emp_id: str = Depends(get_employee_id)):
    try:
        response = supabase.table("leave_records").delete().eq("emp_id", emp_id).eq("leave_start_date", leave_start_date).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave record not found")
        return {"message": "Leave record deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))