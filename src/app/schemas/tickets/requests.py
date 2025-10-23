from pydantic import BaseModel
from enum import Enum
from typing import Optional

class TicketType(Enum):
    add_data = "add_data"
    edit_data = "edit_data"

class TicketStatus(Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class CreateTicketAdd(BaseModel):
    ticket_type: TicketType
    parent_id: int
    name: str

class CreateTicketUpdate(BaseModel):
    ticket_type: TicketType
    tree_id: int
    new_name: str
    new_bio: Optional[str] = None
    new_birth: Optional[str] = None
    new_death: Optional[str] = None

