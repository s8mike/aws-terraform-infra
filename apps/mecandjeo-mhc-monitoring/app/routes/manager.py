# Phase 5: manager supervision, dashboard, and analysis routes.
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..auth import ROLE_ADMIN, ROLE_MANAGER, require_roles
from ..database import get_db
from ..models import User
from ..schemas import (
    ManagerActiveShiftRead,
    ManagerDashboardRead,
    ManagerDelayBreakdownItem,
    ManagerLiveOperatorStatusRead,
    ManagerPerformanceTrendItem,
)
from ..services.dashboard_service import (
    build_active_shift_overview,
    build_live_operator_status,
    build_manager_dashboard,
)
from ..services.delay_analysis_service import build_delay_breakdown
from ..services.performance_service import build_performance_trends


# Phase 5: manager router exposes read-only operational visibility.
router = APIRouter()


# Phase 5: shared dependency keeps manager views limited to managers and admins.
manager_or_admin_user = Depends(require_roles(ROLE_MANAGER, ROLE_ADMIN))


# Phase 5: show high-level operational counts for manager dashboard cards.
@router.get("/dashboard", response_model=ManagerDashboardRead)
def read_manager_dashboard(
    db: Session = Depends(get_db),
    current_user: User = manager_or_admin_user,
):
    return build_manager_dashboard(db)


# Phase 5: show current operator, task, MHC, and delay status for active shifts.
@router.get(
    "/operators/live-status",
    response_model=list[ManagerLiveOperatorStatusRead],
)
def read_operator_live_status(
    db: Session = Depends(get_db),
    current_user: User = manager_or_admin_user,
):
    return build_live_operator_status(db)


# Phase 5: show active shifts with task and delay counts.
@router.get("/shifts/active", response_model=list[ManagerActiveShiftRead])
def read_active_shift_overview(
    db: Session = Depends(get_db),
    current_user: User = manager_or_admin_user,
):
    return build_active_shift_overview(db)


# Phase 5: summarize delay counts and minutes by delay category.
@router.get("/delays/breakdown", response_model=list[ManagerDelayBreakdownItem])
def read_delay_breakdown(
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = manager_or_admin_user,
):
    return build_delay_breakdown(db, date_from=date_from, date_to=date_to)


# Phase 5: summarize completed work by operator, crane, work type, or date.
@router.get("/performance/trends", response_model=list[ManagerPerformanceTrendItem])
def read_performance_trends(
    group_by: str = Query(default="operator"),
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = manager_or_admin_user,
):
    return build_performance_trends(
        db,
        group_by=group_by,
        date_from=date_from,
        date_to=date_to,
    )

