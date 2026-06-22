from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from ..database import get_db
from ..models import Message, User
from ..schemas import (
    MessageCreate,
    MessageResponse
)
from ..auth import get_current_user

router = APIRouter(
    prefix="/messages",
    tags=["Messages"]
)

# ================================
# Send message [phase 11.1 step 2]
# ================================
@router.post(
    "/",
    response_model=MessageResponse
)
def send_message(
    payload: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    receiver = (
        db.query(User)
        .filter(
            User.id == payload.receiver_id
        )
        .first()
    )

    if not receiver:
        raise HTTPException(
            status_code=404,
            detail="Receiver not found"
        )

    db_message = Message(
        sender_id=current_user.id,
        receiver_id=payload.receiver_id,
        message=payload.message
    )

    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    return db_message

# ==================================
# Inbox messages [phase 11.1 step 3]
# ==================================
@router.get(
    "/inbox",
    response_model=list[MessageResponse]
)
def get_inbox(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    messages = (
        db.query(Message)
        .filter(
            Message.receiver_id == current_user.id
        )
        .order_by(                    # Ensures Newest message --> Older Message
            Message.created_at.desc()
        )
        .all()
    )

    return messages
# =================================
# Sent messages [phase 11.1 step 4]
# =================================
@router.get(
    "/sent",
    response_model=list[MessageResponse]
)
def get_sent_messages(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    messages = (
        db.query(Message)
        .filter(
            Message.sender_id == current_user.id
        )
        .order_by(
            Message.created_at.desc()
        )
        .all()
    )

    return messages

# ========================================
# Mark message as read [phase 11.1 step 5]
# ========================================
@router.put(
    "/{message_id}/read",
    response_model=MessageResponse
)
def mark_message_as_read(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    message = (
        db.query(Message)
        .filter(
            Message.id == message_id
        )
        .first()
    )

    if not message:
        raise HTTPException(
            status_code=404,
            detail="Message not found"
        )

    # Only recipient can mark as read
    if message.receiver_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to update this message"
        )

    message.is_read = True

    db.commit()
    db.refresh(message)

    return message

# =====================================
# Conversation view [phase 11.1 step 6]
# =====================================
@router.get(
    "/conversation/{user_id}",
    response_model=list[MessageResponse]
)
def get_conversation(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    conversation = (
        db.query(Message)
        .filter(
            or_(
                and_(
                    Message.sender_id == current_user.id,
                    Message.receiver_id == user_id
                ),
                and_(
                    Message.sender_id == user_id,
                    Message.receiver_id == current_user.id
                )
            )
        )
        .order_by(
            Message.created_at.asc()  # asc used in conversation. read chronologically
        )
        .all()
    )

    return conversation