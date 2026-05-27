# validation schemas for user registration and login, ensuring data integrity and security best practices.
from pydantic import BaseModel, EmailStr
from typing import Optional


# Base shared user fields
class UserBase(BaseModel):
    email: EmailStr                    # validate proper email format
    grade: Optional[str] = None


# Schema for creating new users
class UserCreate(UserBase):
    password: str


# Schema for login requests
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Schema returned from API responses
class UserResponse(UserBase):        # Password is intentionally excluded from response schema
    id: int
    role: str

    class Config:
        from_attributes = True  # allows Pydantic to read data from ORM models directly, enabling seamless integration with SQLAlchemy models.
