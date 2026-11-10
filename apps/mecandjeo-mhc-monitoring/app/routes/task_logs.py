# Phase 4: task log lifecycle routes for operators.
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import ROLE_OPERATOR, require_roles
from ..database import get_db
from ..models import DelayLog, TaskLog, User
from ..schemas import TaskLogEnd, TaskLogRead, TaskLogStart
from ..services.operator_service import (
    ensure_shift_has_no_active_task,
    ensure_shift_is_active,
    ensure_task_is_active,
    get_owned_shift,
    get_owned_task_log,
    validate_end_time,
    validate_reference_value,
)


# Phase 4: task router handles operator work logs inside active shifts.
router = APIRouter()


# Phase 4: start a task log for the current operator's active shift.
@router.post("/start", response_model=TaskLogRead, status_code=status.HTTP_201_CREATED)
def start_task_log(
    payload: TaskLogStart,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ROLE_OPERATOR)),
):
    shift = get_owned_shift(db, payload.shift_id, current_user)
    ensure_shift_is_active(shift)
    ensure_shift_has_no_active_task(db, shift)
    nature_of_work = validate_reference_value(db, "nature_of_work", payload.nature_of_work)
    working_area = validate_reference_value(db, "working_area", payload.working_area)

    task_log = TaskLog(
        shift_id=shift.id,
        operator_id=current_user.id,
        crane_id=shift.crane_id,
        nature_of_work=nature_of_work,
        working_area=working_area,
        vessel_name=payload.vessel_name,
        bay_reference=payload.bay_reference,
        container_count=payload.container_count,
        started_at=payload.started_at,
        status="active",
        notes=payload.notes,
    )
    db.add(task_log)
    db.commit()
    db.refresh(task_log)
    return task_log


# Phase 4: end a task log with a required end timestamp.
@router.patch("/{task_log_id}/end", response_model=TaskLogRead)
def end_task_log(
    task_log_id: int,
    payload: TaskLogEnd,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ROLE_OPERATOR)),
):
    task_log = get_owned_task_log(db, task_log_id, current_user)
    ensure_task_is_active(task_log)
    validate_end_time(task_log.started_at, payload.ended_at)

    active_delay = (
        db.query(DelayLog)
        .filter(DelayLog.task_log_id == task_log.id, DelayLog.ended_at.is_(None))
        .first()
    )
    if active_delay:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="End active delay before ending task",
        )

    task_log.ended_at = payload.ended_at
    task_log.status = "completed"
    if payload.container_count is not None:
        task_log.container_count = payload.container_count
    if payload.notes:
        task_log.notes = payload.notes
    db.commit()
    db.refresh(task_log)
    return task_log
