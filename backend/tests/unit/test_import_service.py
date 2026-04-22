import pytest
from app.core.services.import_service import ImportService
from app.core.exceptions import ImportValidationError


class TestImportService:
    
    def setup_method(self):
        self.service = ImportService()
    
    def _make_csv(self, rows: list[dict]) -> bytes:
        import csv
        import io
        if not rows:
            return b""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
        return output.getvalue().encode("utf-8")
    
    def test_parse_valid_csv(self):
        """Корректный CSV парсится без ошибок"""
        from uuid import uuid4
        content = self._make_csv([
            {
                "employee_id": str(uuid4()),
                "metric_id": str(uuid4()),
                "score": "7.5",
                "category": "quality",
                "period": "2024-01-01",
            }
        ])
        rows = self.service.parse_csv(content)
        assert len(rows) == 1
    
    def test_parse_missing_required_columns(self):
        """CSV без обязательных колонок вызывает ошибку"""
        content = b"name,score\nJohn,5"
        with pytest.raises(ImportValidationError) as exc_info:
            self.service.parse_csv(content)
        assert "Missing required columns" in str(exc_info.value)
    
    def test_parse_empty_csv(self):
        """Пустой файл вызывает ошибку"""
        with pytest.raises(ImportValidationError) as exc_info:
            self.service.parse_csv(b"")
        assert "empty" in str(exc_info.value).lower()
    
    def test_parse_utf8_bom(self):
        """CSV с BOM маркером корректно обрабатывается"""
        from uuid import uuid4
        content = self._make_csv([
            {
                "employee_id": str(uuid4()),
                "metric_id": str(uuid4()),
                "score": "8.0",
                "category": "performance",
                "period": "2024-01-01",
            }
        ])
        bom_content = b"\xef\xbb\xbf" + content
        rows = self.service.parse_csv(bom_content)
        assert len(rows) == 1
    
    def test_transform_row_valid(self):
        """Корректная строка трансформируется без ошибок"""
        from uuid import uuid4
        row = {
            "employee_id": str(uuid4()),
            "metric_id": str(uuid4()),
            "score": "8.5",
            "category": "quality",
            "period": "2024-01-01",
            "comment": "Good work",
        }
        result = self.service.transform_row(row)
        assert result["score"] == 8.5
        assert str(result["period"]) == "2024-01-01"
    
    def test_transform_row_invalid_uuid(self):
        """Невалидный UUID вызывает ValueError"""
        row = {
            "employee_id": "not-a-uuid",
            "metric_id": "also-not-uuid",
            "score": "5.0",
            "category": "quality",
            "period": "2024-01-01",
        }
        with pytest.raises(ValueError):
            self.service.transform_row(row)

