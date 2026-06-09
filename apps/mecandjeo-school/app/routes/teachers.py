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
    Enrollment,  # Enrollment model is imported for phase 6.1 step 2 to query the students enrolled in a specific course for the course roster endpoint.
    Student,     # Student model is imported for phase 6.1 step 2 to query the students enrolled in a specific course for the course roster endpoint.
    User
)
from ..schemas import (     # imports from schemas.py [all teacher-related schemas are imported for teacher profile management endpoints.]
    TeacherCreate,
    TeacherUpdate,
    TeacherResponse,
    TeacherDashboardResponse,  # TeacherDashboardResponse is imported for phase 6.1 step 1. This schema defines the structure of the response for the teacher dashboard endpoint, which includes statistics about courses, assignments, submissions, and grades.
    CourseRosterResponse
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


# Course roster
@router.get(
    "/course-roster",
    response_model=list[CourseRosterResponse]
)
def get_course_roster(
    course_id: int,
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

    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    # Ownership validation
    if course.teacher_id != teacher.id: # Ownership validation is performed by comparing the teacher_id of the course with the id of the currently authenticated teacher. If they do not match, it means the teacher does not own the course.
        raise HTTPException(
            status_code=403,
            detail="You do not own this course"
        )

    enrollments = db.query(Enrollment).filter(  # Query the Enrollment table to get all enrollments for the specified course_id.
        Enrollment.course_id == course_id
    ).all()

    roster = []

    for enrollment in enrollments:

        roster.append(
            {
                "student_id": enrollment.student_id
            }
        )

    return roster