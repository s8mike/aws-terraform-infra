# API endpoints for user registration and login

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import UserCreate, UserLogin, UserResponse
from ..auth import hash_password, verify_password, create_token

router = APIRouter()


# Register new user
@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):

    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Create new user
    db_user = User(
        email=user.email,
        password=hash_password(user.password),
        grade=user.grade
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


# Login existing user
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.email == user.email).first()

    # Validate credentials
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    # Generate JWT token
    token = create_token({"sub": db_user.email})

    return {
        "access_token": token,
        "token_type": "bearer"
    }