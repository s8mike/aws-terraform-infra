from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, Parent
from ..schemas import (
    ParentCreate,
    ParentRegistrationResponse
)
from ..auth import hash_password

router = APIRouter(
    prefix="/parents",
    tags=["Parents"]
)

@router.post(
    "/register",
    response_model=ParentRegistrationResponse
)
def register_parent(
    parent_data: ParentCreate,
    db: Session = Depends(get_db)
):

    existing_user = (
        db.query(User)
        .filter(
            User.email == parent_data.email
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = User(
        email=parent_data.email,
        password=hash_password(
            parent_data.password
        ),
        role="parent"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    new_parent = Parent(
        user_id=new_user.id,
        full_name=parent_data.full_name,
        phone_number=parent_data.phone_number
    )

    db.add(new_parent)
    db.commit()
    db.refresh(new_parent)

    return {
        "id": new_parent.id,
        "email": new_user.email,
        "role": new_user.role,
        "full_name": new_parent.full_name,
        "phone_number": new_parent.phone_number
    }