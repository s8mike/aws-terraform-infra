# Security utilities for password hashing and JWT token management
# Backend authentication and authorization utilities.
# Provides password hashing, JWT management,
# authenticated user retrieval, and role validation

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

#============================================
# AUTHENTICATION FUNCTIONS
#============================================

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

# Returns proper API errors if user is not found 
# or token payload is invalid
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

# ==========================================================
# ROLE AUTHORIZATION HELPERS [AUTHORIZATION FUNCTIONS]
# ==========================================================
# These helper functions are centralized in auth.py to avoid
# duplicating role-validation logic across multiple route files.
#
# Before this refactor:
# - teachers.py defined require_teacher()
# - grades.py defined require_student() and require_teacher()
# - submissions.py defined require_student()
# - enrollments.py defined require_student()
# - students.py defined require_student()
#
# Centralizing them here provides:
#
# 1. Single Source of Truth
#    Any role validation change is made once.
#
# 2. Easier Maintenance
#    Prevents inconsistent authorization logic across files.
#
# 3. Better Scalability
#    Future roles such as:
#    - admin
#    - head_teacher
#    - department_head
#    can be managed centrally.
#
# 4. Cleaner Route Files
#    Route files focus on business logic while auth.py
#    handles authentication and authorization concerns.
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