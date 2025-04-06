from fastapi import APIRouter, HTTPException, status
from services.supabase import supabase
from models.schemas import LeaveRecord
from typing import List
from datetime import date

router = APIRouter()

@router.post("/", response_model=LeaveRecord)
async def create_leave(leave: LeaveRecord):
    try:
        response = supabase.table("leave_records").insert(leave.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=List[LeaveRecord])
async def read_leaves():
    try:
        response = supabase.table("leave_records").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{emp_id}", response_model=List[LeaveRecord])
async def read_employee_leaves(emp_id: str):
    try:
        response = supabase.table("leave_records").select("*").eq("emp_id", emp_id).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/{emp_id}/{leave_start_date}", response_model=LeaveRecord)
async def update_leave(emp_id: str, leave_start_date: date, leave: LeaveRecord):
    try:
        response = supabase.table("leave_records").update(leave.dict()).eq("emp_id", emp_id).eq("leave_start_date", leave_start_date).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave record not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{emp_id}/{leave_start_date}")
async def delete_leave(emp_id: str, leave_start_date: date):
    try:
        response = supabase.table("leave_records").delete().eq("emp_id", emp_id).eq("leave_start_date", leave_start_date).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave record not found")
        return {"message": "Leave record deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))