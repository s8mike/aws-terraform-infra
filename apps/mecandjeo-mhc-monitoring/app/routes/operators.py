# Phase 4: operator self-service routes.
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth import ROLE_OPERATOR, require_roles
from ..database import get_db
from ..models import User
from ..schemas import OperatorActiveStateRead, OperatorSummaryRead, ShiftSummaryRead
from ..services.operator_service import (
    build_operator_active_state,
    build_operator_summary,
    build_shift_summary,
    get_owned_shift,
)


# Phase 4: operator router exposes self-service operator views.
router = APIRouter()


# Phase 4: show the current operator's all-time performance summary.
@router.get("/me/summary", response_model=OperatorSummaryRead)
def read_operator_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ROLE_OPERATOR)),
):
    return build_operator_summary(db, current_user)


# Phase 10: return the open shift, task, and delay so the UI can resume after a reload.
@router.get("/me/active", response_model=OperatorActiveStateRead)
def read_operator_active_state(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ROLE_OPERATOR)),
):
    return build_operator_active_state(db, current_user)


# Phase 10: totals for one of the operator's own shifts (404 if the shift belongs to someone else).
@router.get("/me/shifts/{shift_id}/summary", response_model=ShiftSummaryRead)
def read_shift_summary(
    shift_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ROLE_OPERATOR)),
):
    shift = get_owned_shift(db, shift_id, current_user)
    return build_shift_summary(db, shift)