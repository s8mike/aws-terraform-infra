# Security utilities for password hashing and JWT token management
#backend can identify authenticated users

from passlib.context import CryptContext
from fastapi import Depends, HTTPException  
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt
import os

from .database import get_db
from .models import User

# Secret key used for JWT signing
SECRET = os.getenv("SECRET_KEY", "secret")

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"])

# OAuth2 bearer token extraction [extracts JWT token from requests]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")


# Hash plain password
def hash_password(password: str):
    return pwd_context.hash(password)


# Verify password against stored hash
def verify_password(password, hashed):
    return pwd_context.verify(password, hashed)


# Create JWT token
def create_token(data: dict):
    return jwt.encode(data, SECRET, algorithm="HS256")


# Decode and validate JWT token [checks if JWT token is valid]
def verify_token(token: str):

    try:
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        return payload

    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


# Extract currently authenticated user [identifies logged-in user]
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    payload = verify_token(token)

    email = payload.get("sub")

# returns proper API errors if user is not found or token is invalid
    if not email:
        raise HTTPException(
            status_code=401,
            detail="Invalid token payload"
        )

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(                    
            status_code=404,
            detail="User not found"
        )

    return user



###########################################################################################
## Early Starting Version with users having all permissions and no authentication.
#Backend trusted everyone.

# # Security utilities for password hashing and JWT token creation
# from passlib.context import CryptContext
# import jwt
# import os

# SECRET = os.getenv("SECRET_KEY", "secret")

# pwd_context = CryptContext(schemes=["bcrypt"])

# def hash_password(password: str):
#     return pwd_context.hash(password)

# def verify_password(password, hashed):
#     return pwd_context.verify(password, hashed)

# def create_token(data: dict):
#     return jwt.encode(data, SECRET, algorithm="HS256")