from pydantic import BaseModel
from uuid import UUID
from datetime import date
from typing import Optional


class EmployeeCreate(BaseModel):
    department_id: UUID
    full_name: str
    email: str
    position: str
    hire_date: date


class EmployeeResponse(BaseModel):
    id: UUID
    full_name: str
    email: str
    position: str
    hire_date: date
    department_id: UUID
    is_active: bool

    class Config:
        from_attributes = True


# backend/app/schemas/department.py
from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class DepartmentCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None


class DepartmentResponse(BaseModel):
    id: UUID
    name: str
    code: str

    class Config:
        from_attributes = True

