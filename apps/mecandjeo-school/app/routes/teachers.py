# Teacher profile management

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Teacher, User
from ..schemas import (
    TeacherCreate,
    TeacherUpdate,
    TeacherResponse
)
from ..auth import get_current_user


router = APIRouter(
    prefix="/teachers",
    tags=["Teachers"]
)

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


# Create teacher profile
@router.post("/", response_model=TeacherResponse)
def create_teacher_profile(
    teacher: TeacherCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)  # current_user: User = Depends(get_current_user) (Protect teacher creation)
):

    # Prevent duplicate teacher profiles
    existing_profile = db.query(Teacher).filter(
        Teacher.user_id == current_user.id
    ).first()

    if existing_profile:
        raise HTTPException(
            status_code=400,
            detail="Teacher profile already exists"
        )

    profile = Teacher(
        user_id=current_user.id,
        full_name=teacher.full_name,
        subject=teacher.subject
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return profile

# Get current teacher profile
@router.get("/me", response_model=TeacherResponse)
def get_my_teacher_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    profile = db.query(Teacher).filter(
        Teacher.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found"
        )

    return profile

# Update current teacher profile
@router.put("/me", response_model=TeacherResponse)
def update_my_teacher_profile(
    teacher: TeacherUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    profile = db.query(Teacher).filter(
        Teacher.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found"
        )

    profile.full_name = teacher.full_name
    profile.subject = teacher.subject

    db.commit()               # commit or save changes to the database
    db.refresh(profile)       # return the updated profile from the database

    return profile