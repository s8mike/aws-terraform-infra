# Security utilities for password hashing and JWT token management
# Backend authentication and authorization utilities.
# Provides password hashing, JWT management,
# authenticated user retrieval, and role validation

from passlib.context import CryptContext
from fastapi import Depends, HTTPException  
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt

from .database import get_db
from .models import User
from datetime import datetime, timedelta
from .logger import logger   # added at phase 12.1 step 5

# Secret key used for JWT signing
from .config import (
    SECRET_KEY,
    JWT_EXPIRE_HOURS
)

ALGORITHM = "HS256"

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"])

# OAuth2 bearer token extraction [extracts JWT token from requests]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

#============================================
# AUTHENTICATION FUNCTIONS
#============================================

# Hash plain password
def hash_password(password: str):
    return pwd_context.hash(password)


# Verify password against stored hash
def verify_password(password, hashed):
    return pwd_context.verify(password, hashed)


# Create JWT token for a User and to expire after certain hours [Modified at phase 12.1 step 2]
def create_token(data: dict): # Fxn expects a dictionary

    payload = data.copy()

    expire = (
        datetime.utcnow()       # Current UTC time and date [utc=coordinated universal time]
        + timedelta(hours=JWT_EXPIRE_HOURS)
    )

    payload["exp"] = expire  # add an expiration field to JWT payload

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

# Decode and validate JWT token [checks if JWT token is valid]
def verify_token(token: str):

    try:
        payload = jwt.decode(
            token, 
            SECRET_KEY, 
            algorithms=[ALGORITHM]
        )
        return payload

    except jwt.PyJWTError:

        logger.warning(
            "Authentication failed due to an invalid or expired JWT."
        )    
        raise HTTPException(
            status_code=401,
            detail="Authentication failed"
        )


# Extract currently authenticated user [identifies logged-in user]
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    payload = verify_token(token)

    email = payload.get("sub")

# Returns proper API errors if user is not found 
# or token payload is invalid
    if not email:
        raise HTTPException(
            status_code=401,
            detail="Authentication failed"
        )

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(                    
            status_code=401,
            detail="Authentication failed"
        )

    return user

# ==========================================================
# ROLE AUTHORIZATION HELPERS [AUTHORIZATION FUNCTIONS]
# ==========================================================
# These helper functions are centralized in auth.py to avoid
# duplicating role-validation logic across multiple route files.
# It acts as a single source of truth
#
# Before this refactor:
# - teachers.py defined require_teacher()
# - grades.py defined require_student() and require_teacher()
# - submissions.py defined require_student()
# - enrollments.py defined require_student()
# - students.py defined require_student()

#
# This follows the Separation of Concerns principle used in
# professional FastAPI applications.
# ==========================================================


# Verify teacher role
def require_teacher(
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "teacher":
        raise HTTPException(
            status_code=403,
            detail="Teacher access required"
        )

    return current_user


# Verify student role
def require_student(
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "student":
        raise HTTPException(
            status_code=403,
            detail="Student access required"
        )

    return current_user


# Verify admin role
def require_admin(
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return current_user

# Verify Parent authorization

def require_parent(
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "parent":
        raise HTTPException(
            status_code=403,
            detail="Parent access required"
        )

    return current_user


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
#     return jwt.encode(data, SECRET, algorithm="ALGORITHM")