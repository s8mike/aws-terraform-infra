from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import User

router = APIRouter(prefix="/admin")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Simple admin dashboard
@router.get("/dashboard")
def admin_dashboard():
    return {
        "message": "Admin dashboard",
        "status": "ok"
    }


# Get all users (admin view)
@router.get("/users")
def admin_get_users(db: Session = Depends(get_db)):
    return db.query(User).all()


# Delete a user (basic)
@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return {"error": "User not found"}

    db.delete(user)
    db.commit()

    return {"message": f"User {user_id} deleted"}