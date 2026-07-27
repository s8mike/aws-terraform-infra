# One-time system initialization
"""
bootstrap.py

Purpose:
--------
Provides the one-time system initialization endpoint for the LMS.

Responsibilities:
- Checks whether an administrator already exists.
- Creates the first administrator when the system is deployed for the first time.
- Prevents creation of additional bootstrap administrators after initialization.

Why this file exists:
---------------------
A newly installed LMS has no administrator, so nobody can access the
admin-only endpoints to manage users and roles.

This bootstrap endpoint solves the "first admin" problem by allowing the
creation of exactly one administrator. Once an admin account exists,
this endpoint becomes unavailable, and all future administrators or
teachers must be created or promoted through the normal admin workflow.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.auth import hash_password

from app.schemas import (
    BootstrapAdminRequest,
    BootstrapAdminResponse,
)



router = APIRouter(
    prefix="/bootstrap",
    tags=["Bootstrap"]
)


@router.post(
    "/admin",
    response_model=BootstrapAdminResponse,
    status_code=201,
    responses={
        400: {"description": "Email already registered"},
        403: {"description": "Bootstrap administrator has already been created"},
    },
)
def create_bootstrap_admin(
    request: BootstrapAdminRequest,
    db: Session = Depends(get_db)
):
    """
    Create the first administrator for the LMS.

    This endpoint is only available when no administrator
    account exists in the system.
    """

    # ---------------------------------------------------------
    # Prevent duplicate email addresses.
    # ---------------------------------------------------------
    existing_user = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # ---------------------------------------------------------
    # Allow bootstrap only if no administrator exists.
    # ---------------------------------------------------------
    existing_admin = (
        db.query(User)
        .filter(User.role == "admin")
        .first()
    )

    if existing_admin:
        raise HTTPException(
            status_code=403,
            detail="Bootstrap administrator has already been created."
        )

    # ---------------------------------------------------------
    # Create the first administrator.
    # ---------------------------------------------------------
    admin = User(
        email=request.email,
        password=hash_password(request.password),
        role="admin"
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    return admin