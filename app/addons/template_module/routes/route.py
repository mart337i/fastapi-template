from fastapi import HTTPException
from fastapi.routing import APIRouter
from fastapi.responses import FileResponse

from app.base.logger import logger as _logger

router = APIRouter(
    prefix=f"/test",
    tags=["Test route"],
)

dependency = []


@router.get("/route1")
async def route1():
    return {"message": "Route 1"}

@router.get("/route2")
async def route2():
    return {"message": "Route 2"}
