from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .database import Base


# Returns timezone-aware UTC timestamps for database defaults.
def utc_now():
    return datetime.now(timezone.utc)


# Adds common creation and update timestamps to business records.
class TimestampMixin:
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(
        DateTime,
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )


# Stores login identity, role, and account status for every user.
class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="operator")
    is_active = Column(Boolean, nullable=False, default=True)

    # Connects a user to role-specific profiles and activity history.
    operator_profile = relationship(
        "OperatorProfile",
        back_populates="user",
        uselist=False,
    )
    manager_profile = relationship(
        "ManagerProfile",
        back_populates="user",
        uselist=False,
    )
    admin_profile = relationship(
        "AdminProfile",
        back_populates="user",
        uselist=False,
    )
    shifts = relationship("Shift", back_populates="operator")
    report_exports = relationship("ReportExport", back_populates="requested_by")
    audit_logs = relationship("AuditLog", back_populates="actor")


# Stores operator-specific details and an optional default crane assignment.
class OperatorProfile(Base, TimestampMixin):
    __tablename__ = "operator_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    employee_number = Column(String(100), unique=True, nullable=True)
    certification_level = Column(String(100), nullable=True)
    default_crane_id = Column(Integer, ForeignKey("cranes.id"), nullable=True)

    user = relationship("User", back_populates="operator_profile")
    default_crane = relationship("Crane", back_populates="default_operators")


# Stores manager-specific details used by dashboard and reporting workflows.
class ManagerProfile(Base, TimestampMixin):
    __tablename__ = "manager_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    department = Column(String(150), nullable=True)
    phone_number = Column(String(50), nullable=True)

    user = relationship("User", back_populates="manager_profile")


# Stores admin-specific details used by configuration workflows.
class AdminProfile(Base, TimestampMixin):
    __tablename__ = "admin_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    department = Column(String(150), nullable=True)

    user = relationship("User", back_populates="admin_profile")


# Stores each physical Mobile Harbour Crane asset.
class Crane(Base, TimestampMixin):
    __tablename__ = "cranes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), unique=True, index=True, nullable=False)
    mhc_number = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    manufacturer = Column(String(150), nullable=True)
    model = Column(String(150), nullable=True)
    capacity_tonnes = Column(Float, nullable=True)
    location = Column(String(255), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    # Tracks which operators, shifts, and tasks are associated with this crane.
    default_operators = relationship("OperatorProfile", back_populates="default_crane")
    shifts = relationship("Shift", back_populates="crane")
    task_logs = relationship("TaskLog", back_populates="crane")


# Phase 6: stores admin-managed choices used by operator forms and reporting.
class ReferenceData(Base, TimestampMixin):
    __tablename__ = "reference_data"
    __table_args__ = (
        UniqueConstraint("category", "code", name="uq_reference_data_category_code"),
    )

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), nullable=False, index=True)
    code = Column(String(100), nullable=False)
    label = Column(String(255), nullable=False)
    short_key = Column(String(30), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)


# Stores an operator's login/operation session for a selected MHC.
class Shift(Base, TimestampMixin):
    __tablename__ = "shifts"

    id = Column(Integer, primary_key=True, index=True)
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    crane_id = Column(Integer, ForeignKey("cranes.id"), nullable=False)
    mhc_number = Column(String(100), nullable=False)
    shift_code = Column(String(100), nullable=True)
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    status = Column(String(50), nullable=False, default="active")
    notes = Column(Text, nullable=True)

    # Groups tasks, conditions, and performance snapshots for one operation period.
    operator = relationship("User", back_populates="shifts")
    crane = relationship("Crane", back_populates="shifts")
    task_logs = relationship("TaskLog", back_populates="shift")
    working_conditions = relationship("WorkingCondition", back_populates="shift")
    performance_snapshots = relationship("PerformanceSnapshot", back_populates="shift")


# Stores one unit of crane work performed during a shift.
class TaskLog(Base, TimestampMixin):
    __tablename__ = "task_logs"

    id = Column(Integer, primary_key=True, index=True)
    shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=False)
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    crane_id = Column(Integer, ForeignKey("cranes.id"), nullable=False)
    nature_of_work = Column(String(100), nullable=False)
    working_area = Column(String(100), nullable=False)
    vessel_name = Column(String(255), nullable=True)
    bay_reference = Column(String(100), nullable=True)
    container_count = Column(Integer, nullable=False, default=0)
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    status = Column(String(50), nullable=False, default="active")
    notes = Column(Text, nullable=True)

    # Links task activity to the shift, crane, delays, and performance outputs.
    shift = relationship("Shift", back_populates="task_logs")
    operator = relationship("User")
    crane = relationship("Crane", back_populates="task_logs")
    delay_logs = relationship("DelayLog", back_populates="task_log")
    performance_snapshots = relationship("PerformanceSnapshot", back_populates="task_log")


# Stores downtime attached to a task, including standard and custom delay types.
class DelayLog(Base, TimestampMixin):
    __tablename__ = "delay_logs"

    id = Column(Integer, primary_key=True, index=True)
    task_log_id = Column(Integer, ForeignKey("task_logs.id"), nullable=False)
    delay_type = Column(String(100), nullable=False)
    custom_delay_type = Column(String(150), nullable=True)
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    is_operator_controllable = Column(Boolean, nullable=False, default=False)
    notes = Column(Text, nullable=True)

    # Keeps delay records tied to the task affected by the downtime.
    task_log = relationship("TaskLog", back_populates="delay_logs")


# Stores weather and operational conditions that affect performance context.
class WorkingCondition(Base, TimestampMixin):
    __tablename__ = "working_conditions"

    id = Column(Integer, primary_key=True, index=True)
    shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=False)
    weather_condition = Column(String(100), nullable=True)
    visibility = Column(String(100), nullable=True)
    wind_condition = Column(String(100), nullable=True)
    deck_condition = Column(String(100), nullable=True)
    congestion_level = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    recorded_at = Column(DateTime, default=utc_now, nullable=False)

    # Associates recorded conditions with the shift where they were observed.
    shift = relationship("Shift", back_populates="working_conditions")


# Stores calculated performance metrics for tasks, shifts, or reporting periods.
class PerformanceSnapshot(Base, TimestampMixin):
    __tablename__ = "performance_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=False)
    task_log_id = Column(Integer, ForeignKey("task_logs.id"), nullable=True)
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_task_minutes = Column(Integer, nullable=False, default=0)
    total_delay_minutes = Column(Integer, nullable=False, default=0)
    effective_work_minutes = Column(Integer, nullable=False, default=0)
    container_count = Column(Integer, nullable=False, default=0)
    moves_per_hour = Column(Float, nullable=True)
    snapshot_type = Column(String(50), nullable=False, default="shift")
    calculated_at = Column(DateTime, default=utc_now, nullable=False)

    # Preserves source shift, task, and operator context for each calculation.
    shift = relationship("Shift", back_populates="performance_snapshots")
    task_log = relationship("TaskLog", back_populates="performance_snapshots")
    operator = relationship("User")


# Stores report export requests and generated report file metadata.
class ReportExport(Base, TimestampMixin):
    __tablename__ = "report_exports"

    id = Column(Integer, primary_key=True, index=True)
    requested_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    report_type = Column(String(100), nullable=False)
    file_format = Column(String(50), nullable=False)
    date_from = Column(DateTime, nullable=True)
    date_to = Column(DateTime, nullable=True)
    status = Column(String(50), nullable=False, default="requested")
    file_path = Column(String(500), nullable=True)

    # Links each report export to the user who requested it.
    requested_by = relationship("User", back_populates="report_exports")


# Stores important user and system actions for traceability.
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(150), nullable=False)
    entity_type = Column(String(150), nullable=False)
    entity_id = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    # Actor is nullable to allow system-generated audit events.
    actor = relationship("User", back_populates="audit_logs")
