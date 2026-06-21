from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    User, 
    Parent,
    Student,
    ParentStudentLink,
    Submission,
    Grade,
    Attendance
)
from ..schemas import (
    ParentCreate,
    ParentRegistrationResponse,
    ParentStudentProfileResponse,
    ParentAcademicPerformanceResponse,
    ParentAttendanceResponse,
    ParentRiskAlertResponse,
    ParentDashboardResponse
)
from ..auth import hash_password

router = APIRouter(
    prefix="/parents",
    tags=["Parents"]
)

@router.post(
    "/register",
    response_model=ParentRegistrationResponse
)
def register_parent(
    parent_data: ParentCreate,
    db: Session = Depends(get_db)
):

    existing_user = (
        db.query(User)
        .filter(
            User.email == parent_data.email
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = User(
        email=parent_data.email,
        password=hash_password(
            parent_data.password
        ),
        role="parent"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    new_parent = Parent(
        user_id=new_user.id,
        full_name=parent_data.full_name,
        phone_number=parent_data.phone_number
    )

    db.add(new_parent)
    db.commit()
    db.refresh(new_parent)

    return {
        "id": new_parent.id,
        "email": new_user.email,
        "role": new_user.role,
        "full_name": new_parent.full_name,
        "phone_number": new_parent.phone_number
    }

from ..auth import require_parent

# ================================
# Parent student profile 
# ================================
@router.get(
    "/students",
    response_model=list[
        ParentStudentProfileResponse
    ]
)
def get_linked_students(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_parent)
):
# # This is commented out because it is centralized in auth.py
    # if current_user.role != "parent":
    #     raise HTTPException(
    #         status_code=403,
    #         detail="Parent access required"
    #     )

    parent = (
        db.query(Parent)
        .filter(
            Parent.user_id == current_user.id
        )
        .first()
    )

    if not parent:
        raise HTTPException(
            status_code=404,
            detail="Parent profile not found"
        )

    links = (
        db.query(ParentStudentLink)
        .filter(
            ParentStudentLink.parent_id == parent.id
        )
        .all()
    )

    results = []

    for link in links:

        student = (
            db.query(Student)
            .filter(
                Student.id == link.student_id
            )
            .first()
        )

        if student:
            results.append({
                "student_id": student.id,
                "full_name": student.full_name,
                "grade": student.grade
            })

    return results

# ======================================
# Parent academic performance view
# ======================================

@router.get(
    "/academic-performance",
    response_model=list[
        ParentAcademicPerformanceResponse
    ]
)
def get_academic_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_parent)
):

    parent = (
        db.query(Parent)
        .filter(
            Parent.user_id == current_user.id
        )
        .first()
    )

    if not parent:
        raise HTTPException(
            status_code=404,
            detail="Parent profile not found"
        )

    links = (
        db.query(ParentStudentLink)
        .filter(
            ParentStudentLink.parent_id == parent.id
        )
        .all()
    )

    results = []

    for link in links:

        student = (
            db.query(Student)
            .filter(
                Student.id == link.student_id
            )
            .first()
        )

        if not student:
            continue

        submissions = (
            db.query(Submission)
            .filter(
                Submission.student_id == student.id
            )
            .all()
        )

        assignments_completed = len(submissions)

        grades = (
            db.query(Grade)
            .join(
                Submission,
                Grade.submission_id == Submission.id
            )
            .filter(
                Submission.student_id == student.id
            )
            .all()
        )

        average_grade = 0.0

        if grades:
            average_grade = (
                sum(
                    grade.grade_value
                    for grade in grades
                )
                / len(grades)
            )

        results.append({
            "student_id": student.id,
            "student_name": student.full_name,
            "average_grade": round(
                average_grade,
                2
            ),
            "assignments_completed":
                assignments_completed
        })

    return results

# =============================
# Parent attendance monitoring
# =============================

@router.get(
    "/attendance",
    response_model=list[
        ParentAttendanceResponse
    ]
)
def get_attendance_monitoring(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_parent)
):

    parent = (
        db.query(Parent)
        .filter(
            Parent.user_id == current_user.id
        )
        .first()
    )

    if not parent:
        raise HTTPException(
            status_code=404,
            detail="Parent profile not found"
        )

    links = (
        db.query(ParentStudentLink)
        .filter(
            ParentStudentLink.parent_id == parent.id
        )
        .all()
    )

    results = []

    for link in links:

        student = (
            db.query(Student)
            .filter(
                Student.id == link.student_id
            )
            .first()
        )

        if not student:
            continue

        attendance_records = (
            db.query(Attendance)
            .filter(
                Attendance.student_id == student.id
            )
            .all()
        )

        total_records = len(
            attendance_records
        )

        present = sum(
            1
            for record in attendance_records
            if record.status.lower() == "present"
        )

        absent = sum(
            1
            for record in attendance_records
            if record.status.lower() == "absent"
        )

        late = sum(
            1
            for record in attendance_records
            if record.status.lower() == "late"
        )

        attendance_percentage = 0.0

        if total_records > 0:
            attendance_percentage = (
                present / total_records
            ) * 100

        results.append({
            "student_id": student.id,
            "student_name": student.full_name,
            "attendance_percentage": round(
                attendance_percentage,
                2
            ),
            "total_records": total_records,
            "present": present,
            "absent": absent,
            "late": late
        })

    return results

# ======================
# Parent risk alerts
# ======================
@router.get(
    "/risk-alerts",
    response_model=list[
        ParentRiskAlertResponse
    ]
)
def get_parent_risk_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_parent)
):

    parent = (
        db.query(Parent)
        .filter(
            Parent.user_id == current_user.id
        )
        .first()
    )

    if not parent:
        raise HTTPException(
            status_code=404,
            detail="Parent profile not found"
        )

    links = (
        db.query(ParentStudentLink)
        .filter(
            ParentStudentLink.parent_id == parent.id
        )
        .all()
    )

    results = []

    for link in links:

        student = (
            db.query(Student)
            .filter(
                Student.id == link.student_id
            )
            .first()
        )

        if not student:
            continue

        grades = (
            db.query(Grade)
            .join(
                Submission,
                Grade.submission_id == Submission.id
            )
            .filter(
                Submission.student_id == student.id
            )
            .all()
        )

        average_grade = 0.0

        if grades:
            average_grade = (
                sum(
                    grade.grade_value
                    for grade in grades
                )
                / len(grades)
            )

        attendance_records = (
            db.query(Attendance)
            .filter(
                Attendance.student_id == student.id
            )
            .all()
        )

        total_records = len(
            attendance_records
        )

        present_count = sum(
            1
            for record in attendance_records
            if record.status.lower() == "present"
        )

        attendance_percentage = 0.0

        if total_records > 0:
            attendance_percentage = (
                present_count / total_records
            ) * 100

        at_risk = (
            average_grade < 50
            or attendance_percentage < 75
        )

        risk_level = (
            "High"
            if at_risk
            else "Low"
        )

        reason = (
            "Academic intervention recommended."
            if at_risk
            else "Strong grades and attendance."
        )

        results.append({
            "student_id": student.id,
            "student_name": student.full_name,
            "at_risk": at_risk,
            "risk_level": risk_level,
            "reason": reason
        })

    return results

# ============================
# Parent dashboard summary
# ============================
@router.get(
    "/dashboard",
    response_model=list[
        ParentDashboardResponse
    ]
)
def get_parent_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_parent)
):

    parent = (
        db.query(Parent)
        .filter(
            Parent.user_id == current_user.id
        )
        .first()
    )

    if not parent:
        raise HTTPException(
            status_code=404,
            detail="Parent profile not found"
        )

    links = (
        db.query(ParentStudentLink)
        .filter(
            ParentStudentLink.parent_id == parent.id
        )
        .all()
    )

    results = []

    for link in links:

        student = (
            db.query(Student)
            .filter(
                Student.id == link.student_id
            )
            .first()
        )

        if not student:
            continue

        submissions = (
            db.query(Submission)
            .filter(
                Submission.student_id == student.id
            )
            .all()
        )

        assignments_completed = len(
            submissions
        )

        grades = (
            db.query(Grade)
            .join(
                Submission,
                Grade.submission_id == Submission.id
            )
            .filter(
                Submission.student_id == student.id
            )
            .all()
        )

        average_grade = 0.0

        if grades:
            average_grade = (
                sum(
                    grade.grade_value
                    for grade in grades
                )
                / len(grades)
            )

        attendance_records = (
            db.query(Attendance)
            .filter(
                Attendance.student_id == student.id
            )
            .all()
        )

        total_attendance_records = len(
            attendance_records
        )

        present_count = sum(
            1
            for record in attendance_records
            if record.status.lower() == "present"
        )

        attendance_percentage = 0.0

        if total_attendance_records > 0:
            attendance_percentage = (
                present_count
                / total_attendance_records
            ) * 100

        at_risk = (
            average_grade < 50
            or attendance_percentage < 75
        )

        risk_level = (
            "High"
            if at_risk
            else "Low"
        )

        risk_reason = (
            "Academic intervention recommended."
            if at_risk
            else "Strong grades and attendance."
        )

        results.append({
            "student_id": student.id,
            "student_name": student.full_name,
            "grade": student.grade,

            "average_grade": round(
                average_grade,
                2
            ),
            "assignments_completed":
                assignments_completed,

            "attendance_percentage":
                round(
                    attendance_percentage,
                    2
                ),
            "total_attendance_records":
                total_attendance_records,

            "at_risk": at_risk,
            "risk_level": risk_level,
            "risk_reason": risk_reason
        })

    return results