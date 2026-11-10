# Phase 5: manager delay analysis helpers.
from datetime import datetime

from sqlalchemy.orm import Session

from ..models import DelayLog
from ..schemas import ManagerDelayBreakdownItem


# Phase 5: apply optional date filters to a delay query.
def filter_delays_by_date(query, date_from: datetime | None, date_to: datetime | None):
    if date_from is not None:
        query = query.filter(DelayLog.started_at >= date_from)
    if date_to is not None:
        query = query.filter(DelayLog.started_at <= date_to)
    return query


# Phase 5: use stored duration or derive it when both timestamps are present.
def get_delay_minutes(delay_log: DelayLog) -> int:
    if delay_log.duration_minutes is not None:
        return delay_log.duration_minutes
    if delay_log.ended_at is None:
        return 0
    return int((delay_log.ended_at - delay_log.started_at).total_seconds() // 60)


# Phase 5: group delay logs by standard delay type plus optional custom label.
def build_delay_breakdown(
    db: Session,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> list[ManagerDelayBreakdownItem]:
    delay_query = filter_delays_by_date(db.query(DelayLog), date_from, date_to)
    grouped_delays = {}

    for delay_log in delay_query.all():
        group_key = (delay_log.delay_type, delay_log.custom_delay_type)
        if group_key not in grouped_delays:
            grouped_delays[group_key] = {
                "delay_count": 0,
                "total_delay_minutes": 0,
                "operator_controllable_count": 0,
            }

        grouped_delays[group_key]["delay_count"] += 1
        grouped_delays[group_key]["total_delay_minutes"] += get_delay_minutes(delay_log)
        if delay_log.is_operator_controllable:
            grouped_delays[group_key]["operator_controllable_count"] += 1

    return [
        ManagerDelayBreakdownItem(
            delay_type=delay_type,
            custom_delay_type=custom_delay_type,
            delay_count=values["delay_count"],
            total_delay_minutes=values["total_delay_minutes"],
            operator_controllable_count=values["operator_controllable_count"],
        )
        for (delay_type, custom_delay_type), values in sorted(grouped_delays.items())
    ]
