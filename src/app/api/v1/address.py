from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.config import auth
from src.app.db import get_db
from src.app.core import AddressService


router = APIRouter(prefix="/address", tags=['Adress'])

@router.get("")
async def search_addres(query: str, db: AsyncSession = Depends(get_db)):
    service = AddressService(db)
    return await service.search_locations(query=query)

@router.post('/set')
async def set_or_update_user_address(address_id: int, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    service = AddressService(db)
    user_id = int(user_data['sub'])
    return await service.set_or_update_address(user_id, address_id)