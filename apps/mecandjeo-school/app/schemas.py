# Validation schemas for authentication and school-domain entities

from pydantic import BaseModel, EmailStr
from typing import Optional


# ==========================================================
# USER AUTHENTICATION SCHEMAS (All user-related schemas, including registration, login, and API responses)
# ==========================================================

# Shared user fields 
class UserBase(BaseModel):
    email: EmailStr


# User registration
class UserCreate(UserBase):
    password: str


# User login
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# User API response
class UserResponse(UserBase):
    id: int
    role: str

    class Config:
        from_attributes = True


# ==========================================================
# STUDENT DOMAIN SCHEMAS
# ==========================================================

# Shared student fields
class StudentBase(BaseModel):
    grade: str
    full_name: Optional[str] = None


# Create student profile
class StudentCreate(StudentBase):
    pass


# Update student profile
class StudentUpdate(StudentBase):
    pass


# Student API response
class StudentResponse(StudentBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True






## Starting Point for Schemas.
# # validation schemas for user registration and login, ensuring data integrity and security best practices.
# from pydantic import BaseModel, EmailStr
# from typing import Optional


# # Base shared user fields
# class UserBase(BaseModel):
#     email: EmailStr                    # validate proper email format
#     grade: Optional[str] = None


# # Schema for creating new users
# class UserCreate(UserBase):
#     password: str


# # Schema for login requests
# class UserLogin(BaseModel):
#     email: EmailStr
#     password: str


# # Schema returned from API responses
# class UserResponse(UserBase):        # Password is intentionally excluded from response schema
#     id: int
#     role: str

#     class Config:
#         from_attributes = True  # allows Pydantic to read data from ORM models directly, enabling seamless integration with SQLAlchemy models.
