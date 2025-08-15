# Expense-Tracker
<p>1. Backend Structure (FastAPI)
A sleek and simple expense tracker — effortlessly CRUD your spendings on MongoDB with an intuitive interface with streamlit and real-time insights.

main.py – Entry point that starts FastAPI and includes routes.

routes.py – All endpoints (expenses, categories, summaries, auth, admin actions).

crud.py – Core database operations (add, update, delete, get).

authorization.py – JWT token creation, user authentication, admin checks.

admin_.py – Script to create a default admin user.

models.py – Pydantic schemas for request validation.

data_base.py – MongoDB connection setup.

2. Frontend (Streamlit)

streamlit_app.py – User interface for login, registration, adding/viewing/updating expenses, admin features (manage users, categories).

3. Features Implemented

User Authentication (JWT-based)

Role-based Access (admin vs user)

Expense Management (CRUD)

Category Management (CRUD, admin only)

Summary Reports (monthly totals, top 3 categories)

Filters (by date range, category)

Streamlit UI with different menus for admin and normal users</pr>
<br>
<br>
Author - Salman Ali Khan