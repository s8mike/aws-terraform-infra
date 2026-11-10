# Phase 4: helper functions for operator-owned shifts, tasks, delays, and summaries.
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..models import Crane, DelayLog, ReferenceData, Shift, TaskLog, User, WorkingCondition
from ..schemas import OperatorSummaryRead, ShiftSummaryRead


# Phase 4: valid shift codes operators can select when starting a shift.
VALID_SHIFT_CODES = {"A", "B", "C"}


# Phase 4: normalize and validate the operator-selected shift code.
def normalize_shift_code(shift_code: str) -> str:
    normalized_shift_code = shift_code.strip().upper()
    if normalized_shift_code not in VALID_SHIFT_CODES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Shift code must be A, B, or C",
        )
    return normalized_shift_code

# Phase 9: validate an operator-supplied value against active admin-managed reference data.
def validate_reference_value(db: Session, category: str, value: str) -> str:
    code = value.strip().lower()
    exists = (
        db.query(ReferenceData.id)
        .filter(
            ReferenceData.category == category,
            ReferenceData.code == code,
            ReferenceData.is_active.is_(True),
        )
        .first()
    )
    if not exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {category} value",
        )
    return code


# Phase 4: verify a timestamp closes a record after it was started.
def validate_end_time(started_at: datetime, ended_at: datetime):
    if ended_at <= started_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ended_at must be after started_at",
        )


# Phase 4: find an active MHC by the operator-facing MHC number.
def get_active_crane_by_mhc_number(db: Session, mhc_number: str) -> Crane:
    crane = (
        db.query(Crane)
        .filter(Crane.mhc_number == mhc_number.strip(), Crane.is_active.is_(True))
        .first()
    )
    if not crane:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active MHC number not found",
        )
    return crane


# Phase 4: ensure an operator has no active shift before starting another.
def ensure_operator_has_no_active_shift(db: Session, operator: User):
    active_shift = (
        db.query(Shift)
        .filter(Shift.operator_id == operator.id, Shift.status == "active")
        .first()
    )
    if active_shift:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Operator already has an active shift",
        )


# Phase 4: fetch a shift and verify it belongs to the current operator.
def get_owned_shift(db: Session, shift_id: int, operator: User) -> Shift:
    shift = (
        db.query(Shift)
        .filter(Shift.id == shift_id, Shift.operator_id == operator.id)
        .first()
    )
    if not shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shift not found",
        )
    return shift


# Phase 4: fetch a task and verify it belongs to the current operator.
def get_owned_task_log(db: Session, task_log_id: int, operator: User) -> TaskLog:
    task_log = (
        db.query(TaskLog)
        .filter(TaskLog.id == task_log_id, TaskLog.operator_id == operator.id)
        .first()
    )
    if not task_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task log not found",
        )
    return task_log


# Phase 4: fetch a delay and verify it belongs to the current operator.
def get_owned_delay_log(db: Session, delay_log_id: int, operator: User) -> DelayLog:
    delay_log = (
        db.query(DelayLog)
        .join(TaskLog, DelayLog.task_log_id == TaskLog.id)
        .filter(DelayLog.id == delay_log_id, TaskLog.operator_id == operator.id)
        .first()
    )
    if not delay_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delay log not found",
        )
    return delay_log


# Phase 4: helper confirms a delay is still open before closing it.
def ensure_delay_is_active(delay_log: DelayLog):
    if delay_log.ended_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Delay log is already ended",
        )


# Phase 4: prevent starting more than one active task inside a shift.
def ensure_shift_has_no_active_task(db: Session, shift: Shift):
    active_task = (
        db.query(TaskLog)
        .filter(TaskLog.shift_id == shift.id, TaskLog.status == "active")
        .first()
    )
    if active_task:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Shift already has an active task",
        )


# Phase 4: prevent starting more than one active delay inside a task.
def ensure_task_has_no_active_delay(db: Session, task_log: TaskLog):
    active_delay = (
        db.query(DelayLog)
        .filter(DelayLog.task_log_id == task_log.id, DelayLog.ended_at.is_(None))
        .first()
    )
    if active_delay:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Task already has an active delay",
        )


# Phase 4: calculate delay minutes from timestamps when the client omits it.
def calculate_duration_minutes(started_at: datetime, ended_at: datetime) -> int:
    validate_end_time(started_at, ended_at)
    return int((ended_at - started_at).total_seconds() // 60)


# Phase 4: build a compact operator performance summary.
def build_operator_summary(db: Session, operator: User) -> OperatorSummaryRead:
    shifts = db.query(Shift).filter(Shift.operator_id == operator.id).all()
    active_shift = next((shift for shift in shifts if shift.status == "active"), None)
    completed_tasks = (
        db.query(TaskLog)
        .filter(TaskLog.operator_id == operator.id, TaskLog.status == "completed")
        .all()
    )
    task_ids = [task.id for task in completed_tasks]
    delay_minutes = 0
    if task_ids:
        delays = db.query(DelayLog).filter(DelayLog.task_log_id.in_(task_ids)).all()
        delay_minutes = sum(delay.duration_minutes or 0 for delay in delays)

    return OperatorSummaryRead(
        operator_id=operator.id,
        total_shifts=len(shifts),
        active_shift_id=active_shift.id if active_shift else None,
        completed_tasks=len(completed_tasks),
        total_container_count=sum(task.container_count for task in completed_tasks),
        total_delay_minutes=delay_minutes,
    )


# Phase 4: helper confirms a shift is still open for operator writes.
def ensure_shift_is_active(shift: Shift):
    if shift.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Shift is not active",
        )


# Phase 4: helper confirms a task is still open for operator writes.
def ensure_task_is_active(task_log: TaskLog):
    if task_log.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task log is not active",
        )


# Phase 4: helper creates a working condition record for an owned shift.
def create_working_condition(
    db: Session,
    shift: Shift,
    payload,
) -> WorkingCondition:
    working_condition_values = {
        "shift_id": shift.id,
        "weather_condition": payload.weather_condition,
        "visibility": payload.visibility,
        "wind_condition": payload.wind_condition,
        "deck_condition": payload.deck_condition,
        "congestion_level": payload.congestion_level,
        "notes": payload.notes,
    }
    if payload.recorded_at is not None:
        working_condition_values["recorded_at"] = payload.recorded_at

    working_condition = WorkingCondition(
        **working_condition_values,
    )
    db.add(working_condition)
    db.commit()
    db.refresh(working_condition)
    return working_condition



# Phase 10: find the operator's open shift, its open task, and that task's open delay.
def build_operator_active_state(db: Session, operator: User) -> dict:
    shift = (
        db.query(Shift)
        .filter(Shift.operator_id == operator.id, Shift.status == "active")
        .first()
    )
    task = None
    delay = None
    if shift:
        task = (
            db.query(TaskLog)
            .filter(TaskLog.shift_id == shift.id, TaskLog.status == "active")
            .first()
        )
    if task:
        delay = (
            db.query(DelayLog)
            .filter(DelayLog.task_log_id == task.id, DelayLog.ended_at.is_(None))
            .first()
        )
    return {"shift": shift, "task": task, "delay": delay}



# Phase 10: totals for the completed tasks (and their delays) inside one shift.
def build_shift_summary(db: Session, shift: Shift) -> ShiftSummaryRead:
    completed_tasks = (
        db.query(TaskLog)
        .filter(TaskLog.shift_id == shift.id, TaskLog.status == "completed")
        .all()
    )
    task_ids = [task.id for task in completed_tasks]
    delay_minutes = 0
    if task_ids:
        delays = db.query(DelayLog).filter(DelayLog.task_log_id.in_(task_ids)).all()
        delay_minutes = sum(delay.duration_minutes or 0 for delay in delays)

    return ShiftSummaryRead(
        shift_id=shift.id,
        mhc_number=shift.mhc_number,
        completed_tasks=len(completed_tasks),
        total_container_count=sum(task.container_count for task in completed_tasks),
        total_delay_minutes=delay_minutes,
    )