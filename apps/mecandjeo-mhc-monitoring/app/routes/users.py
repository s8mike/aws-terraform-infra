from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import ROLE_ADMIN, require_roles
from ..database import get_db
from ..models import User
from ..schemas import UserRead


# User router holds admin-only account inspection endpoints.
router = APIRouter()


# List all users. Restricted to admins because it exposes account metadata.
@router.get("/", response_model=list[UserRead])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ROLE_ADMIN)),
):
    return db.query(User).order_by(User.id).all()


# Read one user by id. Restricted to admins for privacy and governance.
@router.get("/{user_id}", response_model=UserRead)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ROLE_ADMIN)),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user
