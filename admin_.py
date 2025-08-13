from data_base import roles_collection, users_collection
from passlib.context import CryptContext
from bson import ObjectId

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin_user(email: str, password: str, full_name: str = "Admin User"):
    # Step 1: Ensure admin role exists
    role = roles_collection.find_one({"name": "admin"})
    if not role:
        role_id = roles_collection.insert_one({"name": "admin"}).inserted_id
        print(f"Admin role created: {role_id}")
    else:
        role_id = role["_id"]
        print(f"Admin role already exists: {role_id}")

    # Step 2: Check if user already exists
    if users_collection.find_one({"email": email}):
        print(f"User with email {email} already exists.")
        return

    # Step 3: Create admin user
    users_collection.insert_one({
        "full_name": full_name,
        "email": email,
        "password_hash": pwd_context.hash(password),
        "role_id": ObjectId(role_id)
    })
    print(f"Admin user created: {email} / {password}")

if __name__ == "__main__":
    # Change these values if you want a different admin account
    create_admin_user(
        email="admin@gmail.com",
        password="admin123",
        full_name="Admin"
    )
