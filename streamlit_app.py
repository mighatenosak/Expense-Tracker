import streamlit as st
import datetime
import requests
from dotenv import load_dotenv
import os
import time

load_dotenv()
URI = os.getenv("URI")

st.set_page_config(page_title="Expense Tracker", page_icon="🧊", layout="centered")
st.title(":red[_Expense Tracker_]")

# --- Session State ---
if "token" not in st.session_state:
    st.session_state.token = None
if "role" not in st.session_state:
    st.session_state.role = "user"
if "started" not in st.session_state:
    st.session_state.started = False


# --- Helper: Get authorization headers ---
def get_headers():
    """Return Authorization headers if logged in."""
    return {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}


# --- Start screen ---
if not st.session_state.started:
    if st.button("Start Expense Tracker", type="primary"):
        st.session_state.started = True
        st.rerun()

# --- Auth screens ---
elif st.session_state.token is None:
    menu = st.sidebar.selectbox("Menu", ["Login", "Register"])

    if menu == "Register":
        st.subheader(":orange[Register New User]")
        full_name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Register", type="primary"):
            payload = {"full_name": full_name, "email": email, "password": password}
            res = requests.post(f"{URI}/auth/register", json=payload)
            if res.status_code == 200:
                st.success(res.json().get("msg", "Registered successfully"))
            else:
                st.error(res.json().get("error", "Registration failed"))

    elif menu == "Login":
        st.subheader(":orange[Login]")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login", type="primary"):
            payload = {"email": email, "password": password}
            res = requests.post(f"{URI}/auth/login", json=payload)
            if res.status_code == 200 and "access_token" in res.json():
                st.session_state.token = res.json()["access_token"]
                st.session_state.role = res.json().get("role", "user")
                st.success(f"Logged in successfully as {st.session_state.role}!")
                time.sleep(1)
                st.rerun()
            else:
                st.error(res.json().get("detail", "Login failed"))

# --- Logged in screens ---
else:
    # Menu without logout
    menu_options = ["Add Expense", "View Expenses", "Monthly Summary", "Top 3 Categories", "Update Expense"]

    if st.session_state.role == "admin":
        menu_options += [
            "View Users", "Update User", "Delete User",
            "Add Category", "View Categories", "Update Category", "Delete Category"
        ]

    menu = st.sidebar.selectbox("Menu", menu_options)

    # Sidebar logout button
    if st.sidebar.button("Logout", type="primary"):
        st.session_state.token = None
        st.session_state.role = "user"
        st.success("Logged out!")
        time.sleep(1)
        st.rerun()

    # --- Add Expense ---
    if menu == "Add Expense":
        st.subheader(":orange[Add New Expense]")
        category_list = []
        res = requests.get(f"{URI}/categories/", headers=get_headers())
        if res.status_code == 200:
            category_list = [c["name"] for c in res.json()]
        amount = st.number_input("Amount", min_value=0.0, step=0.1)
        category = st.selectbox("Category", category_list)
        exp_date = st.date_input("Date", value=datetime.date.today())
        description = st.text_area("Description (optional)")

        if st.button("Add Expense", type="primary"):
            if not category:
                st.error("Select a category")
            else:
                payload = {"amount": amount, "category": category, "date": str(exp_date), "description": description or None}
                res = requests.post(f"{URI}/expenses/", json=payload, headers=get_headers())
                if res.status_code == 200:
                    st.success(res.json().get("msg", "Expense added"))
                else:
                    st.error("Failed to add expense")

    # --- View Expenses ---
    elif menu == "View Expenses":
        st.subheader(":orange[All Expenses]")
        start_date = st.date_input("Start Date", value=None)
        end_date = st.date_input("End Date", value=None)
        category_filter = st.text_input("Category Filter")
        filters = {}
        if start_date and end_date:
            filters["start"] = str(start_date)
            filters["end"] = str(end_date)
        elif category_filter:
            filters["category"] = category_filter
        if st.button("Get Expenses", type="primary"):
            res = requests.get(f"{URI}/expenses/", params=filters, headers=get_headers())
            if res.status_code == 200:
                st.table(res.json())
            else:
                st.error("Failed to fetch expenses")

    # --- Monthly Summary ---
    elif menu == "Monthly Summary":
        month = st.text_input("Month (YYYY-MM)", value=str(datetime.date.today())[:7])
        if st.button("Get Summary", type="primary"):
            res = requests.get(f"{URI}/summary/monthly/{month}", headers=get_headers())
            if res.status_code == 200:
                st.json(res.json())
            else:
                st.error("Failed to fetch summary")

    # --- Top 3 Categories ---
    elif menu == "Top 3 Categories":
        if st.button("Get Top Categories", type="primary"):
            res = requests.get(f"{URI}/summary/top-categories", headers=get_headers())
            if res.status_code == 200:
                st.table(res.json())
            else:
                st.error("Failed to fetch data")

    # --- Update Expense ---
    elif menu == "Update Expense":
        st.subheader("Update Expense")
        res = requests.get(f"{URI}/expenses/", headers=get_headers())
        if res.status_code == 200:
            expenses = res.json()
            if not expenses:
                st.info("No expenses found.")
            else:
                expense_map = {
                    f"{e.get('date', '')} | {e.get('category', '')} | {e.get('amount', 0)}": e["_id"]
                    for e in expenses
                }
                selected_label = st.selectbox("Select Expense", list(expense_map.keys()))
                amount = st.number_input("New Amount (leave 0 to skip)", min_value=0.0, step=0.1, value=0.0)

                category_list = []
                cat_res = requests.get(f"{URI}/categories/", headers=get_headers())
                if cat_res.status_code == 200:
                    category_list = [cat["name"] for cat in cat_res.json()]
                category_list.insert(0, "")
                category = st.selectbox("New Category (leave blank to skip)", category_list, index=0)

                description = st.text_area("New Description (leave blank to skip)")

                if st.button("Update Expense", type="primary"):
                    updates = {}
                    if amount > 0:
                        updates["amount"] = amount
                    if category and category.strip():
                        updates["category"] = category
                    if description and description.strip():
                        updates["description"] = description

                    if not updates:
                        st.warning("No changes provided. Please fill at least one field to update.")
                    else:
                        expense_id = expense_map[selected_label]
                        res = requests.put(f"{URI}/expenses/{expense_id}", json=updates, headers=get_headers())
                        if res.status_code == 200:
                            st.success("Expense updated")
                        else:
                            st.error(res.json().get("error", "Failed to update expense"))
        else:
            st.error("Failed to load expenses.")

    # --- View Users (Admin) ---
    elif menu == "View Users":
        if st.button("Get Users", type="primary"):
            res = requests.get(f"{URI}/admin/users", headers=get_headers())
            if res.status_code == 200:
                st.table(res.json())
            else:
                st.error("Failed to fetch users")

    # --- Update User (Admin) ---
    elif menu == "Update User":
        res = requests.get(f"{URI}/admin/users", headers=get_headers())
        if res.status_code == 200:
            users = res.json()
            if not users:
                st.info("No users found.")
            else:
                user_map = {
                    f"{u.get('full_name', '')} | {u.get('email', '')} | {u.get('_id', '')}": u["_id"]
                    for u in users
                }
                selected_label = st.selectbox("Select User to Update", list(user_map.keys()))
                full_name = st.text_input("New Full Name")
                email = st.text_input("New Email")
                password = st.text_input("New Password", type="password")
                if st.button("Update User", type="primary"):
                    updates = {}
                    if full_name.strip():
                        updates["full_name"] = full_name
                    if email.strip():
                        updates["email"] = email
                    if password.strip():
                        updates["password"] = password
                    if not updates:
                        st.warning("No changes provided.")
                    else:
                        user_id = user_map[selected_label]
                        res = requests.put(f"{URI}/admin/users/{user_id}", json=updates, headers=get_headers())
                        if res.status_code == 200:
                            st.success("User updated")
                        else:
                            st.error(res.json().get("error", "Failed to update user"))
        else:
            st.error("Failed to load users.")

    # --- Delete User (Admin) ---
    elif menu == "Delete User":
        res = requests.get(f"{URI}/admin/users", headers=get_headers())
        if res.status_code == 200:
            users = res.json()
            if not users:
                st.info("No users found.")
            else:
                user_map = {
                    f"{u.get('full_name', '')} | {u.get('email', '')} | {u.get('_id', '')}": u["_id"]
                    for u in users
                }
                selected_label = st.selectbox("Select User to Delete", list(user_map.keys()))
                if st.button("Delete User", type="primary"):
                    user_id = user_map[selected_label]
                    res = requests.delete(f"{URI}/admin/users/{user_id}", headers=get_headers())
                    if res.status_code == 200:
                        st.success("User deleted")
                    else:
                        st.error(res.json().get("error", "Failed to delete user"))
        else:
            st.error("Failed to load users.")

    # --- Add Category (Admin) ---
    elif menu == "Add Category":
        cat_name = st.text_input("Category Name")
        if st.button("Add Category", type="primary"):
            res = requests.post(f"{URI}/categories/", params={"name": cat_name}, headers=get_headers())
            if res.status_code == 200:
                st.success(res.json().get("msg", "Category added"))
            else:
                st.error("Failed to add category")

    # --- View Categories (Admin) ---
    elif menu == "View Categories":
        if st.button("Get Categories", type="primary"):
            res = requests.get(f"{URI}/categories/", headers=get_headers())
            if res.status_code == 200:
                st.table(res.json())
            else:
                st.error("Failed to fetch categories")

    # --- Update Category (Admin) ---
    elif menu == "Update Category":
        res = requests.get(f"{URI}/categories/", headers=get_headers())
        if res.status_code == 200:
            categories = res.json()
            if not categories:
                st.info("No categories found.")
            else:
                category_map = {
                    f"{c.get('name', '')} | {c.get('_id', '')}": c["_id"]
                    for c in categories
                }
                selected_label = st.selectbox("Select Category to Update", list(category_map.keys()))
                new_name = st.text_input("New Category Name")
                if st.button("Update Category", type="primary"):
                    if not new_name.strip():
                        st.warning("Please enter a new category name.")
                    else:
                        cat_id = category_map[selected_label]
                        res = requests.put(f"{URI}/categories/{cat_id}", params={"name": new_name}, headers=get_headers())
                        if res.status_code == 200:
                            st.success("Category updated")
                        else:
                            st.error(res.json().get("error", "Failed to update category"))
        else:
            st.error("Failed to load categories.")

    # --- Delete Category (Admin) ---
    elif menu == "Delete Category":
        res = requests.get(f"{URI}/categories/", headers=get_headers())
        if res.status_code == 200:
            categories = res.json()
            if not categories:
                st.info("No categories found.")
            else:
                category_map = {
                    f"{c.get('name', '')} | {c.get('_id', '')}": c["_id"]
                    for c in categories
                }
                selected_label = st.selectbox("Select Category to Delete", list(category_map.keys()))
                if st.button("Delete Category", type="primary"):
                    cat_id = category_map[selected_label]
                    res = requests.delete(f"{URI}/categories/{cat_id}", headers=get_headers())
                    if res.status_code == 200:
                        st.success("Category deleted")
                    else:
                        st.error(res.json().get("error", "Failed to delete category"))
        else:
            st.error("Failed to load categories.")
