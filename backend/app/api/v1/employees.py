import math
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.api.deps import get_db
from app.infrastructure.database.models.employee import Employee

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("/")
async def list_employees(
    department_id: UUID | None = Query(None),
    is_active: bool = Query(True),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * size
    conditions = [Employee.is_active == is_active]
    if department_id:
        conditions.append(Employee.department_id == department_id)

    count_result = await db.execute(
        select(func.count()).select_from(Employee).where(and_(*conditions))
    )
    total = count_result.scalar_one()

    result = await db.execute(
        select(Employee)
        .options(selectinload(Employee.department))
        .where(and_(*conditions))
        .offset(offset)
        .limit(size)
        .order_by(Employee.full_name)
    )
    employees = result.scalars().all()

    return {
        "items": [
            {
                "id": str(e.id),
                "full_name": e.full_name,
                "email": e.email,
                "position": e.position,
                "hire_date": str(e.hire_date),
                "is_active": e.is_active,
                "department_id": str(e.department_id),
                "department_name": e.department.name if e.department else None,
            }
            for e in employees
        ],
        "total": total,
        "page": page,
        "size": size,
        "pages": math.ceil(total / size) if size > 0 else 0,
    }


@router.get("/{employee_id}")
async def get_employee(employee_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Employee)
        .options(selectinload(Employee.department))
        .where(Employee.id == employee_id)
    )
    employee = result.scalar_one_or_none()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    return {
        "id": str(employee.id),
        "full_name": employee.full_name,
        "email": employee.email,
        "position": employee.position,
        "hire_date": str(employee.hire_date),
        "department_id": str(employee.department_id),
        "department_name": employee.department.name,
    }


@router.post("/", status_code=201)
async def create_employee(data: dict, db: AsyncSession = Depends(get_db)):
    employee = Employee(
        department_id=UUID(data["department_id"]),
        full_name=data["full_name"],
        email=data["email"],
        position=data["position"],
        hire_date=date.fromisoformat(data["hire_date"]),
    )
    db.add(employee)
    await db.commit()
    await db.refresh(employee)
    return {"id": str(employee.id), "full_name": employee.full_name}

