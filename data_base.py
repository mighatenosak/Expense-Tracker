#MONGODB CONNECTION

from pymongo import MongoClient
from dotenv import load_dotenv
import os
#Load dotenv
load_dotenv()

#Loading the MONGO_URI

MONGO_URI=os.getenv("MONGO_URI")

#checking if the uri was loaded
if not MONGO_URI:
    raise Exception("MONGO_URI was not found in environment variables.")

#connect to MONGODB
client = MongoClient(MONGO_URI)

#Creating database
db = client["expense_tracker"]


#Main collection
expenses_collection = db["expenses"]  
categories_collection = db["category"]