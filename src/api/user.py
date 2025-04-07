from fastapi import APIRouter, HTTPException, status, Depends
from api.common import get_employee_id
from services.supabase import supabase
from models.schemas import User
from typing import List
from passlib.context import CryptContext
from datetime import datetime

router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/", response_model=User)
async def create_user(user: User):
    try:
        user_dict = user.dict()
        # Hash the password before storing
        user_dict["password"] = pwd_context.hash(user_dict["password"])
        # Set timestamps
        now = datetime.utcnow()
        user_dict["created_at"] = now
        user_dict["updated_at"] = now
        
        response = supabase.table("user").insert(user_dict).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=List[User])
async def read_users():
    try:
        response = supabase.table("user").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{id}", response_model=User)
async def read_user(id: str):
    try:
        response = supabase.table("user").select("*").eq("id", id).single().execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/{id}", response_model=User)
async def update_user(id: str, user: User):
    try:
        user_dict = user.dict(exclude_unset=True)
        # Update timestamp
        user_dict["updated_at"] = datetime.utcnow()
        # Hash password if it's being updated
        if "password" in user_dict:
            user_dict["password"] = pwd_context.hash(user_dict["password"])
        
        response = supabase.table("user").update(user_dict).eq("id", id).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{id}")
async def delete_user(id: str):
    try:
        response = supabase.table("user").delete().eq("id", id).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))