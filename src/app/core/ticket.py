from src.app.schemas.tickets import (
    CreateTicketUpdate, 
    CreateTicketAdd, 
    ResponseTicketAdd, 
    AddTicketData, 
    UpdateTicketData, 
    ResponseTicketUpdate,
    TicketList, TicketBase
)
from src.app.models import (
    Ticket, 
    TicketAddData, 
    TicketEditData, 
    TicketStatus, 
    TicketType
)
from src.app.schemas.user import UserBase
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class TicketService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_add_ticket(self, user_id: int, payload: CreateTicketAdd):
        try:
            new_ticket = Ticket(
                ticket_type=TicketType.add_data.value,
                status=TicketStatus.pending.value,
                created_by=user_id,
                answered_by=None
            )
            self.db.add(new_ticket)
            await self.db.flush()
            await self.db.refresh(new_ticket)

            ticket_data = TicketAddData(
                ticket_id=new_ticket.id,
                parent_id=payload.parent_id,
                name=payload.name
            )

            self.db.add(ticket_data)
            await self.db.commit()

            await self.db.refresh(new_ticket, attribute_names=["created_by_user", "answered_by_user", "add_data_items"])
            await self.db.refresh(ticket_data)

            response = ResponseTicketAdd(
                id=new_ticket.id,
                ticket_type=new_ticket.ticket_type.value,
                status=new_ticket.status.value,
                created_by=UserBase.from_orm(new_ticket.created_by_user),
                answered_by=(
                    UserBase.from_orm(new_ticket.answered_by_user)
                    if new_ticket.answered_by_user
                    else None
                ),
                data=AddTicketData(
                    parent_id=ticket_data.parent_id,
                    name=ticket_data.name
                ),
                created_at=new_ticket.created_at,
                updated_at=new_ticket.updated_at,
            )

            return response
        except:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Жаңа өтініш жазу кезінде қателік болды, кейінірек қайталап көріңіз'
            )

    async def create_update_ticket(self, user_id: int, payload: CreateTicketUpdate):
        try: 
            new_ticket = Ticket(
                ticket_type=TicketType.edit_data.value,
                status=TicketStatus.pending.value,
                created_by=user_id,
                answered_by=None
            )
            self.db.add(new_ticket)
            await self.db.flush()
            await self.db.refresh(new_ticket) 

            ticket_data = TicketEditData(
                ticket_id=new_ticket.id,
                tree_id=payload.tree_id,
                new_name=payload.new_name,
                new_bio=payload.new_bio,
                new_birth=payload.new_birth,
                new_death=payload.new_death
            )

            self.db.add(ticket_data)
            await self.db.commit()

            await self.db.refresh(new_ticket, attribute_names=["created_by_user", "answered_by_user", "edit_data_items"])
            await self.db.refresh(ticket_data)

            response = ResponseTicketUpdate(
                id=new_ticket.id,
                ticket_type=new_ticket.ticket_type.value,
                status=new_ticket.status.value,
                created_by=UserBase.from_orm(new_ticket.created_by_user),
                answered_by=(
                    UserBase.from_orm(new_ticket.answered_by_user)
                    if new_ticket.answered_by_user
                    else None
                ),
                data=UpdateTicketData(
                    tree_id=ticket_data.tree_id,
                    new_name=ticket_data.new_name,
                    new_bio=ticket_data.new_bio,
                    new_birth=ticket_data.new_birth,
                    new_death=ticket_data.new_death,
                ),
                created_at=new_ticket.created_at,
                updated_at=new_ticket.updated_at,
            )

            return response


        except:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Жаңа өтініш жазу кезінде қателік болды, кейінірек қайталап көріңіз'
            )

    async def get_my_tickets(self, user_id: int, limit: int = 10, offset: int = 0):
        stmp = await self.db.execute(
            select(Ticket).where(Ticket.created_by == user_id).limit(limit).offset(offset)
        )
        tickets = stmp.scalars().all()

        response = TicketList(
            items=[
                TicketBase(
                    id=ticket.id,
                    ticket_type=ticket.ticket_type.value,
                    status=ticket.status.value,
                    created_by=user_id,
                    created_at=ticket.created_at,
                    updated_at=ticket.updated_at
                )
                for ticket in tickets
            ],
            total=len(tickets),
            limit=limit,
            offset=offset
        )

        return response
