from fastapi import HTTPException
from fastapi.routing import APIRouter
from fastapi.responses import FileResponse
import starlette
import re
import sys

from app.base.logger import logger as _logger

router = APIRouter(
    prefix=f"/test2",
    tags=["Test route2"],
)

dependency = []


@router.get('/test_route2')
def test_route2():
    return {"Modules": "Testing"}
