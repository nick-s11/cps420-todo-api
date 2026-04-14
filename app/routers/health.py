from fastapi import APIRouter, HTTPException
from app.database.connection import database
 
router = APIRouter(tags=["health"])
 
 
@router.get("/health")
async def health_check():
    """Returns 200 when healthy, 503 when the database is unreachable."""
    if database.db is None:
        raise HTTPException(status_code=503, detail="Database not connected")
    try:
        await database.client.admin.command("ping")
        return {"status": "ok"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc))