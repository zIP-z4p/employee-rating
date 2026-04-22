from datetime import date
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, get_cache
from app.infrastructure.cache.rating_cache import RatingCacheService
from app.infrastructure.database.models.rating import RatingEntry, RatingSnapshot
from app.core.services.import_service import ImportService
from app.core.services.rating_calculator import RatingCalculatorService
from app.core.exceptions import ImportValidationError
from app.schemas.rating import RatingEntryCreate

router = APIRouter(prefix="/ratings", tags=["ratings"])


@router.get("/snapshots/{period}")
async def get_snapshot(
    period: date,
    top_n: int | None = Query(None, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    cache: RatingCacheService = Depends(get_cache),
):
    cached = await cache.get_snapshot(period, top_n)
    if cached:
        return cached

    query = (
        select(RatingSnapshot)
        .options(
            selectinload(RatingSnapshot.employee).selectinload(
                __import__(
                    'app.infrastructure.database.models.employee',
                    fromlist=['Employee']
                ).Employee.department
            )
        )
        .where(RatingSnapshot.period == period)
        .order_by(RatingSnapshot.rank)
    )
    if top_n:
        query = query.limit(top_n)

    result = await db.execute(query)
    snapshots = result.scalars().all()

    if not snapshots:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No snapshot found for period {period}",
        )

    data = [
        {
            "employee_id": str(s.employee_id),
            "employee_name": s.employee.full_name,
            "department_name": s.employee.department.name,
            "period": str(s.period),
            "total_score": float(s.total_score),
            "rank": s.rank,
            "department_rank": s.department_rank,
            "percentile": float(s.percentile),
            "delta_score": float(s.delta_score) if s.delta_score is not None else None,
            "delta_rank": s.delta_rank,
        }
        for s in snapshots
    ]

    await cache.set_snapshot(period, top_n, data)
    return data


@router.get("/analytics/trends")
async def get_employee_trends(
    employee_id: UUID,
    months: int = Query(6, ge=1, le=24),
    db: AsyncSession = Depends(get_db),
):
    from app.infrastructure.database.models.employee import Employee

    result = await db.execute(
        select(RatingSnapshot)
        .options(selectinload(RatingSnapshot.employee))
        .where(RatingSnapshot.employee_id == employee_id)
        .order_by(RatingSnapshot.period)
        .limit(months)
    )
    snapshots = result.scalars().all()

    if not snapshots:
        raise HTTPException(
            status_code=404,
            detail=f"No rating data for employee {employee_id}",
        )

    return {
        "employee_id": str(employee_id),
        "employee_name": snapshots[0].employee.full_name,
        "trend": [
            {
                "period": str(s.period),
                "total_score": float(s.total_score),
                "rank": s.rank,
                "percentile": float(s.percentile),
                "delta_score": float(s.delta_score) if s.delta_score is not None else None,
            }
            for s in snapshots
        ],
    }


@router.post("/snapshots/build", status_code=202)
async def build_snapshot(
    period: date,
    db: AsyncSession = Depends(get_db),
    cache: RatingCacheService = Depends(get_cache),
):
    from app.core.services.snapshot_service import SnapshotService
    service = SnapshotService(db, cache)
    result = await service.build_snapshot(period)
    return result


@router.post("/import", status_code=201)
async def import_ratings_csv(
    file: UploadFile = File(...),
    period: date = Query(...),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    content = await file.read()
    import_service = ImportService()
    calculator = RatingCalculatorService()

    try:
        rows = import_service.parse_csv(content)
    except ImportValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    transformed = []
    parse_errors = []
    for row in rows:
        try:
            transformed.append(import_service.transform_row(row))
        except (ValueError, KeyError) as e:
            parse_errors.append(f"Row {row.get('_row_number', '?')}: {e}")

    valid_rows, validation_errors = calculator.validate_scores(transformed)
    all_errors = parse_errors + validation_errors

    for entry_data in valid_rows:
        entry_data["period"] = period
        entry_data.pop("_row_number", None)
        db.add(RatingEntry(**entry_data))
    await db.commit()

    return {
        "task_id": "sync-import",
        "total_rows": len(rows),
        "valid_rows": len(valid_rows),
        "error_count": len(all_errors),
        "errors": all_errors[:50],
        "status_url": f"/api/v1/ratings/snapshots/{period}",
    }

@router.post("/", status_code=201)
async def create_rating_entry(
    data: RatingEntryCreate,
    db: AsyncSession = Depends(get_db),
):
    entry = RatingEntry(**data.model_dump())
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return {"id": str(entry.id)}
