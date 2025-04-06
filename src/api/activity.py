from fastapi import APIRouter, HTTPException, status
from services.supabase import supabase
from models.schemas import Activity
from typing import List
from datetime import date

router = APIRouter()

@router.post("/", response_model=Activity)
async def create_activity(activity: Activity):
    try:
        response = supabase.table("activity").insert(activity.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=List[Activity])
async def read_activities():
    try:
        response = supabase.table("activity").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{emp_id}", response_model=List[Activity])
async def read_employee_activities(emp_id: str):
    try:
        response = supabase.table("activity").select("*").eq("emp_id", emp_id).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/{emp_id}/{date_msg}", response_model=Activity)
async def update_activity(emp_id: str, date_msg: date, activity: Activity):
    try:
        response = supabase.table("activity").update(activity.dict()).eq("emp_id", emp_id).eq("date_msg", date_msg).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{emp_id}/{date_msg}")
async def delete_activity(emp_id: str, date_msg: date):
    try:
        response = supabase.table("activity").delete().eq("emp_id", emp_id).eq("date_msg", date_msg).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")
        return {"message": "Activity deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
