from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/")
async def get_employees():
    """Get all employees."""
    return {"message": "Get all employees endpoint"}

@router.get("/{employee_id}")
async def get_employee(employee_id: int):
    """Get employee by ID."""
    return {"message": f"Get employee with ID: {employee_id}"}
