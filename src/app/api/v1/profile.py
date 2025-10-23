from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.config import auth
from src.app.db import get_db

from src.app.utils import standar_atatek
from src.app.schemas.profile import UpdateUser, ResetUserPasswort
from src.app.core import ProfileService

router = APIRouter(prefix="/profile", tags=['Profile'])

@router.put('/update')
@standar_atatek
async def update_user_data(
    payload: UpdateUser, 
    user_data = Depends(auth.get_user_data_dependency()), 
    db: AsyncSession = Depends(get_db)
    ):
    service = ProfileService(db)
    user_id = int(user_data['sub'])
    return await service.update_profile(user_id=user_id, payload=payload)

@router.patch('/reset-password')
@standar_atatek
async def reset_password(
    payload: ResetUserPasswort, 
    user_data = Depends(auth.get_user_data_dependency()), 
    db: AsyncSession = Depends(get_db)
    ):
    service = ProfileService(db)
    user_id = int(user_data['sub'])
    return await service.update_password(user_id=user_id, payload=payload)