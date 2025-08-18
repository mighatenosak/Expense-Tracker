#To create a route group
#APIrouter allows grouping of all routes together so that it cann attach them to the main FASTAPI app
from fastapi import APIRouter, Path, Depends, Body  #Depends for dependency injection(autho check, current user info)
from typing import Optional
from datetime import date   #for date filtering in queries
#importing Expense model and RegisterUser model
from models import Expense, RegisterUser, LoginUser
import crud
from authorization import create_access_token, get_current_user, require_admin

#creating a router instance
router = APIRouter()


#Endpoints using the model
#Route to create new expense
@router.post("/expenses/")
#current user(token required)
def create_expense(expense: Expense, current_user: dict = Depends(get_current_user)):
    crud.add_expense(expense, current_user)
    return {"msg": "Expense added"}
#get expenses

#view expenses — only current user's expenses
#requires authentication
@router.get("/expenses/")
def view_expenses(
    start: Optional[date] = None,
    end: Optional[date] = None,
    category: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    #chooses correct crud function based on the filters given:
    user_id = str(current_user["_id"])
    if start and end:
        return crud.get_expenses_by_date_range(start, end, user_id)
    elif category:
        return crud.get_expenses_by_category(category, user_id)
    return crud.get_all_expenses(user_id)   #no filter show all expenses

#route to create category
@router.post("/categories/")
def create_category(name: str, current_user: dict = Depends(require_admin)):
    return crud.add_category(name)
#route to get categories
@router.get("/categories/")
def view_categories(current_user: dict = Depends(get_current_user)):
    return crud.get_categories()

# @router.get("/summary/monthly")
# def monthly_summary():
#     return crud.get_monthly_total()

@router.get("/summary/monthly/{month}")
def total_for_month(
    month: str = Path(description="Month in the format YYYY-MM, e.g., 2025-08"),
    current_user: dict = Depends(get_current_user)
):
    return crud.get_total_for_month(month, str(current_user["_id"]))

# @router.get("/summary/weekly")
# def weekly_summary():
#     return crud.get_weekly_breakdown()

@router.get("/summary/top-categories")
def top_categories(current_user: dict = Depends(get_current_user)):
    return crud.get_top_categories(str(current_user["_id"]))


#registration
@router.post("/auth/register")
def register(user: RegisterUser):
    result = crud.register_user(user.full_name, user.email, user.password)
    return result

#login
@router.post("/auth/login")
def login(user: LoginUser):
    db_user = crud.login_user(user.email, user.password)
    if not db_user:
        return {"detail": "Invalid credentials"}

    #create JWT with "sub" set to the users email
    token_data = {"sub": db_user["email"]}
    access_token = create_access_token(token_data)

    #get role name
    from crud import get_role_name
    role_name = get_role_name(db_user["role_id"])
    #return token, token type and user role
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": role_name
    }

#view users(for admin)
@router.get("/admin/users")
def view_users(current_user: dict = Depends(require_admin)):
    return crud.get_all_users()

#update expenses(for users)
@router.put("/expenses/{expense_id}")
def edit_expense(expense_id: str, updates: dict = Body(...), current_user: dict = Depends(get_current_user)):
    admin = crud.get_role_name(current_user["role_id"]) == "admin"
    return crud.update_expense(expense_id, updates, current_user, admin=admin)

#delete user(admin)
@router.delete("/admin/users/{user_id}")
def remove_user(user_id: str, current_user: dict = Depends(require_admin)):
    return crud.delete_user(user_id)

#update user(admin)
@router.put("/admin/users/{user_id}")
def edit_user(user_id: str, updates: dict, current_user: dict = Depends(require_admin)):
    return crud.update_user(user_id, updates)

#update categories(admin)
@router.put("/categories/{category_id}")
def edit_category(category_id: str, name: str, current_user: dict = Depends(require_admin)):
    return crud.update_category(category_id, name)

#Delete category(admin)
@router.delete("/categories/{category_id}")
def remove_category(category_id: str, current_user: dict = Depends(require_admin)):
    return crud.delete_category(category_id)
