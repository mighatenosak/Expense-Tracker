import streamlit as st
import datetime
import  requests
from dotenv import load_dotenv
import os
import time
#load dotenv
load_dotenv()

#load URI from .env
URI=os.getenv("URI")

#page config
st.set_page_config(page_title="Expense Tracker",page_icon="🧊", layout="centered")
st.title(":red[_Expense Tracker_]")

#initialize session state
#in streamlit, every time the user interacts with the app clicks a button or changes an input, the script reruns from top to bottom
#and we didn’t store the token in st.session_state, it would be lost on every rerun — meaning the user would get logged out after any interaction.

if "token" not in st.session_state: 
    st.session_state.token = None
if "started" not in st.session_state:
    st.session_state.started = False

# if not started, just show start button
if not st.session_state.started:
    if st.button("Start Expense Tracker",type="primary"):
        st.session_state.started = True
        st.rerun()
elif st.session_state.token is None:
    #only show login/register if not logged in
    menu = st.sidebar.selectbox(
        "Menu",
        ["Login", "Register"]
    )
    #register section
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
        pass
    #login
    elif menu == "Login":
        st.subheader(":orange[Login]")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login", type="primary"):
            payload = {"email": email, "password": password}
            res = requests.post(f"{URI}/auth/login", json=payload)
            if res.status_code == 200 and "access_token" in res.json():
                st.session_state.token = res.json().get("access_token")
                st.session_state.role = res.json().get("role", "user")
                st.success(f"Logged in successfully as {st.session_state.role}!")
                time.sleep(1)
                st.rerun()
            else:
                st.error(res.json().get("detail", "Login failed"))


else:
    # if st.session_state.token:
        #sidebar menu to switch between different sections
    menu_options = ["Add Expense", "View Expenses", "Monthly Summary", "Top 3 Categories","Logout"]

    if st.session_state.token:
        menu_options = ["Add Expense", "View Expenses", "Monthly Summary", "Top 3 Categories","Logout"]
    if st.session_state.get("role") == "admin":
        menu_options.insert(2, "Add Category")
        menu_options.insert(3, "View Categories")

    menu = st.sidebar.selectbox("Menu", menu_options)

 

    # else:
    #     menu = st.sidebar.selectbox(
    #         "Menu",
    #         ["Login", "Register"]
    #     )

    #add expense
    # if menu=="Add Expense":
    #     st.subheader(":orange[Add New Expense]")
    #     amount=st.number_input("Amount",min_value=0,step=1, placeholder="Enter an Amount")    #only +ve amount
    #     category = st.text_input("Category",placeholder="Enter the Category")
    #     exp_date = st.date_input("Date", value=datetime.date.today())  #default = today
    #     description = st.text_area("Description (optional)")    #multi-line text input widget

    #     if st.button("Add Expense",type="primary"):
    #         #payload to send to backend
    #         loadexpense = {
    #             "amount": amount,
    #             "category": category,
    #             "date": str(exp_date),
    #             "description": description if description else None
    #         }
    #         res = requests.post(f"{URI}/expenses/", json=loadexpense)
    #         st.success(res.json().get("msg", "Expense added"))

    # add expense
    # if menu == "Add Expense":
    #     st.subheader(":orange[Add New Expense]")

    #     # Fetch categories from backend
    #     cat_res = requests.get(f"{URI}/categories/")
    #     if cat_res.status_code == 200:
    #         categories_data = cat_res.json()
    #         category_list = [cat["name"] for cat in categories_data] if categories_data else []
    #     else:
    #         st.error("Failed to load categories from database.")
    #         category_list = []

    #     amount = st.number_input("Amount", min_value=0, step=1, placeholder="Enter an Amount")

    if menu == "Add Expense":
        st.subheader(":orange[Add New Expense]")

        category_list = []
        try:
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            cat_res = requests.get(f"{URI}/categories/", headers=headers)
            if cat_res.status_code == 200:
                categories_data = cat_res.json()
                category_list = [cat["name"] for cat in categories_data] if categories_data else []
            elif cat_res.status_code == 403:
                st.warning("You do not have permission to view categories. Please ask an admin to add them.")
            else:
                st.error("Failed to load categories from database.")
        except Exception as e:
            st.error(f"Error fetching categories: {e}")

        amount = st.number_input("Amount", min_value=0, step=1, placeholder="Enter an Amount")
        category = st.selectbox("Category", category_list)
        exp_date = st.date_input("Date", value=datetime.date.today())
        description = st.text_area("Description (optional)")

        if st.button("Add Expense", type="primary"):
            if not category:
                st.error("Please select a category before adding expense.")
            else:
                loadexpense = {
                    "amount": amount,
                    "category": category,
                    "date": str(exp_date),
                    "description": description if description else None
                }
                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                res = requests.post(f"{URI}/expenses/", json=loadexpense, headers=headers)
                if res.status_code == 200:
                    st.success(res.json().get("msg", "Expense added"))
                else:
                    st.error("Failed to add expense.")

    # view all expenses section (with filters)
    elif menu == "View Expenses":
        st.subheader(":orange[All Expenses]")
        start_date = st.date_input("Start Date", value=None)
        end_date = st.date_input("End Date", value=None)
        category_filter = st.text_input("Filter by Category")

        filters = {}
        if start_date and end_date:
            filters["start"] = str(start_date)
            filters["end"] = str(end_date)
        elif category_filter:
            filters["category"] = category_filter

        if st.button("Get Expenses", type="primary"):
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            res = requests.get(f"{URI}/expenses/", params=filters, headers=headers)
            if res.status_code == 200:
                st.table(res.json())
            else:
                st.error("Failed to fetch expenses.")


    # add new category section
    elif menu == "Add Category":
        st.subheader(":orange[Add New Category]")
        category_name = st.text_input("Category Name", placeholder="Enter a Valid Category")
        if st.button("Add Category", type="primary"):
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            res = requests.post(f"{URI}/categories/", params={"name": category_name}, headers=headers)
            if res.status_code == 200:
                st.success(res.json().get("msg", "Category added"))
            else:
                st.error(f"Failed to add category. Status {res.status_code}: {res.text}")

    #view all categories
    elif menu == "View Categories":
        st.subheader(":orange[All Categories]")
        if st.button("Get Categories", type="primary"):
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            res = requests.get(f"{URI}/categories/", headers=headers)
            if res.status_code == 200:
                st.table(res.json())
            else:
                st.error(f"Failed to fetch categories. Status {res.status_code}: {res.text}")


    #monthly total section
    elif menu == "Monthly Summary":
        st.subheader(":orange[Monthly Total Summary]")
        month = st.text_input("Enter Month (YYYY-MM)", value=str(datetime.date.today())[:7])  
        if st.button("Get Monthly Total", type="primary"):
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            res = requests.get(f"{URI}/summary/monthly/{month}", headers=headers)
            if res.status_code == 200:
                st.json(res.json())
            else:
                st.error(f"Failed to fetch monthly summary. Status {res.status_code}: {res.text}")


    #top 3 categories section
    elif menu == "Top 3 Categories":
        st.subheader(":orange[Top 3 Spending Categories]")
        if st.button("Get Top 3 Categories",type="primary"):
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            res = requests.get(f"{URI}/summary/top-categories", headers=headers)

            if res.status_code == 200:
                st.table(res.json())
            else:
                st.error("Failed to fetch top categories.")

    #logout
    elif menu=="Logout":
        st.session_state.token= None
        st.success("Logged out!")
        # time.sleep(1)
        st.rerun()