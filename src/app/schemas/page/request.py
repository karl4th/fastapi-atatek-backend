from pydantic import BaseModel, Field
from typing import List, Optional

class CreatePage(BaseModel):
    title: str = Field(..., description="The title of the page")
    
    tree_id: int = Field(..., description="The ID of the associated tree")

    bread1: str = Field(..., description="alban")
    bread2: str = Field(..., description="sary")
    bread3: str = Field(..., description="zharty")

    main_gen_id: int = Field(..., description="Main gen ID")
    main_gen_child_id: int = Field(..., description="Main gen child ID")

class UpdatePage(BaseModel):
    title: Optional[str] = Field(None, description="The title of the page")
    
    tree_id: Optional[int] = Field(None, description="The ID of the associated tree")

    bread1: Optional[str] = Field(None, description="alban")
    bread2: Optional[str] = Field(None, description="sary")
    bread3: Optional[str] = Field(None, description="zharty")

    main_gen_id: Optional[int] = Field(None, description="Main gen ID")
    main_gen_child_id: Optional[int] = Field(None, description="Main gen child ID")
