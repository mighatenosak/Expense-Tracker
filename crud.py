#Connect to MongoDB
from data_base import expenses_collection, categories_collection, users_collection, roles_collection
#imports the Pydantic model for validating expense data.
from models import Expense  
from datetime import datetime, date
#CryptoContext for hashing and verifying passwords
from passlib.context import CryptContext
from typing import Union, Optional,Any  #'Any'type-hint that a variable can hold any data
#bson.objectid to convert str into objectid
from bson import ObjectId


#create expense
def add_expense(expense: Union[Expense, dict], current_user: dict):
    #convert Pydantic model to dict if needed
    #if it’s a Pydantic object convert to dictionary using .model_dump().
    if isinstance(expense, Expense):
        data = expense.model_dump()
    else:   #if it’s already a dictionary, make a copy.
        data = dict(expense)

    # Attach the user_id to the expense(converted to str because Mongo IDs are objs)
    data["user_id"] = str(current_user["_id"])

    # Ensure date is ISO string in format (YYYY-MM-DD)which is MongoDB-friendly
    if isinstance(data.get("date"), (datetime, date)):
        data["date"] = data["date"].isoformat()

    return expenses_collection.insert_one(data) #return expense
# def add_expense(expense: Expense):
    # return expenses_collection.insert_one(expense.dict())
    # return expenses_collection.insert_one(expense.model_dump())

#get all expenses
def get_all_expenses(user_id: str):
    expenses = list(expenses_collection.find({"user_id": user_id})) #fetch expense
    #convert Mongo ID obj to str for json
    for exp in expenses:
        exp["_id"] = str(exp["_id"])
    return expenses #return list of expenses

#create category
def add_category(name: str):
    #prevents duplicate categories
    if categories_collection.find_one({"name": name}):
        return {"msg": "Category already exists"}
    categories_collection.insert_one({"name": name})    #insert category into DB
    return {"msg": "Category added"}

#get all category
def get_categories():
    #retrieve all categories and covert obj id to str
    categories = list(categories_collection.find())
    for cat in categories:
        cat["_id"] = str(cat["_id"])  #convert ObjectId to string
    return categories


#filter by date
# def get_expenses_by_date_range(start, end):
def get_expenses_by_date_range(start, end, user_id: str):
    #convert python date objects to str
    start_str = start.isoformat()
    end_str = end.isoformat()
    #filter expenses between start and end dates for the given user
    expenses = list(expenses_collection.find({
        "user_id": user_id,
        "date": {"$gte": start_str, "$lte": end_str}
    }))
    #convert obj id to str
    for exp in expenses:
        exp["_id"] = str(exp["_id"])
    return expenses



#filter by category
def get_expenses_by_category(category, user_id: str):
    #find expenses for a user where the category matches
    expenses = list(expenses_collection.find({
        "user_id": user_id,
        "category": category
    }))
    #convert obj id to str
    for exp in expenses:
        exp["_id"] = str(exp["_id"])
    return expenses
#monthly total summary
def get_total_for_month(month: str, user_id: str):
    #here i used regex to match all dates starting with "YYYY-MM"
    expenses = list(expenses_collection.find(
        {
            "user_id": user_id,
            "date": {"$regex": f"^{month}"}
        }
    ))
    #sums total amount for that month
    total = sum(exp["amount"] for exp in expenses)
    return {"month": month, "total": total}



#top3 spending categories where the most money was spent
def get_top_categories(user_id: str, limit: int = 3):
    #using MONGODB's aggregation pipeline to filter by user, group by category and sum amounts, sort by total spent
    #and limit to top n categories(default 3)
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
        "password_hash": hash_password(password),   #password hashing using bcrypt algo
        "role_id": role_id
    })
    return {"msg": "User registered successfully"}

#login user
def login_user(email: str, password: str):
    #verify email and password by matching
    user = users_collection.find_one({"email": email})
    if not user:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return user

#add password hashing utility using bcrypt algorithm from Cryptocontext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")   #'deprecated=auto' automatically rehashes and old hashing scheme if detected.
#hashing pass
def hash_password(password: str) -> str:
    return pwd_context.hash(password)
#pass verification
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

#get roll name

def get_role_name(role_id: Union[str, ObjectId]) -> Optional[str]:
    #convert string ids to obj id
    if isinstance(role_id, str):
        try:
            role_id = ObjectId(role_id)
        except Exception:
            return None
    #fetch the role name
    role = roles_collection.find_one({"_id": role_id})
    return role["name"] if role else None

#view users(admin only)
def get_all_users():
    #retrieve all users excluding pass hashes
    users = list(users_collection.find({}, {"password_hash": 0}))  # exclude passwords
    for user in users:
        user["_id"] = str(user["_id"])
        user["role_id"] = str(user["role_id"])
    return users

#update expenses (for users)
#admins can edit any expense, normal users can only edit their own expenses
def update_expense(expense_id: str, updates: dict, current_user: dict, admin: bool = False):
    query: dict[str, Any] = {"_id": ObjectId(expense_id)}
    if not admin:
        query["user_id"] = str(current_user["_id"])  # match stored string user_id

    #remove empty update fields before updating
    updates = {k: v for k, v in updates.items() if v is not None and v != ""}
    result = expenses_collection.update_one(query, {"$set": updates})
    
    if result.modified_count == 0:
        return {"error": "No expense updated. Check ID or permissions."}
    return {"msg": "Expense updated successfully"}

#delete user(admin)
def delete_user(user_id: str):
    #delete user by id
    result = users_collection.delete_one({"_id": ObjectId(user_id)})
    return {"deleted_count": result.deleted_count}

#update user(admin)
def update_user(user_id: str, updates: dict):
    #if pass is updated, hash it before storing
    if "password" in updates:
        updates["password_hash"] = hash_password(updates.pop("password"))
    result = users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": updates})
    return {"modified_count": result.modified_count}

#update categories(admin)
def update_category(category_id: str, name: str):
    result = categories_collection.update_one({"_id": ObjectId(category_id)}, {"$set": {"name": name}})
    return {"modified_count": result.modified_count}

#delete category(admin)

def delete_category(category_id: str):
    result = categories_collection.delete_one({"_id": ObjectId(category_id)})
    return {"deleted_count": result.deleted_count}
