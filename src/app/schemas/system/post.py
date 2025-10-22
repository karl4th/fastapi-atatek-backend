from pydantic import BaseModel, Field
from typing import List, Optional

class RoleCreate(BaseModel):
    name: str
    description: str