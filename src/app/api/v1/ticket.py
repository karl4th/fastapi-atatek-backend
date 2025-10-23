from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession


from src.app.db import get_db
from src.app.config.auth import auth
from src.app.schemas.tickets import CreateTicketUpdate, CreateTicketAdd
from src.app.utils import standar_atatek

from src.app.core import TicketService

router = APIRouter(prefix="/ticket", tags=["National tree tickets"])

@router.get('')
@standar_atatek
async def get_my_tickets(
    limit: int = None,
    offset: int = None,
    user_data = Depends(auth.get_user_data_dependency()), 
    db: AsyncSession = Depends(get_db)
):
    service = TicketService(db)
    user_id = int(user_data['sub'])
    return await service.get_my_tickets(
        user_id=user_id,
        limit=limit,
        offset=offset
    )

@router.post('/add')
@standar_atatek
async def create_add_ticket(
    payload: CreateTicketAdd,
    user_data = Depends(auth.get_user_data_dependency()), 
    db: AsyncSession = Depends(get_db)):
    service = TicketService(db)
    user_id = int(user_data['sub'])
    return await service.create_add_ticket(
        user_id=user_id,
        payload=payload
    )


@router.post('/update')
@standar_atatek
async def create_add_ticket(
    payload: CreateTicketUpdate,
    user_data = Depends(auth.get_user_data_dependency()), 
    db: AsyncSession = Depends(get_db)):
    service = TicketService(db)
    user_id = int(user_data['sub'])
    return await service.create_update_ticket(
        user_id=user_id,
        payload=payload
    )