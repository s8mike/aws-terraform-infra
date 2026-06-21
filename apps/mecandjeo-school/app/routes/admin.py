from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    User,
    Student,
    Teacher,
    Course,
    Grade,
    Submission,
    Assignment,
    Parent,
    ParentStudentLink
)
from ..schemas import (
    AdminDashboardResponse,
    AdminUserResponse,
    UpdateUserRoleRequest,
    UpdateUserRoleResponse,
    AdminCourseResponse,
    AcademicOverviewResponse,
    ParentStudentLinkCreate,
    ParentStudentLinkResponse
)

from ..auth import require_admin   # import from app/auth.py

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


# Protected admin dashboard [Dashbaord Enhancement] phase 8.2 step 1
@router.get(
    "/dashboard",
    response_model=AdminDashboardResponse
)
def admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    return {
        "total_users": db.query(User).count(),
        "total_students": db.query(Student).count(),
        "total_teachers": db.query(Teacher).count(),
        "total_courses": db.query(Course).count(),
        "total_assignments": db.query(Assignment).count()
    }

# Protected admin user listing [User Management]-- Step 2
@router.get("/users")
def admin_get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    return db.query(User).all()

# Get single user
@router.get(
    "/users/{user_id}",
    response_model=AdminUserResponse
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


# Change user role [Role Management] phase 8.2 step 3
@router.put(
    "/users/{user_id}/role",
    response_model=UpdateUserRoleResponse
)
def update_user_role(
    user_id: int,
    request: UpdateUserRoleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    allowed_roles = [
        "student",
        "teacher",
        "admin"
    ]

    if request.role not in allowed_roles:
        raise HTTPException(
            status_code=400,
            detail="Invalid role"
        )

    user.role = request.role

    db.commit()
    db.refresh(user)

    return user


# Protected user deletion [User deletion]
@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    return {
        "message": f"User {user_id} deleted"
    }

@router.post(
    "/parent-student-links",
    response_model=ParentStudentLinkResponse
)
def create_parent_student_link(
    link_data: ParentStudentLinkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    parent = (
        db.query(Parent)
        .filter(
            Parent.id == link_data.parent_id
        )
        .first()
    )

    if not parent:
        raise HTTPException(
            status_code=404,
            detail="Parent not found"
        )

    student = (
        db.query(Student)
        .filter(
            Student.id == link_data.student_id
        )
        .first()
    )

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    existing_link = (
        db.query(ParentStudentLink)
        .filter(
            ParentStudentLink.parent_id == link_data.parent_id,
            ParentStudentLink.student_id == link_data.student_id
        )
        .first()
    )

    if existing_link:
        raise HTTPException(
            status_code=400,
            detail="Link already exists"
        )

    new_link = ParentStudentLink(
        parent_id=link_data.parent_id,
        student_id=link_data.student_id
    )

    db.add(new_link)
    db.commit()
    db.refresh(new_link)

    return new_link

# List all courses in the LMS [Course Oversight] -- Step 4
@router.get(
    "/courses",
    response_model=list[AdminCourseResponse]
)
def get_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    return db.query(Course).all()


# Institution academic overview  -- Step 5
@router.get(
    "/analytics",
    response_model=AcademicOverviewResponse
)
def academic_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    total_students = db.query(Student).count()

    total_courses = db.query(Course).count()

    total_assignments = db.query(Assignment).count()

    grades = db.query(Grade).all()

    average_grade = 0.0

    if grades:
        average_grade = (
            sum(g.grade_value for g in grades)
            / len(grades)
        )

    return {
        "total_students": total_students,
        "total_courses": total_courses,
        "total_assignments": total_assignments,
        "average_grade": round(
            average_grade,
            2
        )
    }

################################################
#The Basic starting Version.

# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from ..database import SessionLocal
# from ..models import User

# router = APIRouter(prefix="/admin")


# # Dependency
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# # Simple admin dashboard
# @router.get("/dashboard")
# def admin_dashboard():
#     return {
#         "message": "Admin dashboard",
#         "status": "ok"
#     }


# # Get all users (admin view)
# @router.get("/users")
# def admin_get_users(db: Session = Depends(get_db)):
#     return db.query(User).all()


# # Delete a user (basic)
# @router.delete("/users/{user_id}")
# def delete_user(user_id: int, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.id == user_id).first()

#     if not user:
#         return {"error": "User not found"}

#     db.delete(user)
#     db.commit()

#     return {"message": f"User {user_id} deleted"}






