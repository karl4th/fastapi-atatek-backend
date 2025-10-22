from pydantic import BaseModel, Field
from typing import List, Optional

class CreateUser(BaseModel):
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    phone: str
    password: str


class VerifyUser(BaseModel):
    verify_code: int = 000000

class SetAddressUser(BaseModel):
    address_id: int

class LoginUser(BaseModel):
    phone: str
    password: str