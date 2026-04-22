import pytest
from uuid import uuid4

from app.core.services.rating_calculator import RatingCalculatorService


class TestRatingCalculatorService:
    def setup_method(self):
        self.service = RatingCalculatorService()

    def test_validate_scores_valid_data(self):
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
        assert errors == []

    def test_validate_scores_invalid_score_range(self):
        entries = [
            {
                "employee_id": str(uuid4()),
                "metric_id": str(uuid4()),
                "score": 11.0,
                "category": "quality",
            }
        ]
        valid, errors = self.service.validate_scores(entries)
        assert valid == []
        assert any("score must be in [0, 10]" in e for e in errors)

    def test_validate_scores_missing_employee_id(self):
        entries = [{"metric_id": str(uuid4()), "score": 5.0, "category": "quality"}]
        valid, errors = self.service.validate_scores(entries)
        assert valid == []
        assert any("employee_id is required" in e for e in errors)

    def test_validate_scores_missing_metric_id(self):
        entries = [{"employee_id": str(uuid4()), "score": 5.0, "category": "quality"}]
        valid, errors = self.service.validate_scores(entries)
        assert valid == []
        assert any("metric_id is required" in e for e in errors)

    def test_validate_scores_boundary_values(self):
        entries = [
            {"employee_id": str(uuid4()), "metric_id": str(uuid4()), "score": 0.0, "category": "quality"},
            {"employee_id": str(uuid4()), "metric_id": str(uuid4()), "score": 10.0, "category": "quality"},
        ]
        valid, errors = self.service.validate_scores(entries)
        assert len(valid) == 2
        assert errors == []

    def test_compute_deltas_first_period(self):
        emp_id = str(uuid4())
        current = [
            {
                "employee_id": emp_id,
                "total_score": 8.0,
                "global_rank": 1,
            }
        ]
        res = self.service.compute_deltas(current, previous_snapshots={})
        assert res[0]["delta_score"] is None
        assert res[0]["delta_rank"] is None

    def test_compute_deltas_with_previous(self):
        emp_id = str(uuid4())

        class Prev:
            total_score = 7.25
            rank = 3

        current = [
            {"employee_id": emp_id, "total_score": 8.0, "global_rank": 1}
        ]
        res = self.service.compute_deltas(current, previous_snapshots={uuid4(): Prev()})
        # предыдущий снапшот по другому UUID — дельт не будет
        assert res[0]["delta_score"] is None
        assert res[0]["delta_rank"] is None

        # правильный ключ
        from uuid import UUID
        res = self.service.compute_deltas(
            current,
            previous_snapshots={UUID(emp_id): Prev()},
        )
        assert res[0]["delta_score"] == pytest.approx(0.75)
        assert res[0]["delta_rank"] == 2  # 3 - 1 = +2 позиции

