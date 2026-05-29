# This file was added to routes/ as the app evolves towards a more modular structure. It contains the routes related to students.

# Student profile management

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Student, User
from ..schemas import (
    StudentCreate,
    StudentUpdate,
    StudentResponse
)
from ..auth import get_current_user

router = APIRouter(prefix="/students", tags=["Students"])


# Create student profile
@router.post("/", response_model=StudentResponse)
def create_student_profile(
    student: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Prevent duplicate student profiles
    existing_profile = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if existing_profile:
        raise HTTPException(
            status_code=400,
            detail="Student profile already exists"
        )

    profile = Student(
        user_id=current_user.id,
        grade=student.grade,
        full_name=student.full_name
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return profile

# Get current student's profile
@router.get("/me", response_model=StudentResponse)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    profile = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    return profile

# Update current student's profile
@router.put("/me", response_model=StudentResponse)
def update_my_profile(
    student_data: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    profile = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    profile.grade = student_data.grade
    profile.full_name = student_data.full_name

    db.commit()
    db.refresh(profile)

    return profile