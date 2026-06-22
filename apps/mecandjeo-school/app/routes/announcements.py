from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..auth import get_current_user

from ..models import (
    Announcement,
    Teacher,
    User,
    AnnouncementRead,
    Student,
    Notification
)

from ..schemas import (
    AnnouncementCreate,
    AnnouncementResponse,
    AnnouncementReadResponse,
    NotificationResponse,
    CommunicationDashboardResponse
)

router = APIRouter(
    prefix="/announcements",
    tags=["Announcements"]
)


# Create announcement
@router.post(
    "/",
    response_model=AnnouncementResponse
)
def create_announcement(
    payload: AnnouncementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    teacher = (
        db.query(Teacher)
        .filter(
            Teacher.user_id == current_user.id
        )
        .first()
    )

    if not teacher:
        raise HTTPException(
            status_code=403,
            detail="Teacher profile not found"
        )

    announcement = Announcement(
        teacher_id=teacher.id,
        title=payload.title,
        message=payload.message,
        course_id=payload.course_id
    )

    db.add(announcement)
    db.commit()
    db.refresh(announcement)

    return announcement

# List announcements
@router.get(
    "/",
    response_model=list[AnnouncementResponse]
)
def get_announcements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # No restriction. Announcenment is for all users
):

    announcements = (
        db.query(Announcement)
        .order_by(
            Announcement.id.desc()
        )
        .all()
    )

    return announcements

# Mark announcement as read
@router.post(
    "/{announcement_id}/read",
    response_model=AnnouncementReadResponse
)
def mark_announcement_read(
    announcement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    student = (
        db.query(Student)
        .filter(
            Student.user_id == current_user.id
        )
        .first()
    )

    if not student:
        raise HTTPException(
            status_code=403,
            detail="Student profile not found"
        )

    announcement = (
        db.query(Announcement)
        .filter(
            Announcement.id == announcement_id
        )
        .first()
    )

    if not announcement:
        raise HTTPException(
            status_code=404,
            detail="Announcement not found"
        )

    existing_read = (
        db.query(AnnouncementRead)
        .filter(
            AnnouncementRead.student_id == student.id,
            AnnouncementRead.announcement_id == announcement_id
        )
        .first()
    )

    if existing_read:
        return existing_read

    read_record = AnnouncementRead(
        student_id=student.id,
        announcement_id=announcement_id
    )

    db.add(read_record)
    db.commit()
    db.refresh(read_record)

    return read_record

# Notification center
@router.get(
    "/notifications",
    response_model=list[NotificationResponse]
)
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    student = (
        db.query(Student)
        .filter(
            Student.user_id == current_user.id
        )
        .first()
    )

    if not student:
        raise HTTPException(
            status_code=403,
            detail="Student profile not found"
        )

    notifications = (
        db.query(Notification)
        .filter(
            Notification.student_id == student.id
        )
        .order_by(
            Notification.id.desc()
        )
        .all()
    )

    return notifications

# Communication dashboard
@router.get(
    "/dashboard",
    response_model=CommunicationDashboardResponse
)
def communication_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    student = (
        db.query(Student)
        .filter(
            Student.user_id == current_user.id
        )
        .first()
    )

    if not student:
        raise HTTPException(
            status_code=403,
            detail="Student profile not found"
        )

    total_announcements = (
        db.query(Announcement)
        .count()
    )

    unread_announcements = (
        total_announcements -
        db.query(AnnouncementRead)
        .filter(
            AnnouncementRead.student_id == student.id
        )
        .count()
    )

    total_notifications = (
        db.query(Notification)
        .filter(
            Notification.student_id == student.id
        )
        .count()
    )

    unread_notifications = (
        db.query(Notification)
        .filter(
            Notification.student_id == student.id,
            Notification.is_read == False
        )
        .count()
    )

    return {
        "total_announcements": total_announcements,
        "unread_announcements": unread_announcements,
        "total_notifications": total_notifications,
        "unread_notifications": unread_notifications
    }