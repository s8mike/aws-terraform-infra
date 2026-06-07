# Grade management (PHASE 5.2 Step 8)

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    Grade,
    Submission,
    Teacher,
    User
)
from ..schemas import (
    GradeCreate,
    GradeUpdate,
    GradeResponse
)
from ..auth import get_current_user

router = APIRouter(
    prefix="/grades",
    tags=["Grades"]
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


# Grade submission
@router.post("/", response_model=GradeResponse)
def create_grade(
    grade: GradeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):

    teacher = db.query(Teacher).filter(   # Does the teacher have a profile?
        Teacher.user_id == current_user.id
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found"
        )

    submission = db.query(Submission).filter(   # Does the submission exist for the teacher to grade?
        Submission.id == grade.submission_id
    ).first()

    if not submission:
        raise HTTPException(
            status_code=404,
            detail="Submission not found"
        )
    

    # Prevent duplicate grading [Prevent teachers from grading the same submission multiple times]
    existing_grade = db.query(Grade).filter(
        Grade.submission_id == grade.submission_id
    ).first()

    if existing_grade:
        raise HTTPException(
            status_code=400,
            detail="Submission already graded"
        )

    new_grade = Grade(
        submission_id=grade.submission_id,
        grade_value=grade.grade_value,
        feedback=grade.feedback
    )

    db.add(new_grade)
    db.commit()      # Persist grade to PostgreSQL
    db.refresh(new_grade)

    return new_grade

# Get all grades
@router.get("/", response_model=list[GradeResponse])
def get_grades(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):

    grades = db.query(Grade).all()  # A teacher can grade multiple submissions, so we return a list of grades

    return grades


# Update grade
@router.put("/{grade_id}", response_model=GradeResponse)
def update_grade(
    grade_id: int,
    grade: GradeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):

    teacher = db.query(Teacher).filter(           # Does the teacher have a profile?
        Teacher.user_id == current_user.id
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found"
        )

    existing_grade = db.query(Grade).filter(        # Does the grade exist for the teacher to update?
        Grade.id == grade_id
    ).first()

    if not existing_grade:
        raise HTTPException(
            status_code=404,
            detail="Grade not found"
        )

    existing_grade.grade_value = grade.grade_value
    existing_grade.feedback = grade.feedback

    db.commit()      # Persist grade update to PostgreSQL
    db.refresh(existing_grade)

    return existing_grade


# Delete grade
@router.delete("/{grade_id}")
def delete_grade(
    grade_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):

    teacher = db.query(Teacher).filter(   # Does the teacher have a profile?
        Teacher.user_id == current_user.id
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found"
        )

    grade = db.query(Grade).filter(     # Does the grade exist for the teacher to delete?
        Grade.id == grade_id
    ).first()

    if not grade:
        raise HTTPException(
            status_code=404,
            detail="Grade not found"
        )

    db.delete(grade)
    db.commit()      # Permanently remove grade from PostgreSQL

    return {
        "message": "Grade deleted successfully"
    }