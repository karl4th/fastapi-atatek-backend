from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.config import auth
from src.app.db import get_db

from src.app.utils import standar_atatek

router = APIRouter(prefix="/profile", tags=['Profile'])

