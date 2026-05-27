from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..auth import get_current_user

router = APIRouter(prefix="/admin")


# Verify admin role [checks user role before allowing route access]. Role-based authorization. blocks non-admin users
def require_admin(current_user: User = Depends(get_current_user)):

    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,                   # 403 Forbidden: user is authenticated BUT lacks permission.
            detail="Admin access required"
        )

    return current_user


# Protected admin dashboard
@router.get("/dashboard")
def admin_dashboard(
    # current_user: User = Depends(get_current_user)        # for test purpose only
    current_user: User = Depends(require_admin)
):

    return {
        "message": f"Welcome Admin {current_user.email}",
        "status": "ok"
    }


# Protected admin user listing
@router.get("/users")
def admin_get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    return db.query(User).all()


# Protected user deletion
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






