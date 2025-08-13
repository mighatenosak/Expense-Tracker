# mongodb collections
from data_base import roles_collection, users_collection
from passlib.context import CryptContext    #for password hashing
# working with mongodbs _id fields
from bson import ObjectId

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")   #'auto' means old hashes can be rehashed if outdated.

def create_admin_user(email: str, password: str, full_name: str = "Admin User"):
    # ensure admin role exists
    role = roles_collection.find_one({"name": "admin"})
    if not role:
        role_id = roles_collection.insert_one({"name": "admin"}).inserted_id
        print(f"Admin role created: {role_id}")
    else:
        role_id = role["_id"]
        print(f"Admin role already exists: {role_id}")

    # check if user already exists
    if users_collection.find_one({"email": email}):
        print(f"User with email {email} already exists.")
        return

    # create admin user
    users_collection.insert_one({
        "full_name": full_name,
        "email": email,
        "password_hash": pwd_context.hash(password),
        "role_id": ObjectId(role_id)
    })
    print(f"Admin user created: {email} / {password}")

if __name__ == "__main__":
    # change these values if you want a different admin account
    create_admin_user(
        email="admin@gmail.com",
        password="admin123",
        full_name="Admin"
    )
