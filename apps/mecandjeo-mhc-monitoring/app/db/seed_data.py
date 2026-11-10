"""Phase 6 default reference data and idempotent database seed helpers (reference values and sample cranes)."""

from sqlalchemy.orm import Session

from ..models import Crane, ReferenceData

# Nature of work: what the crane is doing. Code -> label shown to operators.
# Imports are discharged, so they fall under Discharging.
NATURE_OF_WORK_VALUES = {
    "discharging": "Discharging",
    "loading": "Loading",
    "loading_empties": "Loading - Empties",
    "loading_oog": "Loading - OOG",
    "other_work": "Other",
}

# Working area: where and how the work is done; a free open bay is different from across heights.
# Code -> label shown to operators.
WORKING_AREA_VALUES = {
    "port_side": "Port Side",
    "starboard_side": "Starboard Side",
    "deck_free_bay": "Deck Free Bay",
    "across_heights_portside": "Across Heights Portside",
    "underdeck_free_bay": "Underdeck Free Bay",
    "underdeck_across_heights": "Underdeck Across Heights",
    "tight_space": "Tight Space",
    "other": "Other",
}

# Standard delay values used by managers for reporting and trend analysis.
DELAY_TYPE_VALUES = [
    "awaiting_containers_empty",
    "awaiting_containers_export",
    "awaiting_trucks",
    "awaiting_clerks",
    "awaiting_stevedores",
    "control_room_modification",
    "wrong_instructions",
    "breakdown",
    "rainfall",
    "vessel_command_instructions",
    "crane_travelling",
    "other_delay",
]

# Short keys make delay reporting and familiar operational shorthand easier to scan.
DELAY_TYPE_KEYS = {
    "awaiting_containers_empty": "AConE",
    "awaiting_containers_export": "AConX",
    "awaiting_trucks": "AT",
    "awaiting_clerks": "AClerks",
    "awaiting_stevedores": "AStev",
    "control_room_modification": "CRM",
    "wrong_instructions": "WI",
    "breakdown": "BD",
    "rainfall": "RF",
    "vessel_command_instructions": "VCI",
    "crane_travelling": "CT",
    "other_delay": "OD",
}

# Phase 4: standard shift labels operators can select during login/start.
SHIFT_CODE_VALUES = [
    "A",
    "B",
    "C",
]


# Insert defaults only when absent, so the function is safe to run more than once.
def seed_reference_data(db: Session) -> int:
    """Insert default work, area, delay, and shift values; return the count added."""
    defaults = (
        [("nature_of_work", code, label, None) for code, label in NATURE_OF_WORK_VALUES.items()]
        + [("working_area", code, label, None) for code, label in WORKING_AREA_VALUES.items()]
        + [("delay_type", value, value.replace("_", " ").title(), DELAY_TYPE_KEYS.get(value)) for value in DELAY_TYPE_VALUES]
        + [("shift_code", value, f"Shift {value}", value) for value in SHIFT_CODE_VALUES]
    )
    created = 0
    for category, code, label, short_key in defaults:
        exists = db.query(ReferenceData).filter_by(category=category, code=code).first()
        if not exists:
            db.add(ReferenceData(category=category, code=code, label=label, short_key=short_key))
            created += 1
    db.commit()
    return created


# Phase 9: sample cranes for local demos only; gated by SEED_SAMPLE_DATA and never enabled in production.
SAMPLE_CRANE_NUMBERS = ["MHC-01", "MHC-02", "MHC-03"]


# Insert sample cranes only when absent, so the function is safe to run more than once.
def seed_sample_cranes(db: Session) -> int:
    """Insert sample MHC assets for local use; return the count added."""
    created = 0
    for mhc_number in SAMPLE_CRANE_NUMBERS:
        exists = db.query(Crane).filter(Crane.mhc_number == mhc_number).first()
        if not exists:
            db.add(
                Crane(
                    code=mhc_number,
                    mhc_number=mhc_number,
                    name=f"Mobile Harbour Crane {mhc_number[-2:]}",
                    is_active=True,
                )
            )
            created += 1
    db.commit()
    return created