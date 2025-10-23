from pydantic import BaseModel

class Tariff(BaseModel):
    id: int
    name: str
    settings: dict

    class Config:
        from_attributes=True