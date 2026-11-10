# Phase 7: manager and admin historical report and CSV export routes.
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from ..auth import ROLE_ADMIN, ROLE_MANAGER, require_roles
from ..database import get_db
from ..models import ReportExport, User
from ..schemas import PerformanceReportRead, ReportExportRead
from ..services.report_service import build_performance_report, serialize_report_csv


# Phase 7: groups protected historical report and export endpoints.
router = APIRouter()
manager_or_admin_user = Depends(require_roles(ROLE_MANAGER, ROLE_ADMIN))


# Return completed-task performance with delay context as JSON for report screens.
@router.get("/performance", response_model=PerformanceReportRead)
def read_performance_report(
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    operator_id: int | None = Query(default=None, ge=1),
    crane_id: int | None = Query(default=None, ge=1),
    nature_of_work: str | None = Query(default=None, max_length=100),
    db: Session = Depends(get_db),
    current_user: User = manager_or_admin_user,
):
    return build_performance_report(db, date_from, date_to, operator_id, crane_id, nature_of_work)


# Stream a CSV report and persist export metadata without relying on container disk.
@router.get("/performance.csv")
def export_performance_csv(
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    operator_id: int | None = Query(default=None, ge=1),
    crane_id: int | None = Query(default=None, ge=1),
    nature_of_work: str | None = Query(default=None, max_length=100),
    db: Session = Depends(get_db),
    current_user: User = manager_or_admin_user,
):
    report = build_performance_report(db, date_from, date_to, operator_id, crane_id, nature_of_work)
    export = ReportExport(
        requested_by_id=current_user.id,
        report_type="historical_performance",
        file_format="csv",
        date_from=date_from,
        date_to=date_to,
        status="completed",
        file_path="inline://historical-performance.csv",
    )
    db.add(export)
    db.commit()
    return Response(
        content=serialize_report_csv(report),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=historical-performance.csv"},
    )


# Let managers see their export history, while admins can inspect all export metadata.
@router.get("/exports", response_model=list[ReportExportRead])
def list_report_exports(
    db: Session = Depends(get_db),
    current_user: User = manager_or_admin_user,
):
    query = db.query(ReportExport)
    if current_user.role != ROLE_ADMIN:
        query = query.filter(ReportExport.requested_by_id == current_user.id)
    return query.order_by(ReportExport.created_at.desc()).all()
