from data_base import roles_collection
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from data_base import users_collection
from bson import ObjectId
from typing import Optional

# JWT Config
SECRET_KEY = "axel"  # use a long random string(encryption key)
ALGORITHM = "HS256" #hashing algorithm for signing tokens
ACCESS_TOKEN_EXPIRE_MINUTES = 60    #token expires after 60mins

# OAuth2 scheme for reading token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")     #telling fastapi where tokens are.

# Create JWT token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)   
# Get current user from token
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: Optional[str] = payload.get("sub")  # May be None
        
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = users_collection.find_one({"email": email})
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

# Require admin role
def require_admin(current_user: dict = Depends(get_current_user)):
    role = roles_collection.find_one({"_id": ObjectId(current_user["role_id"])})
    if not role or role["name"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return current_user