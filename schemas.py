from pydantic import BaseModel
from datetime import datetime

class TransactionCreate(BaseModel):
    description: str
    amount: float
    category: str

class TransactionOut(BaseModel):
    id: int
    description: str
    amount: float
    category: str
    created_at: datetime

    class Config:
        from_attributes = True
