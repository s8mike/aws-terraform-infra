# Teacher profile management

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    Teacher,
    Course,   # course, assignment, submission, grade models are imported for phase 6.1 step 1. Records are counted from these tables to display stats on the teacher dashboard
    Assignment,
    Submission,
    Grade,
    User
)
from ..schemas import (
    TeacherCreate,
    TeacherUpdate,
    TeacherResponse,
    TeacherDashboardResponse  # TeacherDashboardResponse is imported for phase 6.1 step 2. This schema defines the structure of the response for the teacher dashboard endpoint, which includes statistics about courses, assignments, submissions, and grades.
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


# Teacher dashboard [phase 6.1 step 2: This endpoint provides a dashboard for teachers, showing statistics about their courses, assignments, submissions, and grades. It queries the database to count the relevant records and returns them in a structured response defined by TeacherDashboardResponse schema.]
@router.get(
    "/dashboard",
    response_model=TeacherDashboardResponse
)
def teacher_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):

    teacher = db.query(Teacher).filter(
        Teacher.user_id == current_user.id
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found"
        )

    # Count teacher courses
    total_courses = db.query(Course).filter(
        Course.teacher_id == teacher.id
    ).count()

    # Count assignments belonging to teacher's courses
    total_assignments = db.query(Assignment).join(
        Course
    ).filter(
        Course.teacher_id == teacher.id
    ).count()

    # Count submissions for teacher assignments
    total_submissions = db.query(Submission).join(
        Assignment
    ).join(
        Course
    ).filter(
        Course.teacher_id == teacher.id
    ).count()

    # Count grades for teacher submissions
    total_grades = db.query(Grade).join(      # "join" means connect related tables together based on their relationships.
        Submission
    ).join(
        Assignment
    ).join(
        Course
    ).filter(
        Course.teacher_id == teacher.id
    ).count()

    return {
        "total_courses": total_courses,
        "total_assignments": total_assignments,
        "total_submissions": total_submissions,
        "total_grades": total_grades
    }