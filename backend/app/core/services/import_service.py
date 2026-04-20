import csv
import io
from datetime import date
from uuid import UUID
import logging

from app.core.exceptions import ImportValidationError

logger = logging.getLogger(__name__)


class ImportService:
    REQUIRED_COLUMNS = {"employee_id", "metric_id", "score", "category", "period"}

    def parse_csv(self, file_content: bytes) -> list[dict]:
        try:
            text = file_content.decode("utf-8-sig")
        except UnicodeDecodeError:
            raise ImportValidationError("File encoding error. Use UTF-8.")

        reader = csv.DictReader(io.StringIO(text))

        if not reader.fieldnames:
            raise ImportValidationError("CSV file is empty")

        missing = self.REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            raise ImportValidationError(f"Missing required columns: {missing}")

        rows = []
        for i, row in enumerate(reader, start=2):
            cleaned = {k.strip(): v.strip() for k, v in row.items()}
            cleaned["_row_number"] = i
            rows.append(cleaned)

        logger.info(f"Parsed {len(rows)} rows from CSV")
        return rows

    def transform_row(self, row: dict) -> dict:
        return {
            "employee_id": UUID(row["employee_id"]),
            "metric_id": UUID(row["metric_id"]),
            "score": float(row["score"]),
            "category": row["category"],
            "period": date.fromisoformat(row["period"]),
            "comment": row.get("comment", ""),
        }

