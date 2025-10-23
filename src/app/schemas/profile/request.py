from pydantic import BaseModel, Field
from typing import Optional


class UpdateUser(BaseModel):
    first_name: Optional[str] = Field(..., example="Бағжан")
    last_name: Optional[str] = Field(..., example="Карл")
    middle_name: Optional[str] = Field(..., example="Саматұлы")

    address_id: Optional[int] = None
    page_id: Optional[int] = None

class ResetUserPasswort(BaseModel):
    old_password: Optional[str] = Field(..., example="")
    new_password: Optional[str] = Field(..., example="")
    confirm_password: Optional[str] = Field(..., example="")