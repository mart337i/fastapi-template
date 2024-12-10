from fastapi import HTTPException
from fastapi.routing import APIRouter
from fastapi.responses import FileResponse
import starlette
import re

from base.logger import logger as _logger


router = APIRouter(
    prefix=f"/test",
    tags=["Test route"],
)

dependency = []


@router.get('/test')
def test():
    return {"access_token": "200"}
