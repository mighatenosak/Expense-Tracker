#Connect to MongoDB
from data_base import expenses_collection, categories_collection, users_collection, roles_collection
#For schema
from models import Expense  
from datetime import datetime
from passlib.context import CryptContext

#Create expense
def add_expense(expense: Expense):
    #convert pydantic model into a python dictionary
    #Python models like expense arepython objects and mongodb only understands basic data types:dict,list,str,int,float,bool etc.
    data = expense.model_dump()
    data["date"] = data["date"].isoformat()  # Converts date object to "YYYY-MM-DD string"
    return expenses_collection.insert_one(data) #Insert dictionary to mongodb

# def add_expense(expense: Expense):
    # return expenses_collection.insert_one(expense.dict())
    # return expenses_collection.insert_one(expense.model_dump())

#Get all expenses
def get_all_expenses():
    #get all expense documents form the database
    expenses = list(expenses_collection.find())
    
    for exp in expenses:
        #Convert ObjectId to str
        exp["_id"] = str(exp["_id"])

        #experiment  
        #exp["_id"]
        # print(type(exp["_id"]))

    
    return expenses
#Cretae Category
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
def get_expenses_by_date_range(start, end):
    #convert date to str
    start_str = start.isoformat()  
    end_str = end.isoformat()
    expenses = list(expenses_collection.find({
        "date": {
            "$gte": start_str,
            "$lte": end_str
        }
    }))

    #Converts id to string for each document.
    for exp in expenses:
        #convert ObjectId to string
        exp["_id"] = str(exp["_id"])  

    return expenses



#Filter by category
def get_expenses_by_category(category):
    expenses = list(expenses_collection.find({"category": category}))
    
    for exp in expenses:
        exp["_id"] = str(exp["_id"])
    
    return expenses


#Monthly total summary
def get_total_for_month(month: str):
    expenses=list(expenses_collection.find(
        {
            "date": {"$regex": f"^{month}"}     #using Mongodb's $regex filter ^2025-08 matches any date starting with "2025-08"
        }
    ))
    total=sum(exp["amount"] for exp in expenses)
    return {"month": month,"total":total}

#Top3 spending categories where the most money was spent
def get_top_categories(limit: int=3):
    #Mongodb's aggregation pipeline is designed for a sequence of stages and each stage is a dictionary(like $group,$ sort)
    #To represent this we wrap it inside python's list[]
    pipeline = [
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

#add password hashing utility using bcrypt from Cryptocontext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_password(password: str) -> str:
    return pwd_context.hash(password)
