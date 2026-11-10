# Phase 4: working-condition capture routes for operators.
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..auth import ROLE_OPERATOR, require_roles
from ..database import get_db
from ..models import User
from ..schemas import WorkingConditionCreate, WorkingConditionRead
from ..services.operator_service import (
    create_working_condition,
    ensure_shift_is_active,
    get_owned_shift,
)


# Phase 4: working-condition router records context affecting performance.
router = APIRouter()


# Phase 4: capture environmental or operational conditions during an active shift.
@router.post("/", response_model=WorkingConditionRead, status_code=status.HTTP_201_CREATED)
def record_working_condition(
    payload: WorkingConditionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ROLE_OPERATOR)),
):
    shift = get_owned_shift(db, payload.shift_id, current_user)
    ensure_shift_is_active(shift)
    return create_working_condition(db, shift, payload)
