# This file was added to routes/ as the app evolves towards a more modular structure. It contains the routes related to students.

# Student profile management

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    Student, 
    User,
    Enrollment,
    Course,
    Assignment,
    Submission,
    Grade
) 
from ..schemas import (
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    StudentDashboardResponse,
    MyCourseResponse,
    MyAssignmentResponse,
    AssignmentSubmissionStatusResponse,
    GradeHistoryResponse,
    StudentAnalyticsResponse
)
from ..auth import (
    get_current_user,
    require_student
)

router = APIRouter(
    prefix="/students", 
    tags=["Students"]
)


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


# Student dashboard  [Phase 6.2 step1]
@router.get(
    "/dashboard",
    response_model=StudentDashboardResponse
)
def student_dashboard(
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

    # Count enrolled courses
    total_courses = db.query(Enrollment).filter(
        Enrollment.student_id == student.id
    ).count()

    # Count submissions
    total_submissions = db.query(Submission).filter(
        Submission.student_id == student.id
    ).count()

    # Count grades
    total_grades = db.query(Grade).join(
        Submission
    ).filter(
        Submission.student_id == student.id
    ).count()

    # Count assignments from enrolled courses
    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == student.id
    ).all()

    total_assignments = 0

    for enrollment in enrollments:

        assignment_count = db.query(Assignment).filter(
            Assignment.course_id == enrollment.course_id
        ).count()

        total_assignments += assignment_count

    return {
        "total_courses": total_courses,
        "total_assignments": total_assignments,
        "total_submissions": total_submissions,
        "total_grades": total_grades
    }

# My courses
@router.get(
    "/my-courses",
    response_model=list[MyCourseResponse]
)
def get_my_courses(
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
    ).all()

    results = []

    for enrollment in enrollments:

        course = db.query(Course).filter(
            Course.id == enrollment.course_id
        ).first()

        if course:

            results.append(
                {
                    "course_id": course.id,
                    "title": course.title
                }
            )

    return results


# My assignments
@router.get(
    "/my-assignments",
    response_model=list[MyAssignmentResponse]   # Multiple assignments
)
def get_my_assignments(
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
    ).all()       # All enrolled courses

    results = []

    for enrollment in enrollments:

        assignments = db.query(Assignment).filter(
            Assignment.course_id == enrollment.course_id
        ).all()

        for assignment in assignments:

            results.append(
                {
                    "assignment_id": assignment.id,
                    "title": assignment.title
                }
            )

    return results


# Assignment submission status
@router.get(
    "/assignment-submission-status",
    response_model=list[AssignmentSubmissionStatusResponse]
)
def get_assignment_submission_status(
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
    ).all()

    results = []

    for enrollment in enrollments:

        assignments = db.query(Assignment).filter(
            Assignment.course_id == enrollment.course_id
        ).all()

        for assignment in assignments:

            submission = db.query(Submission).filter(
                Submission.assignment_id == assignment.id,
                Submission.student_id == student.id
            ).first()

            results.append(
                {
                    "assignment_id": assignment.id,
                    "title": assignment.title,
                    "submitted": submission is not None  # Converts submission to "True" if found and "False" if not found
                }
            )

    return results


# Grade history
@router.get(
    "/grade-history",
    response_model=list[GradeHistoryResponse]
)
def get_grade_history(
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

    submissions = db.query(Submission).filter(
        Submission.student_id == student.id
    ).all()

    results = []

    for submission in submissions:

        grade = db.query(Grade).filter(
            Grade.submission_id == submission.id
        ).first()

        if grade:

            results.append(
                {
                    "assignment_id": submission.assignment_id,
                    "grade_value": grade.grade_value,
                    "feedback": grade.feedback
                }
            )

    return results


# Student performance analytics
@router.get(
    "/performance-analytics",
    response_model=StudentAnalyticsResponse
)
def get_performance_analytics(
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

    submissions = db.query(Submission).filter(
        Submission.student_id == student.id
    ).all()

    grades = []

    for submission in submissions:

        grade = db.query(Grade).filter(
            Grade.submission_id == submission.id
        ).first()

        if grade:
            grades.append(grade.grade_value)

    average_grade = 0.0

    if grades:
        average_grade = sum(grades) / len(grades)

    return {
        "student_id": student.id,
        "average_grade": average_grade
    }