#To create a route group
from fastapi import APIRouter, Path
from typing import Optional
from datetime import date
#importing Expense model and RegisterUser model
from models import Expense, RegisterUser
from data_base import users_collection, roles_collection
from bson import ObjectId
import crud

#creating a router instance
router = APIRouter()


#Endpoints using the model
#Route to create new expense
@router.post("/expenses/")
def create_expense(expense: Expense):
    #call function to add to db
    crud.add_expense(expense)
    return {"msg": "Expense added"}
#Get expenses
@router.get("/expenses/")
def view_expenses(start: Optional[date] =None, end: Optional[date] = None, category: Optional[str] = None):
    if start and end:
        return crud.get_expenses_by_date_range(start, end)
    elif category:
        return crud.get_expenses_by_category(category)
    #return all if no filter

    return crud.get_all_expenses()

#Route to create category
@router.post("/categories/")
def create_category(name: str):
    return crud.add_category(name)

#Route to get categories
@router.get("/categories/")
def view_categories():
    return crud.get_categories()


# @router.get("/summary/monthly")
# def monthly_summary():
#     return crud.get_monthly_total()

@router.get("/summary/monthly/{month}")
def total_for_month(month: str = Path(description= "Month in the format YYYY-MM, e.g., 2025-08")):    #Month format "YYYY-MM"
    return crud.get_total_for_month(month)

# @router.get("/summary/weekly")
# def weekly_summary():
#     return crud.get_weekly_breakdown()

@router.get("/summary/top-categories")
def top_categories():
    return crud.get_top_categories()

#registration
@router.post("/auth/register")
def register_user(user: RegisterUser):
    #Check if email already exists
    if users_collection.find_one({"email": user.email}):
        return {"error": "Email already registered"}
    #Get 'user' role or create it if not exists
    role = roles_collection.find_one({"name": "user"})
    if not role:
        role_id = roles_collection.insert_one({"name": "user"}).inserted_id
    else:
        role_id = role["_id"]

    # Hash password
    hashed_pw = crud.hash_password(user.password)

    # Insert user
    users_collection.insert_one({
        "full_name": user.full_name,
        "email": user.email,
        "password_hash": hashed_pw,
        "role_id": role_id
    })

    return {"msg": "User registered successfully"}