# Lets users register, login, change their own password, and read their own authenticated profile.

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from ..auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_password_hash,
    get_user_by_email,
    verify_password,
)
from ..database import get_db
from ..models import AuditLog, User
from ..schemas import PasswordChange, TokenRead, UserCreate, UserLogin, UserRead


# Auth router groups registration, login, password change, and current-user endpoints.
router = APIRouter()


# Register an operator account. Privileged roles are created by an admin in Phase 6.
@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    if payload.role.lower().strip() != "operator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Public registration can only create operator accounts",
        )
    if get_user_by_email(db, payload.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

    user = User(
        email=payload.email.lower(),
        full_name=payload.full_name,
        password_hash=get_password_hash(payload.password),
        role="operator",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# Login with email and password, returning a signed bearer token.
@router.post("/login", response_model=TokenRead)
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenRead(access_token=create_access_token(user))


# Return the current authenticated user's public profile.
@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user


# Phase 10: let any signed-in user change their own password.
# A wrong current password is a 400 (not a 401) so the frontend does not sign the user out.
@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    payload: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    if verify_password(payload.new_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from the current password",
        )

    current_user.password_hash = get_password_hash(payload.new_password)
    # The audit entry records who changed it and when, never the password itself.
    db.add(
        AuditLog(
            actor_id=current_user.id,
            action="user.password_changed",
            entity_type="user",
            entity_id=current_user.id,
            description="Changed own password",
        )
    )
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)