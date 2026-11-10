# Phase 4: delay log lifecycle routes for operators.
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..auth import ROLE_OPERATOR, require_roles
from ..database import get_db
from ..models import DelayLog, User
from ..schemas import DelayLogEnd, DelayLogRead, DelayLogStart
from ..services.operator_service import (
    calculate_duration_minutes,
    ensure_delay_is_active,
    ensure_task_has_no_active_delay,
    ensure_task_is_active,
    get_owned_delay_log,
    get_owned_task_log,
    validate_reference_value,
)


# Phase 4: delay router captures downtime against an active task.
router = APIRouter()


# Phase 4: start a delay log for a task owned by the current operator.
@router.post("/start", response_model=DelayLogRead, status_code=status.HTTP_201_CREATED)
def start_delay_log(
    payload: DelayLogStart,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ROLE_OPERATOR)),
):
    task_log = get_owned_task_log(db, payload.task_log_id, current_user)
    ensure_task_is_active(task_log)
    ensure_task_has_no_active_delay(db, task_log)
    delay_type = validate_reference_value(db, "delay_type", payload.delay_type)

    delay_log = DelayLog(
        task_log_id=task_log.id,
        delay_type=delay_type,
        custom_delay_type=payload.custom_delay_type,
        started_at=payload.started_at,
        is_operator_controllable=payload.is_operator_controllable,
        notes=payload.notes,
    )
    db.add(delay_log)
    db.commit()
    db.refresh(delay_log)
    return delay_log


# Phase 4: end a delay log with a required end timestamp.
@router.patch("/{delay_log_id}/end", response_model=DelayLogRead)
def end_delay_log(
    delay_log_id: int,
    payload: DelayLogEnd,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ROLE_OPERATOR)),
):
    delay_log = get_owned_delay_log(db, delay_log_id, current_user)
    ensure_delay_is_active(delay_log)
    duration_minutes = payload.duration_minutes
    if duration_minutes is None:
        duration_minutes = calculate_duration_minutes(
            delay_log.started_at,
            payload.ended_at,
        )

    delay_log.ended_at = payload.ended_at
    delay_log.duration_minutes = duration_minutes
    if payload.notes:
        delay_log.notes = payload.notes
    db.commit()
    db.refresh(delay_log)
    return delay_log
