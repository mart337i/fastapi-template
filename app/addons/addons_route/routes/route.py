from fastapi import HTTPException
from fastapi.routing import APIRouter
from fastapi.responses import FileResponse
import starlette
import re
import sys

from app.base.logger import logger as _logger

router = APIRouter(
    prefix=f"/test",
    tags=["Test route"],
)

dependency = []


@router.get('/test')
def test():
    return {"Modules": f"{sys.modules.keys()}"}

@router.get("/route1")
async def route1():
    return {"message": "Route 1"}

@router.get("/route2")
async def route2():
    return {"message": "Route 2"}
