# Database tables and ORM models

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


# Authentication and authorization model
class User(Base):
    __tablename__ = "users"

    # Primary unique user ID
    id = Column(Integer, primary_key=True, index=True)

    # User email for authentication
    email = Column(String, unique=True, index=True, nullable=False)

    # Hashed password storage
    password = Column(String, nullable=False)

    # User role (student, teacher, admin)
    role = Column(String, default="student", nullable=False)

    # One-to-one relationship with student profile
    student_profile = relationship(
        "Student",
        back_populates="user",
        uselist=False
    )


# Student domain model
class Student(Base):
    __tablename__ = "students"

    # Primary student ID
    id = Column(Integer, primary_key=True, index=True)

    # Link student to authenticated user. Foreign key= (connects tables together)
    user_id = Column(Integer, ForeignKey("users.id"))

    # Student academic grade
    grade = Column(String, nullable=False)

    # Optional student full name
    full_name = Column(String, nullable=True)

    # Relationship back to user
    user = relationship(
        "User",
        back_populates="student_profile"
    )


#=================================================================
# FIRST BASIC MODEL FOR A SINGLE USER ROLE (STUDENT) - TO BE EXPANDED WITH TEACHER AND ADMIN ROLES LATER (SCALABLE DESIGN)

# # database tables and models for user authentication and roles
# from sqlalchemy import Column, Integer, String
# from .database import Base


# class User(Base):
#     __tablename__ = "users"

#     # Primary unique user ID
#     id = Column(Integer, primary_key=True, index=True)

#     # User email for authentication
#     email = Column(String, unique=True, index=True, nullable=False)

#     # Hashed password storage
#     password = Column(String, nullable=False)

#     # User role (student, teacher, admin)
#     role = Column(String, default="student", nullable=False)

#     # Student grade/class level
#     grade = Column(String, nullable=True)