from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..auth import require_admin
from ..database import get_db
from ..models import User
from ..schemas import UserResponse

router = APIRouter()


# ---------------------------------------------------------
# Retrieve all registered users.
#
# Access:
#   Administrator only.
#
# Response:
#   Returns a list of users without exposing passwords.
# ---------------------------------------------------------
@router.get(
    "/",
    response_model=List[UserResponse],
    summary="Get all users",
    responses={
        200: {"description": "Users retrieved successfully."},
        401: {"description": "Authentication required."},
        403: {"description": "Administrator privileges required."},
    },
)
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> List[UserResponse]:

    users = db.query(User).all()
    return users


# ---------------------------------------------------------
# Retrieve a single user by ID.
#
# Access:
#   Administrator only.
#
# Response:
#   Returns a single user without exposing passwords.
# ---------------------------------------------------------
@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    responses={
        200: {"description": "User retrieved successfully."},
        401: {"description": "Authentication required."},
        403: {"description": "Administrator privileges required."},
        404: {"description": "User not found."},
    },
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> UserResponse:

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    return user