# Student course enrollment management (PHASE 5.2 Step 5)

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    Enrollment,
    Student,
    Course,
    User
)
from ..schemas import (
    EnrollmentCreate,
    EnrollmentResponse
)
from ..auth import (
    get_current_user,
    require_student
)


router = APIRouter(
    prefix="/enrollments",
    tags=["Enrollments"]
)

# # Verify student role
# def require_student(
#     current_user: User = Depends(get_current_user)  # Authenticated user
# ):

#     if current_user.role != "student":    # Role Authorization (Ensure only students can enroll)
#         raise HTTPException(
#             status_code=403,
#             detail="Student access required"
#         )

#     return current_user


# Enroll in a course
@router.post("/", response_model=EnrollmentResponse)
def enroll_in_course(
    enrollment: EnrollmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student)
):

    student = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    course = db.query(Course).filter(
        Course.id == enrollment.course_id
    ).first()

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
            )
    
    # Prevent duplicate enrollments
    existing_enrollment = db.query(Enrollment).filter(        # Check if the student is already enrolled in the course
        Enrollment.student_id == student.id,
        Enrollment.course_id == enrollment.course_id
    ).first()

    if existing_enrollment:                 # If an enrollment already exists, return a 400 Bad Request error to prevent duplicate enrollments
        raise HTTPException(
            status_code=400,
            detail="Already enrolled in this course"
        )
    
    new_enrollment = Enrollment(
        student_id=student.id,
        course_id=enrollment.course_id
    )

    db.add(new_enrollment)
    db.commit()                   # Persistent enrollment to the database (PostgreSQL)
    db.refresh(new_enrollment)

    return new_enrollment


# Get my enrollments
@router.get("/", response_model=list[EnrollmentResponse])
def get_my_enrollments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student)
):

    student = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == student.id
    ).all()                         # Student to many enrollments relationship (One-to-Many)

    return enrollments


# Drop a course (delete enrollment)
@router.delete("/{enrollment_id}")
def drop_course(
    enrollment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student)
):

    student = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    enrollment = db.query(Enrollment).filter(
        Enrollment.id == enrollment_id
    ).first()

    if not enrollment:
        raise HTTPException(
            status_code=404,
            detail="Enrollment not found"
        )

    # Resource-level authorization
    if enrollment.student_id != student.id:      # Student owns enrollment check (Ensure students can only drop their own enrollments)
        raise HTTPException(
            status_code=403,
            detail="You do not own this enrollment"
        )

    db.delete(enrollment)
    db.commit()

    return {
        "message": "Enrollment deleted successfully"
    }