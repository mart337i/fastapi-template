from fastapi.routing import APIRouter
from fastapi import HTTPException, Depends
from typing import Any
from datetime import timedelta

from fastapi.responses import JSONResponse
from pydantic import BaseModel
import base64

from ..models.auth import User

from app.base.logger import logger as _logger
import os

router = APIRouter()

@router.post('/login')
def login(user: User):
    return {"access_token": "200"}