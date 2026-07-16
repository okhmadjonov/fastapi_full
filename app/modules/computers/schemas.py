from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class ComputerBase(BaseModel):
    name: str
    brand: str
    price: float

class ComputerCreate(ComputerBase):
    pass

class ComputerUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    price: Optional[float] = None

class ComputerResponse(ComputerBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
