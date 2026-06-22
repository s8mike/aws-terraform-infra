from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    MeetingRequest,
    Parent,
    Teacher,
    User
)
from ..schemas import (
    MeetingRequestCreate,
    MeetingRequestResponse,
    MeetingRequestStatusUpdate
)
from ..auth import get_current_user


router = APIRouter(
    prefix="/meetings",
    tags=["Meetings"]
)


# Create meeting request [Parent]
@router.post(
    "/",
    response_model=MeetingRequestResponse
)
def create_meeting_request(
    payload: MeetingRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    parent = (
        db.query(Parent)
        .filter(
            Parent.user_id == current_user.id
        )
        .first()
    )

    if not parent:
        raise HTTPException(
            status_code=403,
            detail="Parent profile not found"
        )

    teacher = (
        db.query(Teacher)
        .filter(
            Teacher.id == payload.teacher_id
        )
        .first()
    )

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher not found"
        )

    request = MeetingRequest(
        parent_id=parent.id,
        teacher_id=payload.teacher_id,
        subject=payload.subject,
        message=payload.message
    )

    db.add(request)
    db.commit()
    db.refresh(request)

    return request

# View meeting requests [Teacher]
@router.get(
    "/",
    response_model=list[MeetingRequestResponse]
)
def get_meeting_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    teacher = (
        db.query(Teacher)
        .filter(
            Teacher.user_id == current_user.id
        )
        .first()
    )

    if not teacher:
        raise HTTPException(
            status_code=403,
            detail="Teacher profile not found"
        )

    requests = (
        db.query(MeetingRequest)
        .filter(
            MeetingRequest.teacher_id == teacher.id
        )
        .order_by(
            MeetingRequest.created_at.desc()
        )
        .all()
    )

    return requests

# Update meeting request status [Teacher]
@router.put(
    "/{meeting_id}/status",
    response_model=MeetingRequestResponse
)
def update_meeting_status(
    meeting_id: int,
    payload: MeetingRequestStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    teacher = (
        db.query(Teacher)
        .filter(
            Teacher.user_id == current_user.id
        )
        .first()
    )

    if not teacher:
        raise HTTPException(
            status_code=403,
            detail="Teacher profile not found"
        )

    meeting = (
        db.query(MeetingRequest)
        .filter(
            MeetingRequest.id == meeting_id
        )
        .first()
    )

    if not meeting:
        raise HTTPException(
            status_code=404,
            detail="Meeting request not found"
        )

    if meeting.teacher_id != teacher.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized"
        )

    if payload.status not in [
        "Approved",
        "Rejected"
    ]:
        raise HTTPException(
            status_code=400,
            detail="Invalid status"
        )

    meeting.status = payload.status

    db.commit()
    db.refresh(meeting)

    return meeting

# Meeting request history [Parent]
@router.get(
    "/history",
    response_model=list[MeetingRequestResponse]
)
def get_meeting_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    parent = (
        db.query(Parent)
        .filter(
            Parent.user_id == current_user.id
        )
        .first()
    )

    if not parent:
        raise HTTPException(
            status_code=403,
            detail="Parent profile not found"
        )

    requests = (
        db.query(MeetingRequest)
        .filter(
            MeetingRequest.parent_id == parent.id
        )
        .order_by(
            MeetingRequest.created_at.desc()
        )
        .all()
    )

    return requests