from datetime import date
from uuid import UUID
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, text
import logging

from app.infrastructure.database.models.rating import RatingSnapshot
from app.infrastructure.cache.rating_cache import RatingCacheService

logger = logging.getLogger(__name__)


class SnapshotService:

    def __init__(self, session: AsyncSession, cache: RatingCacheService):
        self.session = session
        self.cache = cache

    async def build_snapshot(self, period: date) -> dict:
        logger.info(f"Building snapshot for {period}")

        # Получаем взвешенные баллы через SQL
        sql = text("""
            SELECT
                e.id as employee_id,
                e.full_name,
                e.department_id,
                d.name as department_name,
                SUM(re.score * rm.weight) / NULLIF(SUM(rm.weight), 0) as total_score,
                COUNT(re.id) as entry_count
            FROM employees e
            JOIN departments d ON e.department_id = d.id
            JOIN rating_entries re ON re.employee_id = e.id
            JOIN rating_metrics rm ON re.metric_id = rm.id
            WHERE re.period = :period
              AND e.is_active = true
            GROUP BY e.id, e.full_name, e.department_id, d.name
        """)

        result = await self.session.execute(sql, {"period": period})
        rows = result.mappings().all()

        if not rows:
            logger.warning(f"No data for period {period}")
            return {"status": "no_data", "period": str(period)}

        # Считаем ранги
        sorted_rows = sorted(rows, key=lambda r: float(r["total_score"] or 0), reverse=True)
        total_count = len(sorted_rows)

        # Ранги по отделам
        dept_counters: dict = {}
        for row in sorted_rows:
            dept_id = str(row["department_id"])
            dept_counters[dept_id] = dept_counters.get(dept_id, 0) + 1

        dept_rank_tracker: dict = {}

        # Получаем предыдущий снимок
        from dateutil.relativedelta import relativedelta
        prev_period = (period.replace(day=1) - relativedelta(months=1))
        prev_result = await self.session.execute(
            select(RatingSnapshot).where(RatingSnapshot.period == prev_period)
        )
        prev_snapshots = {s.employee_id: s for s in prev_result.scalars().all()}

        # Удаляем старый снимок
        await self.session.execute(
            delete(RatingSnapshot).where(RatingSnapshot.period == period)
        )

        # Сохраняем новый
        for rank, row in enumerate(sorted_rows, start=1):
            emp_id = row["employee_id"]
            dept_id = str(row["department_id"])

            dept_rank_tracker[dept_id] = dept_rank_tracker.get(dept_id, 0) + 1
            dept_rank = dept_rank_tracker[dept_id]

            percentile = round((1 - (rank - 1) / total_count) * 100, 2)

            prev = prev_snapshots.get(emp_id)
            delta_score = None
            delta_rank = None
            if prev:
                delta_score = Decimal(str(row["total_score"])) - prev.total_score
                delta_rank = prev.rank - rank

            snapshot = RatingSnapshot(
                employee_id=emp_id,
                period=period,
                total_score=Decimal(str(round(float(row["total_score"]), 3))),
                rank=rank,
                department_rank=dept_rank,
                percentile=Decimal(str(percentile)),
                delta_score=delta_score,
                delta_rank=delta_rank,
            )
            self.session.add(snapshot)

        await self.session.commit()
        await self.cache.invalidate_period(period)

        logger.info(f"Snapshot built: {total_count} employees for {period}")
        return {
            "status": "success",
            "period": str(period),
            "employee_count": total_count,
        }

