import pytest
from httpx import AsyncClient


class TestEmployeesAPI:
    
    @pytest.mark.asyncio
    async def test_get_employees_list(
        self,
        client: AsyncClient,
        sample_employee,
    ):
        """GET /employees возвращает список сотрудников"""
        response = await client.get("/api/v1/employees/")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1
    
    @pytest.mark.asyncio
    async def test_get_employees_filter_by_department(
        self,
        client: AsyncClient,
        sample_employee,
        sample_department,
    ):
        """Фильтрация сотрудников по отделу работает корректно"""
        response = await client.get(
            "/api/v1/employees/",
            params={"department_id": str(sample_department.id)},
        )
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert item["department_id"] == str(sample_department.id)
    
    @pytest.mark.asyncio
    async def test_pagination(self, client: AsyncClient, sample_employee):
        """Пагинация возвращает корректные метаданные"""
        response = await client.get(
            "/api/v1/employees/",
            params={"page": 1, "size": 5}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["size"] == 5
        assert "pages" in data
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self, client: AsyncClient):
        """Health check работает"""
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
