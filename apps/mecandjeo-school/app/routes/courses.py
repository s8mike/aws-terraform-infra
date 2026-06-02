# Course management   (Phase 5.2-Step-4)

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Course, Teacher, User
from ..schemas import (
    CourseCreate,
    CourseUpdate,
    CourseResponse
)
from ..auth import get_current_user

router = APIRouter(
    prefix="/courses",
    tags=["Courses"]
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

# Create course
@router.post("/", response_model=CourseResponse)
def create_course(
    course: CourseCreate,
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

    new_course = Course(
        teacher_id=teacher.id,
        title=course.title,
        description=course.description
    )

    db.add(new_course)
    db.commit()
    db.refresh(new_course)

    return new_course

# Get all courses owned by current teacher
@router.get("/", response_model=list[CourseResponse])
def get_my_courses(
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

    courses = db.query(Course).filter(
        Course.teacher_id == teacher.id
    ).all()

    return courses

# Update course (Teachers can only update their own courses - ownership validation)
@router.put("/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: int,
    course: CourseUpdate,
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

    existing_course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if not existing_course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    # Ownership validation
    if existing_course.teacher_id != teacher.id:
        raise HTTPException(
            status_code=403,
            detail="You do not own this course"
        )

    existing_course.title = course.title
    existing_course.description = course.description

    db.commit()
    db.refresh(existing_course)

    return existing_course


# Delete course (Teachers can only delete their own courses - ownership validation)
@router.delete("/{course_id}")
def delete_course(
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
    if course.teacher_id != teacher.id:
        raise HTTPException(
            status_code=403,
            detail="You do not own this course"
        )

    db.delete(course)
    db.commit()

    return {
        "message": "Course deleted successfully"
    }