from pydantic import BaseModel, Field
from typing import List, Optional

class PageBase(BaseModel):
    id: int
    title: int
    tree_id: int | None

    bread1: str
    bread2: str
    bread3: str

    main_gen: int
    main_gen_child: int

    class Config:
        from_attributes=True