# Phase 9: read-only lookup values so operator, manager, and admin forms can populate dropdowns.
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth import ROLE_ADMIN, ROLE_MANAGER, ROLE_OPERATOR, require_roles
from ..database import get_db
from ..models import Crane, ReferenceData, User
from ..schemas import LookupsRead


router = APIRouter()
any_role = Depends(require_roles(ROLE_OPERATOR, ROLE_MANAGER, ROLE_ADMIN))

LOOKUP_CATEGORIES = ("nature_of_work", "working_area", "delay_type", "shift_code")


# Return only active reference values and active MHC numbers; inactive records stay hidden.
@router.get("", response_model=LookupsRead)
def list_lookups(
    db: Session = Depends(get_db),
    current_user: User = any_role,
):
    rows = (
        db.query(ReferenceData)
        .filter(ReferenceData.is_active.is_(True), ReferenceData.category.in_(LOOKUP_CATEGORIES))
        .order_by(ReferenceData.category, ReferenceData.code)
        .all()
    )
    grouped = {category: [] for category in LOOKUP_CATEGORIES}
    for row in rows:
        grouped[row.category].append(row)
    cranes = db.query(Crane).filter(Crane.is_active.is_(True)).order_by(Crane.mhc_number).all()
    return {**grouped, "cranes": cranes}