from decimal import Decimal
from uuid import UUID
import logging

logger = logging.getLogger(__name__)


class RatingCalculatorService:

    def validate_scores(self, entries: list[dict]) -> tuple[list[dict], list[str]]:
        valid = []
        errors = []
        for i, entry in enumerate(entries):
            row_errors = []
            score = entry.get("score", -1)
            try:
                if not (0 <= float(score) <= 10):
                    row_errors.append(f"Row {i}: score must be in [0, 10], got {score}")
            except (TypeError, ValueError):
                row_errors.append(f"Row {i}: score must be a number, got {score}")

            if not entry.get("employee_id"):
                row_errors.append(f"Row {i}: employee_id is required")

            if not entry.get("metric_id"):
                row_errors.append(f"Row {i}: metric_id is required")

            if row_errors:
                errors.extend(row_errors)
            else:
                valid.append(entry)

        return valid, errors

    def compute_deltas(
        self,
        current: list[dict],
        previous_snapshots: dict,
    ) -> list[dict]:
        result = []
        for row in current:
            emp_id = row.get("employee_id")
            if isinstance(emp_id, str):
                emp_id = UUID(emp_id)

            prev = previous_snapshots.get(emp_id)
            delta_score = None
            delta_rank = None

            if prev:
                delta_score = float(row["total_score"]) - float(prev.total_score)
                delta_rank = int(prev.rank) - int(row["global_rank"])

            result.append({
                **row,
                "delta_score": delta_score,
                "delta_rank": delta_rank,
            })
        return result

