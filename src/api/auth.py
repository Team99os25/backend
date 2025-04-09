from fastapi import APIRouter, HTTPException, status, Depends, Response, Cookie
from services.supabase import supabase
from models.schemas import User, LoginRequest
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os


router = APIRouter()

# JWT Settings
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

@router.post("/login")
async def login(response: Response, login_data: LoginRequest):
    # Get user from database
    result = supabase.table("user").select("*").eq("id", login_data.employee_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    user = result.data[0]
    
    # Check role
    if user["role"] != login_data.role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    # Verify password
    if not verify_password(login_data.password, user["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    # Create JWT token
    token = create_access_token({"sub": user["id"], "role": user["role"]})
    
    # Set JWT in cookie
    response.set_cookie(
        key="auth_token", 
        value=token, 
        httponly=True, 
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        secure=True,
        samesite="none",
        path="/",
        domain=os.getenv("DOMAIN").replace("https://", "").replace("http://", ""),
    )
    
    # Return user data
    return {
        "id": user["id"],
        "role": user["role"],
        "message": "Login successful",
    }

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("auth_token")
    return {"message": "Logged out successfully"}