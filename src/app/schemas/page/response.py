from pydantic import BaseModel, Field
from typing import List, Optional

class ModeratorBase(BaseModel):
    id: int
    
    first_name: str
    last_name: str
    middle_name: Optional[str]

    phone: str

class PageBase(BaseModel):
    id: int
    title: str
    tree_id: int

    bread1: str
    bread2: str
    bread3: str

    main_gen: int
    main_gen_child: int

    class Config:
        from_attributes=True

class FullPageResponse(PageBase):
    moderators: List[ModeratorBase] = Field(default_factory=list)

    class Config:
        from_attributes = True



class PageListResponse(BaseModel):
    items: List[PageBase]
    total: int
    limit: Optional[int] = 10
    offset: Optional[int] = 0

    class Config:
        from_attributes = True