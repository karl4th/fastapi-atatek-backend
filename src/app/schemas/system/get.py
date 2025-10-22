from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class RoleBase(BaseModel):
    id: int
    name: str
    description: str

    class Config:
        from_attributes=True


class RoleResponse(RoleBase):
    created_at: datetime
    updated_at: datetime




class RolesList(BaseModel):
    items: List[RoleResponse]
    total: int




class AddressBase(BaseModel):
    id: int
    osm: str
    name: str
    display_name: str

    class Config:
        from_attributes=True
