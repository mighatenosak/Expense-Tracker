from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

#for expenses
class Expense(BaseModel):
    amount: float
    category: str
    date: date
    description: Optional[str] = None
#For the registration of users
class RegisterUser(BaseModel):
    full_name: str
    email: EmailStr
    password: str
# for login
class LoginUser(BaseModel):
    email: EmailStr
    password: str