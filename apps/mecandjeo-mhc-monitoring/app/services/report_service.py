# Phase 7: historical performance report calculations and CSV serialization.
import csv
from datetime import datetime
from io import StringIO

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..models import DelayLog, TaskLog
from ..schemas import (
    PerformanceReportDelayItem,
    PerformanceReportRead,
    PerformanceReportSummary,
    PerformanceReportTaskItem,
)
from .delay_analysis_service import get_delay_minutes
from .performance_service import get_task_minutes


# Reject an inverted reporting period before executing a database query.
def validate_report_dates(date_from: datetime | None, date_to: datetime | None) -> None:
    if date_from and date_to and date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="date_from must be earlier than or equal to date_to",
        )


# Fetch completed task logs using optional report filters.
def get_report_tasks(
    db: Session,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    operator_id: int | None = None,
    crane_id: int | None = None,
    nature_of_work: str | None = None,
) -> list[TaskLog]:
    validate_report_dates(date_from, date_to)
    query = db.query(TaskLog).filter(TaskLog.status == "completed", TaskLog.ended_at.is_not(None))
    if date_from:
        query = query.filter(TaskLog.ended_at >= date_from)
    if date_to:
        query = query.filter(TaskLog.ended_at <= date_to)
    if operator_id is not None:
        query = query.filter(TaskLog.operator_id == operator_id)
    if crane_id is not None:
        query = query.filter(TaskLog.crane_id == crane_id)
    if nature_of_work:
        query = query.filter(TaskLog.nature_of_work == nature_of_work)
    return query.order_by(TaskLog.ended_at.asc(), TaskLog.id.asc()).all()


# Build the task rows, summary totals, and delay reasons from the selected tasks.
def build_performance_report(
    db: Session,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    operator_id: int | None = None,
    crane_id: int | None = None,
    nature_of_work: str | None = None,
) -> PerformanceReportRead:
    task_logs = get_report_tasks(db, date_from, date_to, operator_id, crane_id, nature_of_work)
    task_rows = []
    delay_groups: dict[tuple[str, str | None], dict[str, int]] = {}
    total_task_minutes = 0
    total_delay_minutes = 0
    total_container_count = 0

    for task_log in task_logs:
        task_minutes = get_task_minutes(task_log)
        task_delay_minutes = 0
        task_delay_reasons = []
        for delay_log in task_log.delay_logs:
            delay_minutes = get_delay_minutes(delay_log)
            task_delay_minutes += delay_minutes
            task_delay_reasons.append(delay_log.custom_delay_type or delay_log.delay_type)
            group = delay_groups.setdefault(
                (delay_log.delay_type, delay_log.custom_delay_type),
                {"delay_count": 0, "total_delay_minutes": 0},
            )
            group["delay_count"] += 1
            group["total_delay_minutes"] += delay_minutes

        effective_minutes = max(task_minutes - task_delay_minutes, 0)
        moves_per_hour = round(task_log.container_count / (effective_minutes / 60), 2) if effective_minutes else None
        total_task_minutes += task_minutes
        total_delay_minutes += task_delay_minutes
        total_container_count += task_log.container_count
        task_rows.append(
            PerformanceReportTaskItem(
                task_log_id=task_log.id,
                operator_id=task_log.operator_id,
                operator_name=task_log.operator.full_name,
                crane_id=task_log.crane_id,
                mhc_number=task_log.crane.mhc_number,
                nature_of_work=task_log.nature_of_work,
                working_area=task_log.working_area,
                vessel_name=task_log.vessel_name,
                started_at=task_log.started_at,
                ended_at=task_log.ended_at,
                task_minutes=task_minutes,
                delay_minutes=task_delay_minutes,
                delay_reasons=task_delay_reasons,
                effective_work_minutes=effective_minutes,
                container_count=task_log.container_count,
                moves_per_hour=moves_per_hour,
            )
        )

    effective_work_minutes = max(total_task_minutes - total_delay_minutes, 0)
    moves_per_hour = round(total_container_count / (effective_work_minutes / 60), 2) if effective_work_minutes else None
    delay_breakdown = [
        PerformanceReportDelayItem(
            delay_type=delay_type,
            custom_delay_type=custom_delay_type,
            delay_count=values["delay_count"],
            total_delay_minutes=values["total_delay_minutes"],
        )
        for (delay_type, custom_delay_type), values in sorted(delay_groups.items())
    ]
    return PerformanceReportRead(
        date_from=date_from,
        date_to=date_to,
        operator_id=operator_id,
        crane_id=crane_id,
        nature_of_work=nature_of_work,
        summary=PerformanceReportSummary(
            completed_tasks=len(task_rows),
            total_task_minutes=total_task_minutes,
            total_delay_minutes=total_delay_minutes,
            effective_work_minutes=effective_work_minutes,
            total_container_count=total_container_count,
            moves_per_hour=moves_per_hour,
        ),
        tasks=task_rows,
        delay_breakdown=delay_breakdown,
    )


# Serialize report task rows to RFC-compatible CSV text for direct download.
def serialize_report_csv(report: PerformanceReportRead) -> str:
    output = StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow([
        "task_log_id", "operator", "mhc_number", "nature_of_work", "working_area",
        "vessel_name", "started_at", "ended_at", "task_minutes", "delay_minutes", "delay_reasons",
        "effective_work_minutes", "container_count", "moves_per_hour",
    ])
    for task in report.tasks:
        writer.writerow([
            task.task_log_id, task.operator_name, task.mhc_number, task.nature_of_work,
            task.working_area, task.vessel_name or "", task.started_at.isoformat(),
            task.ended_at.isoformat(), task.task_minutes, task.delay_minutes, "; ".join(task.delay_reasons),
            task.effective_work_minutes, task.container_count, task.moves_per_hour or "",
        ])
    return output.getvalue()
