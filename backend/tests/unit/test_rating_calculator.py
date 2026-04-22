import pytest
from decimal import Decimal
from datetime import date
from uuid import uuid4

from app.core.services.rating_calculator import (
    RatingCalculatorService,
    EmployeeScoreData,
)


class TestRatingCalculatorService:
    
    def setup_method(self):
        self.service = RatingCalculatorService()
    
    def test_validate_scores_valid_data(self):
        """Корректные данные проходят валидацию"""
        entries = [
            {
                "employee_id": str(uuid4()),
                "metric_id": str(uuid4()),
                "score": 7.5,
                "category": "quality",
            }
        ]
        valid, errors = self.service.validate_scores(entries)
        assert len(valid) == 1
        assert len(errors) == 0
    
    def test_validate_scores_invalid_score_range(self):
        """Баллы вне диапазона [0, 10] отклоняются"""
        entries = [
            {
                "employee_id": str(uuid4()),
                "metric_id": str(uuid4()),
                "score": 11.0,
                "category": "quality",
            }
        ]
        valid, errors = self.service.validate_scores(entries)
        assert len(valid) == 0
        assert len(errors) == 1
        assert "score must be in [0, 10]" in errors[0]
    
    def test_validate_scores_missing_employee_id(self):
        """Отсутствующий employee_id вызывает ошибку"""
        entries = [{"metric_id": str(uuid4()), "score": 5.0, "category": "quality"}]
        valid, errors = self.service.validate_scores(entries)
        assert len(valid) == 0
        assert any("employee_id is required" in e for e in errors)
    
    def test_compute_deltas_first_period(self):
        """Первый период не имеет дельт"""
        emp_id = uuid4()
        current = [
            {
                "employee_id": emp_id,
                "full_name": "John Doe",
                "department_id": uuid4(),
                "department_name": "Engineering",
                "total_score": Decimal("7.500"),
                "entry_count": 5,
                "global_rank": 1,
                "dept_rank": 1,
                "percentile": Decimal("95.00"),
            }
        ]
        snapshots = self.service.compute_deltas(current, {})
        assert snapshots[0]["delta_score"] is None
        assert snapshots[0]["delta_rank"] is None
    
    def test_compute_deltas_positive_improvement(self):
        """Рост рейтинга отражается в положительной дельте"""
        emp_id = uuid4()
        
        class PrevSnapshot:
            total_score = Decimal("6.000")
            rank = 3
        
        current = [
            {
                "employee_id": emp_id,
                "full_name": "Jane Smith",
                "department_id": uuid4(),
                "department_name": "HR",
                "total_score": Decimal("8.000"),
                "entry_count": 5,
                "global_rank": 1,
                "dept_rank": 1,
                "percentile": Decimal("99.00"),
            }
        ]
        snapshots = self.service.compute_deltas(current, {emp_id: PrevSnapshot()})
        assert snapshots[0]["delta_score"] == Decimal("2.000")
        assert snapshots[0]["delta_rank"] == 2  # 3 - 1 = +2 позиции
    
    def test_validate_scores_boundary_values(self):
        """Граничные значения 0 и 10 валидны"""
        entries = [
            {
                "employee_id": str(uuid4()),
                "metric_id": str(uuid4()),
                "score": 0.0,
                "category": "quality",
            },
            {
                "employee_id": str(uuid4()),
                "metric_id": str(uuid4()),
                "score": 10.0,
                "category": "quality",
            },
        ]
        valid, errors = self.service.validate_scores(entries)
        assert len(valid) == 2
        assert len(errors) == 0
    
    def test_validate_scores_mixed_data(self):
        """Смешанные данные: валидные и невалидные обрабатываются отдельно"""
        entries = [
            {
                "employee_id": str(uuid4()),
                "metric_id": str(uuid4()),
                "score": 5.0,
                "category": "quality",
            },
            {
                "employee_id": str(uuid4()),
                "metric_id": str(uuid4()),
                "score": -1.0,
                "category": "quality",
            },
        ]
        valid, errors = self.service.validate_scores(entries)
        assert len(valid) == 1
        assert len(errors) == 1


