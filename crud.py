#Connect to MongoDB
from data_base import expenses_collection, categories_collection, users_collection, roles_collection
#For schema
from models import Expense  
from datetime import datetime, date
from passlib.context import CryptContext
from typing import Union, Optional
from bson import ObjectId

#Create expense
def add_expense(expense: Union[Expense, dict], current_user: dict):
    """Add a new expense linked to a specific user."""
    # Convert Pydantic model to dict if needed
    if isinstance(expense, Expense):
        data = expense.model_dump()
    else:
        data = dict(expense)

    # Attach the user_id
    data["user_id"] = str(current_user["_id"])

    # Ensure date is ISO string
    if isinstance(data.get("date"), (datetime, date)):
        data["date"] = data["date"].isoformat()

    return expenses_collection.insert_one(data)
# def add_expense(expense: Expense):
    # return expenses_collection.insert_one(expense.dict())
    # return expenses_collection.insert_one(expense.model_dump())

#Get all expenses
def get_all_expenses(user_id: str):
    expenses = list(expenses_collection.find({"user_id": user_id}))
    for exp in expenses:
        exp["_id"] = str(exp["_id"])
    return expenses
    
    return expenses
#create category
def add_category(name: str):
    #Prevent duplicates
    if categories_collection.find_one({"name": name}):
        return {"msg": "Category already exists"}
    categories_collection.insert_one({"name": name})
    return {"msg": "Category added"}

#Get All Category
def get_categories():
    categories = list(categories_collection.find())
    for cat in categories:
        cat["_id"] = str(cat["_id"])  #Convert ObjectId to string
    return categories


#Filter by date
# def get_expenses_by_date_range(start, end):
def get_expenses_by_date_range(start, end, user_id: str):
    start_str = start.isoformat()
    end_str = end.isoformat()
    expenses = list(expenses_collection.find({
        "user_id": user_id,
        "date": {"$gte": start_str, "$lte": end_str}
    }))
    for exp in expenses:
        exp["_id"] = str(exp["_id"])
    return expenses



#Filter by category
def get_expenses_by_category(category, user_id: str):
    expenses = list(expenses_collection.find({
        "user_id": user_id,
        "category": category
    }))
    for exp in expenses:
        exp["_id"] = str(exp["_id"])
    return expenses
#Monthly total summary
def get_total_for_month(month: str, user_id: str):
    expenses = list(expenses_collection.find(
        {
            "user_id": user_id,
            "date": {"$regex": f"^{month}"}
        }
    ))
    total = sum(exp["amount"] for exp in expenses)
    return {"month": month, "total": total}



#Top3 spending categories where the most money was spent
def get_top_categories(user_id: str, limit: int = 3):
    # Filter first by user_id
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {
            "_id": "$category",
            "total": {"$sum": "$amount"}
        }},
        {"$sort": {"total": -1}},
        {"$limit": limit}
    ]
    return list(expenses_collection.aggregate(pipeline))

#register user
def register_user(full_name: str, email: str, password: str):
    #check if email already exists
    if users_collection.find_one({"email": email}):
        return {"error": "Email already registered"}

    #get user role or create it
    role = roles_collection.find_one({"name": "user"})
    if not role:
        role_id = roles_collection.insert_one({"name": "user"}).inserted_id
    else:
        role_id = role["_id"]

    #insert user
    users_collection.insert_one({
        "full_name": full_name,
        "email": email,
        "password_hash": hash_password(password),
        "role_id": role_id
    })
    return {"msg": "User registered successfully"}

#login user
def login_user(email: str, password: str):
    user = users_collection.find_one({"email": email})
    if not user:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return user

#add password hashing utility using bcrypt from Cryptocontext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_password(password: str) -> str:
    return pwd_context.hash(password)
# pass verification
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

#get roll name

def get_role_name(role_id: Union[str, ObjectId]) -> Optional[str]:
    """Return the role name for a given role_id, or None if not found."""
    if isinstance(role_id, str):
        try:
            role_id = ObjectId(role_id)
        except Exception:
            return None
    role = roles_collection.find_one({"_id": role_id})
    return role["name"] if role else None