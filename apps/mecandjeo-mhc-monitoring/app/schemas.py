# Defines request and response schemas for auth, crane, operator, and reporting APIs.
from datetime import datetime
from typing import Optional

# Phase 4 update: adds operator workflow request/response schemas.
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator



# Enables Pydantic response models to read values from SQLAlchemy objects.
class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# Shared user fields used by create and read payloads.
class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    role: str = Field(default="operator", max_length=50)
    is_active: bool = True


# Registration payload that includes the plain password before hashing.
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)

    # Phase 4 improvement: enforce stronger passwords before hashing.
    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, password: str) -> str:
        special_characters = set("!@#%$")
        if not any(character.islower() for character in password):
            raise ValueError("Password must include a lowercase letter")
        if not any(character.isupper() for character in password):
            raise ValueError("Password must include an uppercase letter")
        if not any(character.isdigit() for character in password):
            raise ValueError("Password must include a number")
        if not any(character in special_characters for character in password):
            raise ValueError("Password must include one of !, @, #, %, $")
        return password


# Public user response payload returned by API endpoints.
class UserRead(UserBase, ORMModel):
    id: int
    created_at: datetime
    updated_at: datetime


# Phase 6: admin payload for creating a managed account with a secure password.
class AdminUserCreate(UserCreate):
    pass


# Phase 6: all account fields are optional so admins can make focused updates.
class AdminUserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    password: Optional[str] = Field(default=None, min_length=8, max_length=128)
    role: Optional[str] = Field(default=None, max_length=50)
    is_active: Optional[bool] = None

    # Applies the same password strength policy to admin password resets.
    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, password: Optional[str]) -> Optional[str]:
        if password is None:
            return password
        special_characters = set("!@#%$")
        if not any(character.islower() for character in password):
            raise ValueError("Password must include a lowercase letter")
        if not any(character.isupper() for character in password):
            raise ValueError("Password must include an uppercase letter")
        if not any(character.isdigit() for character in password):
            raise ValueError("Password must include a number")
        if not any(character in special_characters for character in password):
            raise ValueError("Password must include one of !, @, #, %, $")
        return password


# Login payload accepted by the authentication endpoint.
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Token payload returned after successful authentication.
class TokenRead(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Shared operator profile fields, including default crane assignment.
class OperatorProfileBase(BaseModel):
    employee_number: Optional[str] = None
    certification_level: Optional[str] = None
    default_crane_id: Optional[int] = None


# Operator profile creation payload.
class OperatorProfileCreate(OperatorProfileBase):
    user_id: int


# Operator profile response payload.
class OperatorProfileRead(OperatorProfileBase, ORMModel):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


# Shared manager profile fields.
class ManagerProfileBase(BaseModel):
    department: Optional[str] = None
    phone_number: Optional[str] = None


# Manager profile creation payload.
class ManagerProfileCreate(ManagerProfileBase):
    user_id: int


# Manager profile response payload.
class ManagerProfileRead(ManagerProfileBase, ORMModel):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


# Shared admin profile fields.
class AdminProfileBase(BaseModel):
    department: Optional[str] = None


# Admin profile creation payload.
class AdminProfileCreate(AdminProfileBase):
    user_id: int


# Admin profile response payload.
class AdminProfileRead(AdminProfileBase, ORMModel):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


# Shared physical crane fields, including the operator-facing MHC number.
class CraneBase(BaseModel):
    code: str = Field(min_length=1, max_length=100)
    mhc_number: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=255)
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    capacity_tonnes: Optional[float] = None
    location: Optional[str] = None
    is_active: bool = True


# Crane creation payload.
class CraneCreate(CraneBase):
    pass


# Crane response payload.
class CraneRead(CraneBase, ORMModel):
    id: int
    created_at: datetime
    updated_at: datetime


# Phase 6: partial crane update payload for asset corrections and deactivation.
class CraneUpdate(BaseModel):
    code: Optional[str] = Field(default=None, min_length=1, max_length=100)
    mhc_number: Optional[str] = Field(default=None, min_length=1, max_length=100)
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    capacity_tonnes: Optional[float] = Field(default=None, ge=0)
    location: Optional[str] = None
    is_active: Optional[bool] = None


# Phase 6: shared fields for controlled work, area, delay, and shift reference data.
class ReferenceDataBase(BaseModel):
    category: str = Field(min_length=1, max_length=100)
    code: str = Field(min_length=1, max_length=100)
    label: str = Field(min_length=1, max_length=255)
    short_key: Optional[str] = Field(default=None, max_length=30)
    description: Optional[str] = None
    is_active: bool = True


# Phase 6: create an admin-managed reference value.
class ReferenceDataCreate(ReferenceDataBase):
    pass


# Phase 6: update one or more fields of an existing reference value.
class ReferenceDataUpdate(BaseModel):
    category: Optional[str] = Field(default=None, min_length=1, max_length=100)
    code: Optional[str] = Field(default=None, min_length=1, max_length=100)
    label: Optional[str] = Field(default=None, min_length=1, max_length=255)
    short_key: Optional[str] = Field(default=None, max_length=30)
    description: Optional[str] = None
    is_active: Optional[bool] = None


# Phase 6: reference value returned to the admin configuration screen.
class ReferenceDataRead(ReferenceDataBase, ORMModel):
    id: int
    created_at: datetime
    updated_at: datetime


# Shared shift fields captured when the operator logs into an MHC.
class ShiftBase(BaseModel):
    operator_id: int
    crane_id: int
    mhc_number: str = Field(min_length=1, max_length=100)
    shift_code: Optional[str] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    status: str = "active"
    notes: Optional[str] = None


# Phase 4 start-shift payload used when an operator logs into an MHC.
class ShiftStart(BaseModel):
    mhc_number: str = Field(min_length=1, max_length=100)
    shift_code: str = Field(min_length=1, max_length=10)
    started_at: datetime
    notes: Optional[str] = None


# Phase 4 end-shift payload. A closing action must provide an end timestamp.
class ShiftEnd(BaseModel):
    ended_at: datetime
    notes: Optional[str] = None


# Shift creation payload.
class ShiftCreate(ShiftBase):
    pass


# Shift response payload.
class ShiftRead(ShiftBase, ORMModel):
    id: int
    created_at: datetime
    updated_at: datetime


# Shared task log fields for crane production work.
class TaskLogBase(BaseModel):
    shift_id: int
    operator_id: int
    crane_id: int
    nature_of_work: str = Field(max_length=100)
    working_area: str = Field(max_length=100)
    vessel_name: Optional[str] = None
    bay_reference: Optional[str] = None
    container_count: int = Field(default=0, ge=0)
    started_at: datetime
    ended_at: Optional[datetime] = None
    status: str = "active"
    notes: Optional[str] = None


# Phase 4 task-start payload. The current operator is inferred from the JWT.
class TaskLogStart(BaseModel):
    shift_id: int
    nature_of_work: str = Field(max_length=100)
    working_area: str = Field(max_length=100)
    vessel_name: Optional[str] = None
    bay_reference: Optional[str] = None
    container_count: int = Field(default=0, ge=0)
    started_at: datetime
    notes: Optional[str] = None


# Phase 4 task-end payload. A closing action must provide an end timestamp.
class TaskLogEnd(BaseModel):
    ended_at: datetime
    container_count: Optional[int] = Field(default=None, ge=0)
    notes: Optional[str] = None


# Task log creation payload.
class TaskLogCreate(TaskLogBase):
    pass


# Task log response payload.
class TaskLogRead(TaskLogBase, ORMModel):
    id: int
    created_at: datetime
    updated_at: datetime


# Shared delay fields for standard and site-specific downtime reasons.
class DelayLogBase(BaseModel):
    task_log_id: int
    delay_type: str = Field(max_length=100)
    custom_delay_type: Optional[str] = Field(default=None, max_length=150)
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(default=None, ge=0)
    is_operator_controllable: bool = False
    notes: Optional[str] = None


# Phase 4 delay-start payload for downtime captured against an active task.
class DelayLogStart(BaseModel):
    task_log_id: int
    delay_type: str = Field(max_length=100)
    custom_delay_type: Optional[str] = Field(default=None, max_length=150)
    started_at: datetime
    is_operator_controllable: bool = False
    notes: Optional[str] = None


# Phase 4 delay-end payload. A closing action must provide an end timestamp.
class DelayLogEnd(BaseModel):
    ended_at: datetime
    duration_minutes: Optional[int] = Field(default=None, ge=0)
    notes: Optional[str] = None


# Delay log creation payload.
class DelayLogCreate(DelayLogBase):
    pass


# Delay log response payload.
class DelayLogRead(DelayLogBase, ORMModel):
    id: int
    created_at: datetime
    updated_at: datetime


# Shared working condition fields for environmental and operational context.
class WorkingConditionBase(BaseModel):
    shift_id: int
    weather_condition: Optional[str] = None
    visibility: Optional[str] = None
    wind_condition: Optional[str] = None
    deck_condition: Optional[str] = None
    congestion_level: Optional[str] = None
    notes: Optional[str] = None
    recorded_at: Optional[datetime] = None


# Working condition creation payload.
class WorkingConditionCreate(WorkingConditionBase):
    pass


# Working condition response payload.
class WorkingConditionRead(WorkingConditionBase, ORMModel):
    id: int
    recorded_at: datetime
    created_at: datetime
    updated_at: datetime


# Shared calculated performance metric fields.
class PerformanceSnapshotBase(BaseModel):
    shift_id: int
    task_log_id: Optional[int] = None
    operator_id: int
    total_task_minutes: int = Field(default=0, ge=0)
    total_delay_minutes: int = Field(default=0, ge=0)
    effective_work_minutes: int = Field(default=0, ge=0)
    container_count: int = Field(default=0, ge=0)
    moves_per_hour: Optional[float] = None
    snapshot_type: str = "shift"
    calculated_at: Optional[datetime] = None


# Performance snapshot creation payload.
class PerformanceSnapshotCreate(PerformanceSnapshotBase):
    pass


# Performance snapshot response payload.
class PerformanceSnapshotRead(PerformanceSnapshotBase, ORMModel):
    id: int
    calculated_at: datetime
    created_at: datetime
    updated_at: datetime


# Shared report export request and file metadata fields.
class ReportExportBase(BaseModel):
    requested_by_id: int
    report_type: str = Field(max_length=100)
    file_format: str = Field(max_length=50)
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    status: str = "requested"
    file_path: Optional[str] = None


# Report export creation payload.
class ReportExportCreate(ReportExportBase):
    pass


# Report export response payload.
class ReportExportRead(ReportExportBase, ORMModel):
    id: int
    created_at: datetime
    updated_at: datetime


# Audit log response payload for traceability screens and reviews.
class AuditLogRead(ORMModel):
    id: int
    actor_id: Optional[int]
    action: str
    entity_type: str
    entity_id: Optional[int]
    description: Optional[str]
    created_at: datetime


# Phase 4 operator summary response for quick personal performance feedback.
class OperatorSummaryRead(BaseModel):
    operator_id: int
    total_shifts: int
    active_shift_id: Optional[int]
    completed_tasks: int
    total_container_count: int
    total_delay_minutes: int


# Phase 5 manager dashboard totals for a quick operational snapshot.
class ManagerDashboardRead(BaseModel):
    total_operators: int
    total_cranes: int
    active_shifts: int
    active_tasks: int
    active_delays: int
    completed_tasks: int
    total_container_count: int
    total_delay_minutes: int


# Phase 5 live row showing what one active operator is doing now.
class ManagerLiveOperatorStatusRead(BaseModel):
    operator_id: int
    operator_name: str
    shift_id: int
    shift_code: Optional[str]
    mhc_number: str
    crane_id: int
    shift_started_at: datetime
    active_task_id: Optional[int]
    active_task_nature_of_work: Optional[str]
    active_delay_id: Optional[int]
    active_delay_type: Optional[str]
    status: str


# Phase 5 active shift row used by manager shift overview screens.
class ManagerActiveShiftRead(BaseModel):
    shift_id: int
    operator_id: int
    operator_name: str
    crane_id: int
    mhc_number: str
    shift_code: Optional[str]
    started_at: datetime
    active_task_count: int
    completed_task_count: int
    active_delay_count: int
    total_container_count: int


# Phase 5 delay totals grouped by standard and optional custom delay labels.
class ManagerDelayBreakdownItem(BaseModel):
    delay_type: str
    custom_delay_type: Optional[str]
    delay_count: int
    total_delay_minutes: int
    operator_controllable_count: int


# Phase 5 performance row grouped by operator, crane, work type, or date.
class ManagerPerformanceTrendItem(BaseModel):
    group_by: str
    group_key: str
    label: str
    completed_tasks: int
    total_task_minutes: int
    total_delay_minutes: int
    effective_work_minutes: int
    total_container_count: int
    moves_per_hour: Optional[float]


# Phase 7: report summary for completed tasks in the requested reporting period.
class PerformanceReportSummary(BaseModel):
    completed_tasks: int
    total_task_minutes: int
    total_delay_minutes: int
    effective_work_minutes: int
    total_container_count: int
    moves_per_hour: Optional[float]


# Phase 7: one completed task included in a historical performance report.
class PerformanceReportTaskItem(BaseModel):
    task_log_id: int
    operator_id: int
    operator_name: str
    crane_id: int
    mhc_number: str
    nature_of_work: str
    working_area: str
    vessel_name: Optional[str]
    started_at: datetime
    ended_at: datetime
    task_minutes: int
    delay_minutes: int
    delay_reasons: list[str]
    effective_work_minutes: int
    container_count: int
    moves_per_hour: Optional[float]


# Phase 7: delay totals included beside report production metrics for context.
class PerformanceReportDelayItem(BaseModel):
    delay_type: str
    custom_delay_type: Optional[str]
    delay_count: int
    total_delay_minutes: int


# Phase 7: date-filtered report payload returned to managers and administrators.
class PerformanceReportRead(BaseModel):
    date_from: Optional[datetime]
    date_to: Optional[datetime]
    operator_id: Optional[int]
    crane_id: Optional[int]
    nature_of_work: Optional[str]
    summary: PerformanceReportSummary
    tasks: list[PerformanceReportTaskItem]
    delay_breakdown: list[PerformanceReportDelayItem]


# Phase 9: read-only lookup payloads for operator, manager, and admin forms.


class LookupValueRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    label: str
    short_key: str | None = None


class LookupCraneRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    mhc_number: str


class LookupsRead(BaseModel):
    nature_of_work: list[LookupValueRead]
    working_area: list[LookupValueRead]
    delay_type: list[LookupValueRead]
    shift_code: list[LookupValueRead]
    cranes: list[LookupCraneRead]



# Phase 10: lets the operator UI restore the current shift, task, and delay after a page reload.
class OperatorActiveStateRead(ORMModel):
    shift: Optional[ShiftRead] = None
    task: Optional[TaskLogRead] = None
    delay: Optional[DelayLogRead] = None



# Phase 10: totals for one shift so the operator screen can show "this shift" figures.
class ShiftSummaryRead(BaseModel):
    shift_id: int
    mhc_number: str
    completed_tasks: int
    total_container_count: int
    total_delay_minutes: int


# Phase 10: shared password-strength rule for the self-service change-password request.
def _check_password_strength(password: str) -> str:
    special_characters = set("!@#%$")
    if not any(character.islower() for character in password):
        raise ValueError("Password must include a lowercase letter")
    if not any(character.isupper() for character in password):
        raise ValueError("Password must include an uppercase letter")
    if not any(character.isdigit() for character in password):
        raise ValueError("Password must include a number")
    if not any(character in special_characters for character in password):
        raise ValueError("Password must include one of !, @, #, %, $")
    return password


# Phase 10: request body for a signed-in user changing their own password.
class PasswordChange(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)

    # Apply the same strength policy used for registration and admin resets.
    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, password: str) -> str:
        return _check_password_strength(password)