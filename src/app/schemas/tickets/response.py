from pydantic import BaseModel
from enum import Enum
from src.app.schemas.user import UserBase
from typing import Optional, List
from datetime import datetime

class TicketType(Enum):
    add_data = "add_data"
    edit_data = "edit_data"

class TicketStatus(Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class AddTicketData(BaseModel):
    parent_id: int
    name: str

class UpdateTicketData(BaseModel):
    tree_id: int
    new_name: str
    new_bio: Optional[str] = None
    new_birth: Optional[str] = None
    new_death: Optional[str] = None

class ResponseTicketAdd(BaseModel):
    id: int
    ticket_type: TicketType
    status: TicketStatus

    created_by: UserBase
    answered_by: Optional[UserBase] = None
    data: AddTicketData

    created_at: datetime
    updated_at: datetime

class ResponseTicketUpdate(BaseModel):
    id: int
    ticket_type: TicketType
    status: TicketStatus

    created_by: UserBase
    answered_by: Optional[UserBase] = None
    data: UpdateTicketData

    created_at: datetime
    updated_at: datetime

class TicketBase(BaseModel):
    id: int
    ticket_type: TicketType
    status: TicketStatus

    created_by: int

    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes=True

class TicketList(BaseModel):
    items: List[TicketBase]
    total: int

    limit: Optional[int] = None
    offset: Optional[int] = None