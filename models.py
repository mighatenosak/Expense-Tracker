from pydantic import BaseModel
from typing import Optional
from datetime import date

class Expense(BaseModel):
    amount: float
    category: str
    date: date
    description: Optional[str] = None
