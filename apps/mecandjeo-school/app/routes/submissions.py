# Submission management (PHASE 5.2 Step 7)

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    Submission,
    Assignment,
    Student,
    User
)
from ..schemas import (
    SubmissionCreate,
    SubmissionUpdate,
    SubmissionResponse
)
from ..auth import (
    get_current_user,
    require_student
)

router = APIRouter(
    prefix="/submissions",
    tags=["Submissions"]  # For API documentation grouping, this will create a "Submissions" section in the Swagger UI
)

# # Verify student role. This is now imported from app/auth.py
# def require_student(
#     current_user: User = Depends(get_current_user)
# ):

#     if current_user.role != "student":
#         raise HTTPException(
#             status_code=403,
#             detail="Student access required"
#         )

#     return current_user


# Submit assignment
@router.post("/", response_model=SubmissionResponse)
def create_submission(
    submission: SubmissionCreate,
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

    assignment = db.query(Assignment).filter(
        Assignment.id == submission.assignment_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=404,
            detail="Assignment not found"
        )
    
    # Prevent duplicate submissions (Guide against one student, many submissions - we want one student, one submission per assignment)
    existing_submission = db.query(Submission).filter(
        Submission.student_id == student.id,
        Submission.assignment_id == submission.assignment_id
    ).first()

    if existing_submission:
        raise HTTPException(
            status_code=400,
            detail="Assignment already submitted"
        )

    new_submission = Submission(
        student_id=student.id,  # Comes from the authenticated user's student profile
        assignment_id=submission.assignment_id,
        content=submission.content
    )

    db.add(new_submission)
    db.commit()            # Persist submission to PostgreSQL
    db.refresh(new_submission)

    return new_submission


# Get my submissions
@router.get("/", response_model=list[SubmissionResponse])
def get_my_submissions(
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
    ).all()      # One student can have many submissions to different assignments, but only one submission per assignment (enforced in create_submission)

    return submissions


# Update submission
@router.put("/{submission_id}", response_model=SubmissionResponse)
def update_submission(
    submission_id: int,
    submission: SubmissionUpdate,
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

    existing_submission = db.query(Submission).filter(
        Submission.id == submission_id
    ).first()

    if not existing_submission:
        raise HTTPException(
            status_code=404,
            detail="Submission not found"
        )

    # Resource-level authorization
    if existing_submission.student_id != student.id:  # Do you own this submission? You can only update your own submission
        raise HTTPException(
            status_code=403,
            detail="You do not own this submission"
        )

    existing_submission.content = submission.content

    db.commit()              # Persist update to PostgreSQL
    db.refresh(existing_submission)

    return existing_submission


# Delete submission
@router.delete("/{submission_id}")
def delete_submission(
    submission_id: int,
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

    submission = db.query(Submission).filter(
        Submission.id == submission_id
    ).first()

    if not submission:
        raise HTTPException(
            status_code=404,
            detail="Submission not found"
        )

    # Resource-level authorization
    if submission.student_id != student.id: # Do you own this submission? You can only delete your own submission
        raise HTTPException(
            status_code=403,
            detail="You do not own this submission"
        )

    db.delete(submission)
    db.commit()      # Permanently remove submission from PostgreSQL

    return {
        "message": "Submission deleted successfully"
    }