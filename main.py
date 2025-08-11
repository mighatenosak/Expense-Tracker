#ENTRY POINT (FASTAPI APP)
from fastapi import FastAPI

#We import all endpoints from routes.py
from routes import router  
app = FastAPI(title="Daily Expense Tracker")

#This makes all routes active
app.include_router(router) 
