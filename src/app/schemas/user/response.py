from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from src.app.schemas.system import RoleBase, AddressBase
from src.app.schemas.page import PageBase

class UserBase(BaseModel):
    id: int
    
    first_name: str
    last_name: str
    middle_name: Optional[str]

    phone: str

    is_active: bool
    is_banned: bool
    is_deleted: bool
    is_verified: bool

    class Config:
        from_attributes=True


class UserFull(UserBase):
    role: RoleBase
    address: Optional[AddressBase]
    page: Optional[PageBase]

    class Config:
        from_attributes=True


class UserResponse(UserBase):
    created_at: datetime
    updated_at: datetime