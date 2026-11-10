# Phase 6: admin-only Mobile Harbour Crane asset management routes.
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..auth import ROLE_ADMIN, require_roles
from ..database import get_db
from ..models import Crane, User
from ..schemas import CraneCreate, CraneRead, CraneUpdate
from ..services.admin_service import record_admin_action


# Phase 6: groups physical MHC inventory management endpoints.
router = APIRouter()
admin_user = Depends(require_roles(ROLE_ADMIN))


# List all cranes, including inactive assets retained for historical records.
@router.get("/", response_model=list[CraneRead])
def list_cranes(
    db: Session = Depends(get_db),
    current_user: User = admin_user,
):
    return db.query(Crane).order_by(Crane.mhc_number).all()


# Create an MHC asset that operators can later select at shift start.
@router.post("/", response_model=CraneRead, status_code=status.HTTP_201_CREATED)
def create_crane(
    payload: CraneCreate,
    db: Session = Depends(get_db),
    current_user: User = admin_user,
):
    crane = Crane(**payload.model_dump())
    db.add(crane)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Crane code or MHC number already exists") from exc
    record_admin_action(db, current_user, "crane.created", "crane", crane.id, f"Created crane {crane.mhc_number}")
    db.commit()
    db.refresh(crane)
    return crane


# Update crane details or deactivate an MHC while preserving its work history.
@router.patch("/{crane_id}", response_model=CraneRead)
def update_crane(
    crane_id: int,
    payload: CraneUpdate,
    db: Session = Depends(get_db),
    current_user: User = admin_user,
):
    crane = db.query(Crane).filter(Crane.id == crane_id).first()
    if not crane:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crane not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(crane, field, value)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Crane code or MHC number already exists") from exc
    record_admin_action(db, current_user, "crane.updated", "crane", crane.id, f"Updated crane {crane.mhc_number}")
    db.commit()
    db.refresh(crane)
    return crane
