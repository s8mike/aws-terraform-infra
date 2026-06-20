# This file was added to routes/ as the app evolves towards a more modular structure. It contains the routes related to students.

# Student profile management

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    Student, 
    User,
    Enrollment,
    Course,
    Assignment,
    Submission,
    Grade,
    Announcement,
    AnnouncementRead,
    Notification,
    Attendance
) 
from ..schemas import (
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    StudentDashboardResponse,
    MyCourseResponse,
    MyAssignmentResponse,
    AssignmentSubmissionStatusResponse,
    GradeHistoryResponse,
    StudentAnalyticsResponse,
    StudentPassFailResponse,
    StudentGradeDistributionResponse,
    StudentProgressReportResponse,
    StudentRankingResponse,
    StudentAnnouncementResponse,
    StudentCourseAnnouncementResponse,
    UnreadAnnouncementResponse,
    AnnouncementReadResponse,
    AnnouncementHistoryResponse,
    AssignmentNotificationResponse,
    GradeNotificationResponse,
    AnnouncementNotificationResponse,
    NotificationDashboardResponse,
    NotificationReadResponse,
    AttendanceHistoryResponse,
    AttendanceStatisticsResponse,
    AttendanceAnalyticsResponse,
    AttendanceAlertResponse
)
from ..auth import (
    get_current_user,
    require_student
)

router = APIRouter(
    prefix="/students", 
    tags=["Students"]
)


# Create student profile
@router.post("/", response_model=StudentResponse)
def create_student_profile(
    student: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Prevent duplicate student profiles
    existing_profile = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if existing_profile:
        raise HTTPException(
            status_code=400,
            detail="Student profile already exists"
        )

    profile = Student(
        user_id=current_user.id,
        grade=student.grade,
        full_name=student.full_name
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return profile

# Get current student's profile
@router.get("/me", response_model=StudentResponse)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    profile = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    return profile

# Update current student's profile
@router.put("/me", response_model=StudentResponse)
def update_my_profile(
    student_data: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    profile = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    profile.grade = student_data.grade
    profile.full_name = student_data.full_name

    db.commit()
    db.refresh(profile)

    return profile


# Student dashboard  [Phase 6.2 step1]
@router.get(
    "/dashboard",
    response_model=StudentDashboardResponse
)
def student_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student)
):

    student = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    # Count enrolled courses
    total_courses = db.query(Enrollment).filter(
        Enrollment.student_id == student.id
    ).count()

    # Count submissions
    total_submissions = db.query(Submission).filter(
        Submission.student_id == student.id
    ).count()

    # Count grades
    total_grades = db.query(Grade).join(
        Submission
    ).filter(
        Submission.student_id == student.id
    ).count()

    # Count assignments from enrolled courses
    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == student.id
    ).all()

    total_assignments = 0

    for enrollment in enrollments:

        assignment_count = db.query(Assignment).filter(
            Assignment.course_id == enrollment.course_id
        ).count()

        total_assignments += assignment_count

    return {
        "total_courses": total_courses,
        "total_assignments": total_assignments,
        "total_submissions": total_submissions,
        "total_grades": total_grades
    }

# My courses
@router.get(
    "/my-courses",
    response_model=list[MyCourseResponse]
)
def get_my_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student)
):

    student = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == student.id
    ).all()

    results = []

    for enrollment in enrollments:

        course = db.query(Course).filter(
            Course.id == enrollment.course_id
        ).first()

        if course:

            results.append(
                {
                    "course_id": course.id,
                    "title": course.title
                }
            )

    return results


# My assignments
@router.get(
    "/my-assignments",
    response_model=list[MyAssignmentResponse]   # Multiple assignments
)
def get_my_assignments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student)
):

    student = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == student.id
    ).all()       # All enrolled courses

    results = []

    for enrollment in enrollments:

        assignments = db.query(Assignment).filter(
            Assignment.course_id == enrollment.course_id
        ).all()

        for assignment in assignments:

            results.append(
                {
                    "assignment_id": assignment.id,
                    "title": assignment.title
                }
            )

    return results


# Assignment submission status
@router.get(
    "/assignment-submission-status",
    response_model=list[AssignmentSubmissionStatusResponse]
)
def get_assignment_submission_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student)
):

    student = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == student.id
    ).all()

    results = []

    for enrollment in enrollments:

        assignments = db.query(Assignment).filter(
            Assignment.course_id == enrollment.course_id
        ).all()

        for assignment in assignments:

            submission = db.query(Submission).filter(
                Submission.assignment_id == assignment.id,
                Submission.student_id == student.id
            ).first()

            results.append(
                {
                    "assignment_id": assignment.id,
                    "title": assignment.title,
                    "submitted": submission is not None  # Converts submission to "True" if found and "False" if not found
                }
            )

    return results


# Grade history
@router.get(
    "/grade-history",
    response_model=list[GradeHistoryResponse]
)
def get_grade_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student)
):

    student = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    submissions = db.query(Submission).filter(
        Submission.student_id == student.id
    ).all()

    results = []

    for submission in submissions:

        grade = db.query(Grade).filter(
            Grade.submission_id == submission.id
        ).first()

        if grade:

            results.append(
                {
                    "assignment_id": submission.assignment_id,
                    "grade_value": grade.grade_value,
                    "feedback": grade.feedback
                }
            )

    return results


# Student performance analytics
@router.get(
    "/performance-analytics",
    response_model=StudentAnalyticsResponse
)
def get_performance_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student)
):

    student = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    submissions = db.query(Submission).filter(
        Submission.student_id == student.id
    ).all()

    grades = []

    for submission in submissions:

        grade = db.query(Grade).filter(
            Grade.submission_id == submission.id
        ).first()

        if grade:
            grades.append(grade.grade_value)

    average_grade = 0.0

    if grades:
        average_grade = sum(grades) / len(grades)

    return {
        "student_id": student.id,
        "average_grade": average_grade
    }


# Student pass / fail statistics
@router.get(
    "/pass-fail-statistics",
    response_model=StudentPassFailResponse
)
def get_student_pass_fail_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student)
):

    student = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    submissions = db.query(Submission).filter(
        Submission.student_id == student.id
    ).all()

    passed = 0
    failed = 0

    for submission in submissions:

        grade = db.query(Grade).filter(
            Grade.submission_id == submission.id
        ).first()

        if grade:

            if grade.grade_value >= 50:
                passed += 1
            else:
                failed += 1

    return {
        "total_graded": passed + failed,
        "passed": passed,
        "failed": failed
    }

# Student grade distribution
@router.get(
    "/grade-distribution",
    response_model=list[StudentGradeDistributionResponse]
)
def get_student_grade_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student)
):

    student = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    submissions = db.query(Submission).filter(
        Submission.student_id == student.id
    ).all()

    distribution = {
        "90-100": 0,
        "80-89": 0,
        "70-79": 0,
        "60-69": 0,
        "50-59": 0,
        "0-49": 0
    }

    for submission in submissions:

        grade = db.query(Grade).filter(
            Grade.submission_id == submission.id
        ).first()

        if grade:

            if grade.grade_value >= 90:
                distribution["90-100"] += 1

            elif grade.grade_value >= 80:
                distribution["80-89"] += 1

            elif grade.grade_value >= 70:
                distribution["70-79"] += 1

            elif grade.grade_value >= 60:
                distribution["60-69"] += 1

            elif grade.grade_value >= 50:
                distribution["50-59"] += 1

            else:
                distribution["0-49"] += 1

    results = []

    for grade_range, count in distribution.items():

        results.append(
            {
                "grade_range": grade_range,
                "assignment_count": count
            }
        )

    return results


# Student progress report
@router.get(
    "/progress-report",
    response_model=StudentProgressReportResponse
)
def get_progress_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student)
):

    student = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    submissions = db.query(Submission).filter(
        Submission.student_id == student.id
    ).all()

    grades = []
    passed = 0
    failed = 0

    for submission in submissions:

        grade = db.query(Grade).filter(
            Grade.submission_id == submission.id
        ).first()

        if grade:

            grades.append(grade.grade_value)

            if grade.grade_value >= 50:
                passed += 1
            else:
                failed += 1

    average_grade = 0.0

    if grades:
        average_grade = sum(grades) / len(grades)

    return {
        "student_id": student.id,
        "average_grade": average_grade,
        "total_graded": len(grades),
        "passed": passed,
        "failed": failed
    }


# Student ranking
@router.get(
    "/ranking",
    response_model=StudentRankingResponse
)
def get_student_ranking(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student)
):

    student = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    students = db.query(Student).all()

    rankings = []

    for current_student in students:

        submissions = db.query(Submission).filter(
            Submission.student_id == current_student.id
        ).all()

        grades = []

        for submission in submissions:

            grade = db.query(Grade).filter(
                Grade.submission_id == submission.id
            ).first()

            if grade:
                grades.append(grade.grade_value)

        average_grade = 0.0

        if grades:
            average_grade = sum(grades) / len(grades)

        rankings.append(
            {
                "student_id": current_student.id,
                "average_grade": average_grade
            }
        )

    rankings.sort(
        key=lambda student: student["average_grade"],
        reverse=True
    )

    rank_position = 0

    for index, ranking in enumerate(rankings, start=1):

        if ranking["student_id"] == student.id:
            rank_position = index
            break

    student_result = next(
        item for item in rankings
        if item["student_id"] == student.id
    )

    return {
        "student_id": student.id,
        "average_grade": student_result["average_grade"],
        "rank": rank_position
    }


# View announcements available to student [phase 7.2]
@router.get(
    "/announcements",
    response_model=list[StudentAnnouncementResponse]
)
def get_student_announcements(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student)
):

    student = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == student.id
    ).all()

    results = []

    for enrollment in enrollments:

        announcements = db.query(Announcement).filter(
            Announcement.course_id == enrollment.course_id
        ).all()

        results.extend(announcements)

    return results

# View announcements for a specific enrolled course
@router.get(
    "/courses/{course_id}/announcements",
    response_model=list[StudentCourseAnnouncementResponse]
)
def get_course_announcements(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student)
):

    student = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == student.id,   # Enrolled student with id.
        Enrollment.course_id == course_id
    ).first()

    if not enrollment:
        raise HTTPException(
            status_code=403,
            detail="Not enrolled in this course"
        )

    announcements = db.query(Announcement).filter(
        Announcement.course_id == course_id
    ).all()

    return announcements


# Unread announcements
@router.get(
    "/unread-announcements",
    response_model=list[UnreadAnnouncementResponse]
)
def get_unread_announcements(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student)
):

    student = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == student.id
    ).all()

    unread_announcements = []

    for enrollment in enrollments:

        announcements = db.query(Announcement).filter(
            Announcement.course_id == enrollment.course_id
        ).all()

        for announcement in announcements:

            already_read = db.query(AnnouncementRead).filter(
                AnnouncementRead.student_id == student.id,
                AnnouncementRead.announcement_id == announcement.id
            ).first()

            if not already_read:
                unread_announcements.append(announcement)

    return unread_announcements


# Mark announcement as read
@router.post(
    "/announcements/{announcement_id}/read",
    response_model=AnnouncementReadResponse
)
def mark_announcement_as_read(
    announcement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student)
):

    student = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    announcement = db.query(Announcement).filter(
        Announcement.id == announcement_id
    ).first()

    if not announcement:
        raise HTTPException(
            status_code=404,
            detail="Announcement not found"
        )

    existing = db.query(AnnouncementRead).filter(
        AnnouncementRead.student_id == student.id,
        AnnouncementRead.announcement_id == announcement_id
    ).first()

    if existing:
        return existing

    read_record = AnnouncementRead(
        student_id=student.id,
        announcement_id=announcement_id
    )

    db.add(read_record)
    db.commit()
    db.refresh(read_record)

    return read_record


# Announcement history (read announcements)
@router.get(
    "/announcement-history",
    response_model=list[AnnouncementHistoryResponse]
)
def get_announcement_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student)
):

    student = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    read_records = db.query(AnnouncementRead).filter(
        AnnouncementRead.student_id == student.id
    ).all()

    results = []

    for record in read_records:

        announcement = db.query(Announcement).filter(
            Announcement.id == record.announcement_id
        ).first()

        if announcement:
            results.append(announcement)

    return results


# Assignment notifications
@router.post(
    "/assignment-notifications",
    response_model=list[AssignmentNotificationResponse]
)
def create_assignment_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student)
):

    student = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == student.id
    ).all()

    created_notifications = []

    for enrollment in enrollments:

        assignments = db.query(Assignment).filter(
            Assignment.course_id == enrollment.course_id
        ).all()

        for assignment in assignments:

            notification = Notification(
                student_id=student.id,
                message=f"New assignment available: {assignment.title}"
            )

            db.add(notification)
            created_notifications.append(notification)

    db.commit()

    for notification in created_notifications:
        db.refresh(notification)

    return created_notifications


# Grade notifications
@router.post(
    "/grade-notifications",
    response_model=list[GradeNotificationResponse]
)
def create_grade_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student)
):

    student = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    submissions = db.query(Submission).filter(
        Submission.student_id == student.id
    ).all()

    created_notifications = []

    for submission in submissions:

        grades = db.query(Grade).filter(
            Grade.submission_id == submission.id
        ).all()

        for grade in grades:

            notification = Notification(
                student_id=student.id,
                message=f"Assignment graded: {grade.grade_value}"
            )

            db.add(notification)
            created_notifications.append(notification)

    db.commit()

    for notification in created_notifications:
        db.refresh(notification)

    return created_notifications


# Announcement notifications
@router.post(
    "/announcement-notifications",
    response_model=list[AnnouncementNotificationResponse]
)
def create_announcement_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student)
):

    student = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == student.id
    ).all()

    created_notifications = []

    for enrollment in enrollments:

        announcements = db.query(Announcement).filter(
            Announcement.course_id == enrollment.course_id
        ).all()

        for announcement in announcements:

            notification = Notification(
                student_id=student.id,
                message=f"New announcement: {announcement.title}"
            )

            db.add(notification)
            created_notifications.append(notification)

    db.commit()

    for notification in created_notifications:
        db.refresh(notification)

    return created_notifications


# Notification dashboard
@router.get(
    "/notifications",
    response_model=list[NotificationDashboardResponse]
)
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student)
):

    student = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    notifications = db.query(Notification).filter(
        Notification.student_id == student.id
    ).order_by(
        Notification.id.desc()        # Sort by Notification ID in descending order [desc=descending]
    ).all()

    return notifications


# Mark notification as read
@router.put(
    "/notifications/{notification_id}/read",
    response_model=NotificationReadResponse
)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student)
):

    student = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.student_id == student.id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    notification.is_read = True

    db.commit()
    db.refresh(notification)

    return notification

# Student attendance history
@router.get(
    "/attendance-history",
    response_model=list[AttendanceHistoryResponse]
)
def get_attendance_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student)
):

    student = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    attendance_records = (
        db.query(Attendance)
        .filter(
            Attendance.student_id == student.id
        )
        .order_by(
            Attendance.attendance_date.desc()
        )
        .all()
    )

    return attendance_records

# Student attendance statistics
@router.get(
    "/attendance-statistics",
    response_model=AttendanceStatisticsResponse
)
def get_attendance_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student)
):

    student = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    attendance_records = (
        db.query(Attendance)
        .filter(
            Attendance.student_id == student.id
        )
        .all()
    )

    total_records = len(attendance_records)

    present_count = sum(
        1
        for record in attendance_records
        if record.status.lower() == "present"
    )

    absent_count = sum(
        1
        for record in attendance_records
        if record.status.lower() == "absent"
    )

    late_count = sum(
        1
        for record in attendance_records
        if record.status.lower() == "late"
    )

    attendance_percentage = 0.0

    if total_records > 0:
        attendance_percentage = (
            present_count / total_records
        ) * 100

    return {
        "total_records": total_records,
        "present": present_count,
        "absent": absent_count,
        "late": late_count,
        "attendance_percentage": round(
            attendance_percentage,
            2
        )
    }

# Student attendance analytics
@router.get(
    "/attendance-analytics",
    response_model=AttendanceAnalyticsResponse
)
def get_attendance_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student)
):

    student = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    attendance_records = (
        db.query(Attendance)
        .filter(
            Attendance.student_id == student.id
        )
        .all()
    )

    total_records = len(attendance_records)

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

    if attendance_percentage >= 90:
        rating = "Excellent"
        risk = "Low"

    elif attendance_percentage >= 75:
        rating = "Good"
        risk = "Moderate"

    elif attendance_percentage >= 50:
        rating = "Poor"
        risk = "High"

    else:
        rating = "Critical"
        risk = "Very High"

    return {
        "attendance_percentage": round(
            attendance_percentage,
            2
        ),
        "attendance_rating": rating,
        "risk_level": risk
    }

# Student attendance risk alerts
@router.get(
    "/attendance-alerts",
    response_model=AttendanceAlertResponse
)
def get_attendance_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student)
):

    student = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    attendance_records = (
        db.query(Attendance)
        .filter(
            Attendance.student_id == student.id
        )
        .all()
    )

    total_records = len(attendance_records)

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

    if attendance_percentage >= 90:
        return {
            "at_risk": False,
            "risk_level": "Low",
            "message": "Attendance is satisfactory."
        }

    elif attendance_percentage >= 75:
        return {
            "at_risk": False,
            "risk_level": "Moderate",
            "message": "Attendance should be monitored."
        }

    else:
        return {
            "at_risk": True,
            "risk_level": "High",
            "message": "Attendance intervention recommended."
        }