# Phase 5: manager dashboard aggregation helpers.
from sqlalchemy.orm import Session

from ..auth import ROLE_OPERATOR
from ..models import Crane, DelayLog, Shift, TaskLog, User
from ..schemas import (
    ManagerActiveShiftRead,
    ManagerDashboardRead,
    ManagerLiveOperatorStatusRead,
)


# Phase 5: return high-level counts for the manager dashboard.
def build_manager_dashboard(db: Session) -> ManagerDashboardRead:
    completed_tasks = (
        db.query(TaskLog)
        .filter(TaskLog.status == "completed", TaskLog.ended_at.isnot(None))
        .all()
    )
    all_delays = db.query(DelayLog).all()

    return ManagerDashboardRead(
        total_operators=db.query(User)
        .filter(User.role == ROLE_OPERATOR, User.is_active.is_(True))
        .count(),
        total_cranes=db.query(Crane).filter(Crane.is_active.is_(True)).count(),
        active_shifts=db.query(Shift).filter(Shift.status == "active").count(),
        active_tasks=db.query(TaskLog).filter(TaskLog.status == "active").count(),
        active_delays=db.query(DelayLog).filter(DelayLog.ended_at.is_(None)).count(),
        completed_tasks=len(completed_tasks),
        total_container_count=sum(task.container_count for task in completed_tasks),
        total_delay_minutes=sum(delay.duration_minutes or 0 for delay in all_delays),
    )


# Phase 5: find the active task inside a shift, if one exists.
def get_active_task_for_shift(shift: Shift) -> TaskLog | None:
    return next((task for task in shift.task_logs if task.status == "active"), None)


# Phase 5: find the active delay inside a task, if one exists.
def get_active_delay_for_task(task_log: TaskLog | None) -> DelayLog | None:
    if task_log is None:
        return None
    return next((delay for delay in task_log.delay_logs if delay.ended_at is None), None)


# Phase 5: list operators currently active and whether they are working or delayed.
def build_live_operator_status(db: Session) -> list[ManagerLiveOperatorStatusRead]:
    active_shifts = (
        db.query(Shift)
        .filter(Shift.status == "active")
        .order_by(Shift.started_at.asc())
        .all()
    )
    status_rows = []

    for shift in active_shifts:
        active_task = get_active_task_for_shift(shift)
        active_delay = get_active_delay_for_task(active_task)
        current_status = "delayed" if active_delay else "working" if active_task else "active"

        status_rows.append(
            ManagerLiveOperatorStatusRead(
                operator_id=shift.operator_id,
                operator_name=shift.operator.full_name,
                shift_id=shift.id,
                shift_code=shift.shift_code,
                mhc_number=shift.mhc_number,
                crane_id=shift.crane_id,
                shift_started_at=shift.started_at,
                active_task_id=active_task.id if active_task else None,
                active_task_nature_of_work=(
                    active_task.nature_of_work if active_task else None
                ),
                active_delay_id=active_delay.id if active_delay else None,
                active_delay_type=active_delay.delay_type if active_delay else None,
                status=current_status,
            )
        )

    return status_rows


# Phase 5: summarize active shifts with task and delay counts for supervisors.
def build_active_shift_overview(db: Session) -> list[ManagerActiveShiftRead]:
    active_shifts = (
        db.query(Shift)
        .filter(Shift.status == "active")
        .order_by(Shift.started_at.asc())
        .all()
    )
    overview_rows = []

    for shift in active_shifts:
        active_tasks = [task for task in shift.task_logs if task.status == "active"]
        completed_tasks = [
            task for task in shift.task_logs if task.status == "completed"
        ]
        active_delay_count = sum(
            1
            for task in shift.task_logs
            for delay in task.delay_logs
            if delay.ended_at is None
        )

        overview_rows.append(
            ManagerActiveShiftRead(
                shift_id=shift.id,
                operator_id=shift.operator_id,
                operator_name=shift.operator.full_name,
                crane_id=shift.crane_id,
                mhc_number=shift.mhc_number,
                shift_code=shift.shift_code,
                started_at=shift.started_at,
                active_task_count=len(active_tasks),
                completed_task_count=len(completed_tasks),
                active_delay_count=active_delay_count,
                total_container_count=sum(
                    task.container_count for task in completed_tasks
                ),
            )
        )

    return overview_rows
