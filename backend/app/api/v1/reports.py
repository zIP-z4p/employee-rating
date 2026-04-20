from fastapi import APIRouter

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/generate", status_code=202)
async def generate_report(data: dict):
    return {
        "task_id": "mock-task-id",
        "status": "queued",
        "status_url": "/api/v1/reports/status/mock-task-id",
    }


@router.get("/status/{task_id}")
async def report_status(task_id: str):
    return {"task_id": task_id, "status": "completed"}

