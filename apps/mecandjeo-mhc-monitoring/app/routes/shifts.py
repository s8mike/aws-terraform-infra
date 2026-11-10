# Phase 4: shift lifecycle routes for operators.
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import ROLE_OPERATOR, require_roles
from ..database import get_db
from ..models import Shift, TaskLog, User
from ..schemas import ShiftEnd, ShiftRead, ShiftStart
from ..services.operator_service import (
    ensure_operator_has_no_active_shift,
    ensure_shift_is_active,
    get_active_crane_by_mhc_number,
    get_owned_shift,
    normalize_shift_code,
    validate_end_time,
)


# Phase 4: shift router handles operator shift start/end workflows.
router = APIRouter()


# Phase 4: start a shift after selecting a valid MHC number and shift A/B/C.
@router.post("/start", response_model=ShiftRead, status_code=status.HTTP_201_CREATED)
def start_shift(
    payload: ShiftStart,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ROLE_OPERATOR)),
):
    ensure_operator_has_no_active_shift(db, current_user)
    crane = get_active_crane_by_mhc_number(db, payload.mhc_number)

    shift = Shift(
        operator_id=current_user.id,
        crane_id=crane.id,
        mhc_number=crane.mhc_number,
        shift_code=normalize_shift_code(payload.shift_code),
        started_at=payload.started_at,
        status="active",
        notes=payload.notes,
    )
    db.add(shift)
    db.commit()
    db.refresh(shift)
    return shift


# Phase 4: list shifts owned by the current operator.
@router.get("/", response_model=list[ShiftRead])
def list_my_shifts(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ROLE_OPERATOR)),
):
    return (
        db.query(Shift)
        .filter(Shift.operator_id == current_user.id)
        .order_by(Shift.started_at.desc())
        .all()
    )


# Phase 4: end a shift with a required end timestamp.
@router.patch("/{shift_id}/end", response_model=ShiftRead)
def end_shift(
    shift_id: int,
    payload: ShiftEnd,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ROLE_OPERATOR)),
):
    shift = get_owned_shift(db, shift_id, current_user)
    ensure_shift_is_active(shift)
    validate_end_time(shift.started_at, payload.ended_at)

    active_task = (
        db.query(TaskLog)
        .filter(TaskLog.shift_id == shift.id, TaskLog.status == "active")
        .first()
    )
    if active_task:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="End active task before ending shift",
        )

    shift.ended_at = payload.ended_at
    shift.status = "completed"
    if payload.notes:
        shift.notes = payload.notes
    db.commit()
    db.refresh(shift)
    return shift
