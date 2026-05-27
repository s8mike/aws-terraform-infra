# database tables and models for user authentication and roles
from sqlalchemy import Column, Integer, String
from .database import Base


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

    # Student grade/class level
    grade = Column(String, nullable=True)