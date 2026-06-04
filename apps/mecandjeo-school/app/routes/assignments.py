# Assignment management (PHASE 5.2 Step 6)

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    Assignment,
    Course,
    Teacher,
    User
)
from ..schemas import (
    AssignmentCreate,
    AssignmentResponse
)
from ..auth import get_current_user

# imports
router = APIRouter(
    prefix="/assignments",
    tags=["Assignments"]
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


# Create assignment
@router.post("/", response_model=AssignmentResponse)
def create_assignment(
    course_id: int,
    assignment: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)  # Ensure only teachers can create assignments
):

    teacher = db.query(Teacher).filter(            # Authenticated teacher actually has a teacher profile
        Teacher.user_id == current_user.id
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found"
        )

    course = db.query(Course).filter(                # Ensure the course exists before creating assignment
        Course.id == course_id
    ).first()

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    # Resource-level authorization
    if course.teacher_id != teacher.id:     # Ensure the authenticated teacher actually owns the course. != means "not equal to"
        raise HTTPException(
            status_code=403,
            detail="You do not own this course"
        )

    new_assignment = Assignment(
        course_id=course.id,
        title=assignment.title,
        description=assignment.description
    )

    db.add(new_assignment)
    db.commit()      # Persist assignment to PostgreSQL
    db.refresh(new_assignment)

    return new_assignment


# Get assignments for a course
@router.get("/", response_model=list[AssignmentResponse])
def get_course_assignments(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Allow both teachers and students to view assignments. Only teachers can create,update, and delete assignments. Students can only view assignments they are enrolled in.
):

    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    assignments = db.query(Assignment).filter(
        Assignment.course_id == course_id
    ).all()                                      # Allow authenticated users to view assignments. Enrollment -based access control can be implemented in the future if needed

    return assignments


# Update assignment
@router.put("/{assignment_id}", response_model=AssignmentResponse)
def update_assignment(
    assignment_id: int,
    assignment: AssignmentCreate,
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

    existing_assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id
    ).first()

    if not existing_assignment:
        raise HTTPException(
            status_code=404,
            detail="Assignment not found"
        )

    course = db.query(Course).filter(
        Course.id == existing_assignment.course_id
    ).first()

    # Resource-level authorization
    if course.teacher_id != teacher.id:
        raise HTTPException(
            status_code=403,
            detail="You do not own this assignment"
        )

    existing_assignment.title = assignment.title
    existing_assignment.description = assignment.description

    db.commit()                # Persist updates to PostgreSQL
    db.refresh(existing_assignment)

    return existing_assignment

# Delete assignment
@router.delete("/{assignment_id}")
def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)  # Role authorization to ensure only teachers can delete assignments
):

    teacher = db.query(Teacher).filter(
        Teacher.user_id == current_user.id
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found"
        )

    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=404,
            detail="Assignment not found"
        )

    course = db.query(Course).filter(
        Course.id == assignment.course_id
    ).first()

    # Resource-level authorization
    if course.teacher_id != teacher.id:     # Ensure the authenticated teacher actually owns the course that the assignment belongs to. Only the teacher who owns the course can delete assignments for that course.
        raise HTTPException(
            status_code=403,
            detail="You do not own this assignment"
        )

    db.delete(assignment)
    db.commit()       # Permanently remove assignment from PostgreSQL

    return {
        "message": "Assignment deleted successfully"
    }