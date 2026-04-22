import pytest
import pytest_asyncio
from decimal import Decimal
from datetime import date
from uuid import uuid4
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestRatingsAPI:
    
    @pytest.mark.asyncio
    async def test_create_rating_entry(
        self,
        client: AsyncClient,
        sample_employee,
        sample_metric,
    ):
        """POST /ratings создаёт запись рейтинга"""
        payload = {
            "employee_id": str(sample_employee.id),
            "metric_id": str(sample_metric.id),
            "period": "2024-01-01",
            "score": "8.50",
            "category": "quality",
            "comment": "Excellent code quality",
        }
        response = await client.post("/api/v1/ratings/", json=payload)
        assert response.status_code == 201
        data = response.json()
    
    @pytest.mark.asyncio
    async def test_create_rating_invalid_score(
        self,
        client: AsyncClient,
        sample_employee,
        sample_metric,
    ):
        """Невалидный балл возвращает 422"""
        payload = {
            "employee_id": str(sample_employee.id),
            "metric_id": str(sample_metric.id),
            "period": "2024-01-01",
            "score": "15.0",  # Выше максимума
            "category": "quality",
        }
        response = await client.post("/api/v1/ratings/", json=payload)
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_get_snapshot_not_found(self, client: AsyncClient):
        """Несуществующий снимок возвращает 404"""
        response = await client.get("/api/v1/ratings/snapshots/2020-01-01")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_import_csv_valid_file(
        self,
        client: AsyncClient,
        sample_employee,
        sample_metric,
    ):
        """Валидный CSV импортируется успешно"""
        csv_content = (
            f"employee_id,metric_id,score,category,period\n"
            f"{sample_employee.id},{sample_metric.id},7.5,quality,2024-02-01\n"
        ).encode("utf-8")
        
        response = await client.post(
            "/api/v1/ratings/import",
            params={"period": "2024-02-01"},
            files={"file": ("test.csv", csv_content, "text/csv")},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["total_rows"] == 1
        assert data["valid_rows"] == 1
        assert data["error_count"] == 0
    
    @pytest.mark.asyncio
    async def test_import_csv_wrong_extension(self, client: AsyncClient):
        """Файл без расширения .csv отклоняется"""
        response = await client.post(
            "/api/v1/ratings/import",
            params={"period": "2024-02-01"},
            files={"file": ("data.xlsx", b"binary data", "application/octet-stream")},
        )
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_get_employee_trends(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        sample_employee,
    ):
        """Тренд возвращает данные за N периодов"""
        from app.infrastructure.database.models.rating import RatingSnapshot
        
        # Создаём тестовые снимки
        for month in range(1, 4):
            snapshot = RatingSnapshot(
                employee_id=sample_employee.id,
                period=date(2024, month, 1),
                total_score=Decimal(f"{6 + month}.000"),
                rank=5 - month,
                department_rank=2,
                percentile=Decimal("75.00"),
            )
            db_session.add(snapshot)
        await db_session.flush()
        
        response = await client.get(
            "/api/v1/ratings/analytics/trends",
            params={"employee_id": str(sample_employee.id), "months": 6},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["employee_id"] == str(sample_employee.id)
        assert len(data["trend"]) == 3
        # Проверяем порядок (от раннего к позднему)
        scores = [t["total_score"] for t in data["trend"]]
        assert scores == sorted(scores)

