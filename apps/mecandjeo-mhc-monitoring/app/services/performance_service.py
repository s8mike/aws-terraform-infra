# Phase 5: manager performance trend helpers.
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..models import TaskLog
from ..schemas import ManagerPerformanceTrendItem
from .delay_analysis_service import get_delay_minutes


# Phase 5: supported grouping dimensions for manager trend views.
VALID_PERFORMANCE_GROUPS = {"operator", "crane", "nature_of_work", "date"}


# Phase 5: reject unsupported grouping values before querying.
def validate_performance_group(group_by: str) -> str:
    normalized_group = group_by.strip().lower()
    if normalized_group not in VALID_PERFORMANCE_GROUPS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="group_by must be operator, crane, nature_of_work, or date",
        )
    return normalized_group


# Phase 5: apply optional date filters to completed task logs.
def filter_tasks_by_date(query, date_from: datetime | None, date_to: datetime | None):
    if date_from is not None:
        query = query.filter(TaskLog.started_at >= date_from)
    if date_to is not None:
        query = query.filter(TaskLog.started_at <= date_to)
    return query


# Phase 5: derive total task minutes from task start/end timestamps.
def get_task_minutes(task_log: TaskLog) -> int:
    if task_log.ended_at is None:
        return 0
    return int((task_log.ended_at - task_log.started_at).total_seconds() // 60)


# Phase 5: return a stable grouping key and label for a completed task.
def get_task_group(task_log: TaskLog, group_by: str) -> tuple[str, str]:
    if group_by == "operator":
        return str(task_log.operator_id), task_log.operator.full_name
    if group_by == "crane":
        return str(task_log.crane_id), task_log.crane.mhc_number
    if group_by == "nature_of_work":
        return task_log.nature_of_work, task_log.nature_of_work
    return task_log.started_at.date().isoformat(), task_log.started_at.date().isoformat()


# Phase 5: calculate grouped production and delay metrics for managers.
def build_performance_trends(
    db: Session,
    group_by: str = "operator",
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> list[ManagerPerformanceTrendItem]:
    normalized_group = validate_performance_group(group_by)
    task_query = (
        db.query(TaskLog)
        .filter(TaskLog.status == "completed", TaskLog.ended_at.isnot(None))
        .order_by(TaskLog.started_at.asc())
    )
    task_query = filter_tasks_by_date(task_query, date_from, date_to)
    grouped_tasks = {}

    for task_log in task_query.all():
        group_key, label = get_task_group(task_log, normalized_group)
        if group_key not in grouped_tasks:
            grouped_tasks[group_key] = {
                "label": label,
                "completed_tasks": 0,
                "total_task_minutes": 0,
                "total_delay_minutes": 0,
                "total_container_count": 0,
            }

        task_minutes = get_task_minutes(task_log)
        delay_minutes = sum(get_delay_minutes(delay) for delay in task_log.delay_logs)

        grouped_tasks[group_key]["completed_tasks"] += 1
        grouped_tasks[group_key]["total_task_minutes"] += task_minutes
        grouped_tasks[group_key]["total_delay_minutes"] += delay_minutes
        grouped_tasks[group_key]["total_container_count"] += task_log.container_count

    trend_rows = []
    for group_key, values in sorted(grouped_tasks.items()):
        effective_minutes = max(
            values["total_task_minutes"] - values["total_delay_minutes"],
            0,
        )
        moves_per_hour = None
        if effective_minutes > 0:
            moves_per_hour = round(
                values["total_container_count"] / (effective_minutes / 60),
                2,
            )

        trend_rows.append(
            ManagerPerformanceTrendItem(
                group_by=normalized_group,
                group_key=group_key,
                label=values["label"],
                completed_tasks=values["completed_tasks"],
                total_task_minutes=values["total_task_minutes"],
                total_delay_minutes=values["total_delay_minutes"],
                effective_work_minutes=effective_minutes,
                total_container_count=values["total_container_count"],
                moves_per_hour=moves_per_hour,
            )
        )

    return trend_rows
