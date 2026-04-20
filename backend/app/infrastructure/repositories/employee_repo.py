from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database.models.employee import Employee
from .base import BaseRepository


class EmployeeRepository(BaseRepository[Employee]):
    def __init__(self, session: AsyncSession):
        super().__init__(Employee, session)

    async def get_by_email(self, email: str) -> Employee | None:
        result = await self.session.execute(
            select(Employee).where(Employee.email == email)
        )
        return result.scalar_one_or_none()

    async def get_active_by_department(
        self, department_id: UUID
    ) -> list[Employee]:
        result = await self.session.execute(
            select(Employee)
            .options(selectinload(Employee.department))
            .where(
                and_(
                    Employee.department_id == department_id,
                    Employee.is_active == True,
                )
            )
        )
        return result.scalars().all()

