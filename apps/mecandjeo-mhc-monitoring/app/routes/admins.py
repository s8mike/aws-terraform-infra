# Phase 6: admin-only user and reference-data management routes.
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..auth import ROLE_ADMIN, get_password_hash, require_roles, validate_role
from ..database import get_db
from ..models import ReferenceData, User
from ..schemas import (
    AdminUserCreate,
    AdminUserUpdate,
    ReferenceDataCreate,
    ReferenceDataRead,
    ReferenceDataUpdate,
    UserRead,
)
from ..services.admin_service import record_admin_action


# Phase 6: groups privileged account and operational reference configuration.
router = APIRouter()
admin_user = Depends(require_roles(ROLE_ADMIN))


# Create a user account, including manager and admin roles, from a trusted admin session.
@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: AdminUserCreate,
    db: Session = Depends(get_db),
    current_user: User = admin_user,
):
    email = str(payload.email).lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists")

    user = User(
        email=email,
        full_name=payload.full_name,
        password_hash=get_password_hash(payload.password),
        role=validate_role(payload.role),
        is_active=payload.is_active,
    )
    db.add(user)
    db.flush()
    record_admin_action(db, current_user, "user.created", "user", user.id, f"Created {user.role} account {user.email}")
    db.commit()
    db.refresh(user)
    return user


# Update user details without ever exposing their stored password hash.
@router.patch("/users/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    payload: AdminUserUpdate,
    db: Session = Depends(get_db),
    current_user: User = admin_user,
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    changes = payload.model_dump(exclude_unset=True)
    if user.id == current_user.id:
        if changes.get("is_active") is False:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admins cannot deactivate their own account")
        if "role" in changes and validate_role(changes["role"]) != ROLE_ADMIN:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admins cannot remove their own admin role")

    if "email" in changes:
        email = str(changes["email"]).lower()
        duplicate = db.query(User).filter(User.email == email, User.id != user.id).first()
        if duplicate:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists")
        user.email = email
    if "full_name" in changes:
        user.full_name = changes["full_name"]
    if "password" in changes:
        user.password_hash = get_password_hash(changes["password"])
    if "role" in changes:
        user.role = validate_role(changes["role"])
    if "is_active" in changes:
        user.is_active = changes["is_active"]

    record_admin_action(db, current_user, "user.updated", "user", user.id, f"Updated account {user.email}")
    db.commit()
    db.refresh(user)
    return user


# List reference values, optionally narrowed to a category such as delay_type.
@router.get("/reference-data", response_model=list[ReferenceDataRead])
def list_reference_data(
    category: str | None = Query(default=None, max_length=100),
    db: Session = Depends(get_db),
    current_user: User = admin_user,
):
    query = db.query(ReferenceData)
    if category:
        query = query.filter(ReferenceData.category == category.strip().lower())
    return query.order_by(ReferenceData.category, ReferenceData.code).all()


# Create a selectable operational value, retaining a human label and optional short key.
@router.post("/reference-data", response_model=ReferenceDataRead, status_code=status.HTTP_201_CREATED)
def create_reference_data(
    payload: ReferenceDataCreate,
    db: Session = Depends(get_db),
    current_user: User = admin_user,
):
    reference_data = ReferenceData(
        category=payload.category.strip().lower(),
        code=payload.code.strip().lower(),
        label=payload.label.strip(),
        short_key=payload.short_key.strip() if payload.short_key else None,
        description=payload.description,
        is_active=payload.is_active,
    )
    db.add(reference_data)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Reference code already exists in this category") from exc
    record_admin_action(db, current_user, "reference_data.created", "reference_data", reference_data.id, f"Created {reference_data.category}:{reference_data.code}")
    db.commit()
    db.refresh(reference_data)
    return reference_data


# Update or deactivate a reference value without removing its historical meaning.
@router.patch("/reference-data/{reference_data_id}", response_model=ReferenceDataRead)
def update_reference_data(
    reference_data_id: int,
    payload: ReferenceDataUpdate,
    db: Session = Depends(get_db),
    current_user: User = admin_user,
):
    reference_data = db.query(ReferenceData).filter(ReferenceData.id == reference_data_id).first()
    if not reference_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reference data not found")

    changes = payload.model_dump(exclude_unset=True)
    for field in ("category", "code"):
        if field in changes:
            changes[field] = changes[field].strip().lower()
    if "label" in changes:
        changes["label"] = changes["label"].strip()
    if "short_key" in changes and changes["short_key"]:
        changes["short_key"] = changes["short_key"].strip()
    for field, value in changes.items():
        setattr(reference_data, field, value)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Reference code already exists in this category") from exc
    record_admin_action(db, current_user, "reference_data.updated", "reference_data", reference_data.id, f"Updated {reference_data.category}:{reference_data.code}")
    db.commit()
    db.refresh(reference_data)
    return reference_data
