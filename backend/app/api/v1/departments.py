from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db
from app.infrastructure.database.models.department import Department

router = APIRouter(prefix="/departments", tags=["departments"])


@router.get("/")
async def list_departments(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Department)
        .where(Department.is_active == True)
        .order_by(Department.name)
    )
    departments = result.scalars().all()
    return [
        {
            "id": str(d.id),
            "name": d.name,
            "code": d.code,
            "description": d.description,
        }
        for d in departments
    ]


@router.post("/", status_code=201)
async def create_department(data: dict, db: AsyncSession = Depends(get_db)):
    dept = Department(
        name=data["name"],
        code=data["code"],
        description=data.get("description"),
    )
    db.add(dept)
    await db.commit()
    await db.refresh(dept)
    return {"id": str(dept.id), "name": dept.name, "code": dept.code}

