import streamlit as st
import datetime
import  requests
from dotenv import load_dotenv
import os
#load dotenv
load_dotenv()

#load URI from .env
URI=os.getenv("URI")

#page config
st.set_page_config(page_title="Expense Tracker",page_icon="🧊", layout="centered")
st.title(":red[_Expense Tracker_]")

if "started" not in st.session_state:
    st.session_state.started = False

# if not started, just show start button
if not st.session_state.started:
    if st.button("Start Expense Tracker",type="primary"):
        st.session_state.started = True
        st.rerun()
else:

    #sidebar menu to switch between different sections
    menu = st.sidebar.selectbox(
        "Menu",
        ["Add Expense", "View Expenses", "Add Category", "View Categories", "Monthly Summary", "Top 3 Categories"]
    )

    #add expense
    if menu=="Add Expense":
        st.subheader(":orange[Add New Expense]")
        amount=st.number_input("Amount",min_value=0,step=1, placeholder="Enter an Amount")    #only +ve amount
        category = st.text_input("Category",placeholder="Enter the Category")
        exp_date = st.date_input("Date", value=datetime.date.today())  #default = today
        description = st.text_area("Description (optional)")    #multi-line text input widget

        if st.button("Add Expense",type="primary"):
            #payload to send to backend
            loadexpense = {
                "amount": amount,
                "category": category,
                "date": str(exp_date),
                "description": description if description else None
            }
            res = requests.post(f"{URI}/expenses/", json=loadexpense)
            st.success(res.json().get("msg", "Expense added"))

    # view all expenses section (with filters)
    elif menu=="View Expenses":
        st.subheader(":orange[All Expenses]")
        start_date = st.date_input("Start Date", value=None)  # leave empty for no filter
        end_date = st.date_input("End Date", value=None)
        category_filter = st.text_input("Filter by Category")

        #build filters only if values are given
        filters = {}
        if start_date and end_date:
            filters["start"] = str(start_date)
            filters["end"] = str(end_date)
        elif category_filter:
            filters["category"] = category_filter

        
        if st.button("Get Expenses",type="primary"):
            #params is a special keyword argument in the requests library that lets you send query parameters in a GET request.
            res = requests.get(f"{URI}/expenses/", params=filters)
            if res.status_code == 200:
                st.table(res.json())  #showing as table
            else:
                st.error("Failed to fetch expenses.")

    # add new category section
    elif menu == "Add Category":
        st.subheader(":orange[Add New Category]")
        category_name = st.text_input("Category Name",placeholder="Enter a Valid Category")
        if st.button("Add Category",type="primary"):
            res = requests.post(f"{URI}/categories/", params={"name": category_name})
            st.success(res.json().get("msg", "Category added"))

    #view all categories
    elif menu == "View Categories":
        st.subheader(":orange[All Categories]")
        if st.button("Get Categories",type="primary"):
            res = requests.get(f"{URI}/categories/")
            if res.status_code == 200:
                st.table(res.json())
            else:
                st.error("Failed to fetch categories.")

    #monthly total section
    elif menu == "Monthly Summary":
        st.subheader(":orange[Monthly Total Summary]")
        month = st.text_input("Enter Month (YYYY-MM)", value=str(datetime.date.today())[:7])  # default current month
        if st.button("Get Monthly Total",type="primary"):
            res = requests.get(f"{URI}/summary/monthly/{month}")
            if res.status_code == 200:
                st.json(res.json())
            else:
                st.error("Failed to fetch monthly summary.")

    #top 3 categories section
    elif menu == "Top 3 Categories":
        st.subheader(":orange[Top 3 Spending Categories]")
        if st.button("Get Top 3 Categories",type="primary"):
            res = requests.get(f"{URI}/summary/top-categories")
            if res.status_code == 200:
                st.table(res.json())
            else:
                st.error("Failed to fetch top categories.")