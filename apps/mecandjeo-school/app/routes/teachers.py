# Teacher profile management

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    Teacher,
    Course,   # course, assignment, submission, grade models are imported for phase 6.1 step 1. Records are counted from these tables to display stats on the teacher dashboard
    Assignment,
    Submission,
    Grade,
    Enrollment,  # Enrollment model is imported for phase 6.1 step 2 to query the students enrolled in a specific course for the course roster endpoint.
    Student,     # Student model is imported for phase 6.1 step 2 to query the students enrolled in a specific course for the course roster endpoint.
    User,
    Announcement,
    Attendance
)
from ..schemas import (     # imports from schemas.py [all teacher-related schemas are imported for teacher profile management endpoints.]
    TeacherCreate,
    TeacherUpdate,
    TeacherResponse,
    TeacherDashboardResponse,
    CourseRosterResponse,
    AssignmentSubmissionResponse,
    GradingStatusResponse,
    AssignmentPerformanceResponse,
    CoursePerformanceResponse,
    StudentPerformanceResponse,
    TopStudentResponse,
    PassFailStatisticsResponse,
    GradeDistributionResponse,
    AnnouncementCreate,
    AnnouncementResponse,
    MyAnnouncementResponse,
    AnnouncementUpdate,
    CourseAnnouncementResponse,
    CourseSummaryResponse,
    CourseGradeDistributionResponse,
    AtRiskStudentResponse,
    AttendanceCreate,
    AttendanceResponse,
    TeacherPerformanceDashboardResponse
)
from ..auth import (     # From auth.py
    get_current_user,
    require_teacher
) 

router = APIRouter(
    prefix="/teachers",
    tags=["Teachers"]
)

# # Verify teacher role
# def require_teacher(
#     current_user: User = Depends(get_current_user)
# ):

#     if current_user.role != "teacher":
#         raise HTTPException(
#             status_code=403,
#             detail="Teacher access required"
#         )

#     return current_user


# Create teacher profile
@router.post("/", response_model=TeacherResponse)
def create_teacher_profile(
    teacher: TeacherCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)  # current_user: User = Depends(get_current_user) (Protect teacher creation)
):

    # Prevent duplicate teacher profiles
    existing_profile = db.query(Teacher).filter(
        Teacher.user_id == current_user.id
    ).first()

    if existing_profile:
        raise HTTPException(
            status_code=400,
            detail="Teacher profile already exists"
        )

    profile = Teacher(
        user_id=current_user.id,
        full_name=teacher.full_name,
        subject=teacher.subject
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return profile

# Get current teacher profile
@router.get("/me", response_model=TeacherResponse)
def get_my_teacher_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    profile = db.query(Teacher).filter(
        Teacher.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found"
        )

    return profile

# Update current teacher profile
@router.put("/me", response_model=TeacherResponse)
def update_my_teacher_profile(
    teacher: TeacherUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    profile = db.query(Teacher).filter(
        Teacher.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found"
        )

    profile.full_name = teacher.full_name
    profile.subject = teacher.subject

    db.commit()               # commit or save changes to the database
    db.refresh(profile)       # return the updated profile from the database

    return profile


# Teacher dashboard [phase 6.1 step 2: This endpoint provides a dashboard for teachers, showing statistics about their courses, assignments, submissions, and grades. It queries the database to count the relevant records and returns them in a structured response defined by TeacherDashboardResponse schema.]
@router.get(
    "/dashboard",
    response_model=TeacherDashboardResponse
)
def teacher_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):

    teacher = db.query(Teacher).filter(
        Teacher.user_id == current_user.id
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found"
        )

    # Count teacher courses
    total_courses = db.query(Course).filter(
        Course.teacher_id == teacher.id
    ).count()

    # Count assignments belonging to teacher's courses
    total_assignments = db.query(Assignment).join(
        Course
    ).filter(
        Course.teacher_id == teacher.id
    ).count()

    # Count submissions for teacher assignments
    total_submissions = db.query(Submission).join(
        Assignment
    ).join(
        Course
    ).filter(
        Course.teacher_id == teacher.id
    ).count()

    # Count grades for teacher submissions
    total_grades = db.query(Grade).join(      # "join" means connect related tables together based on their relationships.
        Submission
    ).join(
        Assignment
    ).join(
        Course
    ).filter(
        Course.teacher_id == teacher.id
    ).count()

    return {
        "total_courses": total_courses,
        "total_assignments": total_assignments,
        "total_submissions": total_submissions,
        "total_grades": total_grades
    }


# Course roster [Phase 6.1 step 2: This endpoint allows teachers to view the roster of students enrolled in a specific course. It validates that the teacher owns the course and then queries the Enrollment table to retrieve the list of student IDs enrolled in that course, returning the data structured according to the CourseRosterResponse schema.]
@router.get(
    "/course-roster",
    response_model=list[CourseRosterResponse]
)
def get_course_roster(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):

    teacher = db.query(Teacher).filter(
        Teacher.user_id == current_user.id
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found"
        )

    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    # Ownership validation
    if course.teacher_id != teacher.id: # Ownership validation is performed by comparing the teacher_id of the course with the id of the currently authenticated teacher. If they do not match, it means the teacher does not own the course.
        raise HTTPException(
            status_code=403,
            detail="You do not own this course"
        )

    enrollments = db.query(Enrollment).filter(  # Query the Enrollment table to get all enrollments for the specified course_id.
        Enrollment.course_id == course_id
    ).all()

    roster = []

    for enrollment in enrollments:

        roster.append(
            {
                "student_id": enrollment.student_id
            }
        )

    return roster


# Assignment submission tracking [Phase 6.1 step 3: This endpoint allows teachers to track which students have submitted a particular assignment. It queries the Submission table for the specified assignment_id and returns a list of submissions along with the associated student IDs, structured according to the AssignmentSubmissionResponse schema.]
@router.get(
    "/assignment-submissions",
    response_model=list[AssignmentSubmissionResponse]
)
def get_assignment_submissions(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):

    teacher = db.query(Teacher).filter(
        Teacher.user_id == current_user.id
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found"
        )

    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=404,
            detail="Assignment not found"
        )

    course = db.query(Course).filter(
        Course.id == assignment.course_id
    ).first()

    # Ownership validation
    if course.teacher_id != teacher.id:
        raise HTTPException(
            status_code=403,
            detail="You do not own this assignment"
        )

    submissions = db.query(Submission).filter(
        Submission.assignment_id == assignment_id
    ).all()

    results = []

    for submission in submissions:

        results.append(
            {
                "submission_id": submission.id,
                "student_id": submission.student_id
            }
        )

    return results

# Grading workflow monitoring [Phase 6.1 step 4: This endpoint allows teachers to monitor the grading workflow for a specific assignment. It retrieves all submissions for the given assignment_id and checks if each submission has an associated grade. The response indicates whether each submission has been graded or not, structured according to the GradingStatusResponse schema.]
@router.get(
    "/grading-status",
    response_model=list[GradingStatusResponse]
)
def get_grading_status(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):

    teacher = db.query(Teacher).filter(
        Teacher.user_id == current_user.id
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found"
        )

    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=404,
            detail="Assignment not found"
        )

    course = db.query(Course).filter(
        Course.id == assignment.course_id
    ).first()

    # Ownership validation
    if course.teacher_id != teacher.id:
        raise HTTPException(
            status_code=403,
            detail="You do not own this assignment"
        )

    submissions = db.query(Submission).filter(
        Submission.assignment_id == assignment_id
    ).all()

    results = []

    for submission in submissions:

        grade = db.query(Grade).filter(
            Grade.submission_id == submission.id
        ).first()

        results.append(
            {
                "submission_id": submission.id,
                "student_id": submission.student_id,
                "graded": grade is not None
            }
        )

    return results


# Assignment performance view [Phase 6.1 step 5: This endpoint provides a performance view for a specific assignment, showing the grades and feedback for each student submission. It retrieves all submissions for the given assignment_id, checks for associated grades, and returns the student ID, grade value, and feedback in a structured response defined by the AssignmentPerformanceResponse schema. Only graded submissions are included in the performance view; if a submission does not have an associated grade, it is skipped and not included in the results.]
@router.get(
    "/assignment-performance",
    response_model=list[AssignmentPerformanceResponse]
)
def get_assignment_performance(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):

    teacher = db.query(Teacher).filter(
        Teacher.user_id == current_user.id
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found"
        )

    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=404,
            detail="Assignment not found"
        )

    course = db.query(Course).filter(
        Course.id == assignment.course_id
    ).first()

    # Ownership validation
    if course.teacher_id != teacher.id:
        raise HTTPException(
            status_code=403,
            detail="You do not own this assignment"
        )

    submissions = db.query(Submission).filter(
        Submission.assignment_id == assignment_id
    ).all()

    results = []

    for submission in submissions:

        grade = db.query(Grade).filter(
            Grade.submission_id == submission.id
        ).first()

        if grade:           # Only graded submissions are included in the performance view. If a submission does not have an associated grade, it is skipped and not included in the results.

            results.append(
                {
                    "student_id": submission.student_id,
                    "grade_value": grade.grade_value,
                    "feedback": grade.feedback
                }
            )

    return results


# Course performance analytics [Phase 6.1 step 6: This endpoint provides analytics on overall course performance by calculating the average grade for a specific course. It retrieves all assignments for the course, then all submissions for those assignments, and finally all grades for those submissions. The average grade is calculated and returned in a structured response defined by the CoursePerformanceResponse schema.]
@router.get(
    "/course-performance",
    response_model=CoursePerformanceResponse
)
def get_course_performance(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):

    teacher = db.query(Teacher).filter(
        Teacher.user_id == current_user.id
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found"
        )

    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    # Ownership validation 
    if course.teacher_id != teacher.id:
        raise HTTPException(
            status_code=403,
            detail="You do not own this course"
        )

    assignments = db.query(Assignment).filter(
        Assignment.course_id == course_id
    ).all()

    grades = []   # aggregate all grade values for the course to calculate the average grade. 
    for assignment in assignments:

        submissions = db.query(Submission).filter(
            Submission.assignment_id == assignment.id
        ).all()

        for submission in submissions:

            grade = db.query(Grade).filter(
                Grade.submission_id == submission.id
            ).first()

            if grade:      # Only graded submissions are included in the performance view. If a submission does not have an associated grade, it is skipped and not included in the results.
                grades.append(grade.grade_value)  # Collect [append] all grade values for the course to calculate the average grade.

    average_grade = 0.0  # Initialize average_grade to 0.0 to handle the case where there are no grades. If there are no grades, the average will be returned as 0.0 instead of causing a division by zero error.

    if grades:
        average_grade = sum(grades) / len(grades) # len [length] = How many grades are inside this collection? 

    return {
        "course_id": course_id,
        "average_grade": average_grade
    }


# Student performance analytics [Phase 6.1 step 7: This endpoint provides analytics on individual student performance by calculating the average grade for a specific student across all their submissions. It retrieves all submissions for the student, then all grades for those submissions, and calculates the average grade, which is returned in a structured response defined by the StudentPerformanceResponse schema.]
@router.get(
    "/student-performance",
    response_model=StudentPerformanceResponse
)
def get_student_performance(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):

    teacher = db.query(Teacher).filter(
        Teacher.user_id == current_user.id
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found"
        )

    student = db.query(Student).filter(
        Student.id == student_id
    ).first() # Validate that the student exists. If the student does not exist, a 404 error is raised indicating that the student was not found. 

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    submissions = db.query(Submission).filter(
        Submission.student_id == student_id
    ).all()  # Retrieve all submissions belonging to the specified student id.

    grades = []

    for submission in submissions:

        grade = db.query(Grade).filter(
            Grade.submission_id == submission.id
        ).first()

        if grade:
            grades.append(grade.grade_value)

    average_grade = 0.0   # Empty grade protection or handling the case where there are no grades for the student. If there are no grades, the average will be returned as 0.0 instead of causing a division by zero error.

    if grades:
        average_grade = sum(grades) / len(grades)

    return {
        "student_id": student_id,
        "average_grade": average_grade
    }


# Top performing  students [Phase 6.1 step 8: This endpoint provides a list of top-performing students based on their average grades across all submissions.
@router.get(
    "/top-students",
    response_model=list[TopStudentResponse]
)
def get_top_students(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    # Teacher validation
    teacher = db.query(Teacher).filter(
        Teacher.user_id == current_user.id
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found"
        )

    students = db.query(Student).all()    # Load every student

    results = []

    for student in students:

        submissions = db.query(Submission).filter(
            Submission.student_id == student.id
        ).all()  # Retrieve all submission belonging to specific student id.

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

            results.append(
                {
                    "student_id": student.id,
                    "average_grade": average_grade
                }
            )

    # Sort highest first
    results.sort(
        key=lambda student: student["average_grade"], # = Rank students by average_grade [Highest performer first].
        reverse=True   # Highest performer first.
    )

    return results


# Pass / Fail statistics
@router.get(
    "/pass-fail-statistics",
    response_model=PassFailStatisticsResponse
)
def get_pass_fail_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):

    teacher = db.query(Teacher).filter(
        Teacher.user_id == current_user.id
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found"
        )

    grades = db.query(Grade).all()

    passed = 0
    failed = 0

    for grade in grades: # Process one grade at a time from the collection of grades.

        if grade.grade_value >= 50:
            passed += 1         # +=1 is the short hand for passed = passed + 1
        else:
            failed += 1

    return {
        "total_graded": len(grades),
        "passed": passed,
        "failed": failed
    }

# Grade distribution report
@router.get(
    "/grade-distribution",
    response_model=list[GradeDistributionResponse]
)
def get_grade_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):

    teacher = db.query(Teacher).filter(
        Teacher.user_id == current_user.id
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found"
        )

    grades = db.query(Grade).all()

    distribution = {         # Bucket structure
        "90-100": 0,
        "80-89": 0,
        "70-79": 0,
        "60-69": 0,
        "50-59": 0,
        "0-49": 0
    }

    for grade in grades:

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
                "student_count": count
            }
        )

    return results


# Create announcement
@router.post(
    "/announcements",
    response_model=AnnouncementResponse
)
def create_announcement(
    announcement: AnnouncementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):

    teacher = db.query(Teacher).filter(
        Teacher.user_id == current_user.id
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found"
        )

    course = db.query(Course).filter(
        Course.id == announcement.course_id,
        Course.teacher_id == teacher.id
    ).first()

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    new_announcement = Announcement(
        teacher_id=teacher.id,
        course_id=announcement.course_id,
        title=announcement.title,
        message=announcement.message
    )

    db.add(new_announcement)
    db.commit()
    db.refresh(new_announcement)

    return new_announcement


# View my announcements
@router.get(
    "/announcements",
    response_model=list[MyAnnouncementResponse]
)
def get_my_announcements(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):

    teacher = db.query(Teacher).filter(
        Teacher.user_id == current_user.id
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found"
        )

    announcements = db.query(Announcement).filter(
        Announcement.teacher_id == teacher.id
    ).all()

    return announcements


# Update announcement
@router.put(
    "/announcements/{announcement_id}",
    response_model=AnnouncementResponse
)
def update_announcement(
    announcement_id: int,
    announcement_data: AnnouncementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):

    teacher = db.query(Teacher).filter(
        Teacher.user_id == current_user.id
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found"
        )

    announcement = db.query(Announcement).filter(
        Announcement.id == announcement_id,
        Announcement.teacher_id == teacher.id
    ).first()

    if not announcement:
        raise HTTPException(
            status_code=404,
            detail="Announcement not found"
        )

    announcement.title = announcement_data.title
    announcement.message = announcement_data.message

    db.commit()
    db.refresh(announcement)

    return announcement


# Delete announcement
@router.delete(
    "/announcements/{announcement_id}"
)
def delete_announcement(
    announcement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):

    teacher = db.query(Teacher).filter(
        Teacher.user_id == current_user.id
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found"
        )

    announcement = db.query(Announcement).filter(
        Announcement.id == announcement_id,
        Announcement.teacher_id == teacher.id
    ).first()

    if not announcement:
        raise HTTPException(
            status_code=404,
            detail="Announcement not found"
        )

    db.delete(announcement)
    db.commit()

    return {
        "message": "Announcement deleted successfully"
    }


# Course announcements
@router.get(
    "/courses/{course_id}/announcements",
    response_model=list[CourseAnnouncementResponse]
)
def get_course_announcements(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):

    teacher = db.query(Teacher).filter(
        Teacher.user_id == current_user.id
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found"
        )

    course = db.query(Course).filter(
        Course.id == course_id,
        Course.teacher_id == teacher.id
    ).first()

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    announcements = db.query(Announcement).filter(
        Announcement.course_id == course_id
    ).all()

    return announcements


# Course summary report [phase 8.1c]
@router.get(
    "/courses/{course_id}/summary",
    response_model=CourseSummaryResponse
)
def get_course_summary(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):

    teacher = db.query(Teacher).filter(
        Teacher.user_id == current_user.id
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found"
        )

    course = db.query(Course).filter(
        Course.id == course_id,
        Course.teacher_id == teacher.id
    ).first()

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    total_students = db.query(Enrollment).filter(
        Enrollment.course_id == course.id
    ).count()

    total_assignments = db.query(Assignment).filter(
        Assignment.course_id == course.id
    ).count()

    assignment_ids = db.query(Assignment.id).filter(
        Assignment.course_id == course.id
    ).all()

    assignment_ids = [a[0] for a in assignment_ids]   # Give me the first item or Create a new list from an existing collection

    total_submissions = db.query(Submission).filter(
        Submission.assignment_id.in_(assignment_ids)
    ).count()

    grades = db.query(Grade).join(
        Submission
    ).filter(
        Submission.assignment_id.in_(assignment_ids)
    ).all()

    average_grade = 0.0

    if grades:       # "if grades list contains at least one item"
        average_grade = (
            sum(g.grade_value for g in grades)   # Produce values one at a time or Extract values from objects and calculate the total.
            / len(grades)
        )

    return {
        "course_id": course.id,
        "course_title": course.title,
        "average_grade": round(average_grade, 2),
        "total_students": total_students,
        "total_assignments": total_assignments,
        "total_submissions": total_submissions
    }


# Student performance report
@router.get(
    "/students/{student_id}/performance",
    response_model=StudentPerformanceResponse
)
def get_student_performance(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):

    teacher = db.query(Teacher).filter(
        Teacher.user_id == current_user.id
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found"
        )

    student = db.query(Student).filter(
        Student.id == student_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    submissions = db.query(Submission).filter(
        Submission.student_id == student.id
    ).all()

    total_submissions = len(submissions)

    assignments_completed = total_submissions

    grades = db.query(Grade).join(
        Submission
    ).filter(
        Submission.student_id == student.id
    ).all()

    average_grade = 0.0

    if grades:
        average_grade = (
            sum(g.grade_value for g in grades)
            / len(grades)
        )

    return {
        "student_id": student.id,
        "student_name": student.full_name,
        "average_grade": round(average_grade, 2),   # Keep 2 digits after the decimal point
        "assignments_completed": assignments_completed,
        "total_submissions": total_submissions
    }


# Course grade distribution
@router.get(
    "/courses/{course_id}/grade-distribution",
    response_model=list[CourseGradeDistributionResponse]
)
def get_course_grade_distribution(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):

    teacher = db.query(Teacher).filter(
        Teacher.user_id == current_user.id
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found"
        )

    course = db.query(Course).filter(
        Course.id == course_id,
        Course.teacher_id == teacher.id
    ).first()

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    assignment_ids = db.query(Assignment.id).filter(
        Assignment.course_id == course.id
    ).all()

    assignment_ids = [a[0] for a in assignment_ids]

    grades = db.query(Grade).join(
        Submission
    ).filter(
        Submission.assignment_id.in_(assignment_ids)
    ).all()

    distribution = {       # assumed that no student has this mark yet or counted. For grading purpose
        "90-100": 0,
        "80-89": 0,
        "70-79": 0,
        "60-69": 0,
        "50-59": 0,
        "0-49": 0
    }

    for grade in grades:   # Loop through every grade object one at a time.

        value = grade.grade_value    # Extract the actual numeric score from the Grade object

        if value >= 90:
            distribution["90-100"] += 1      # += 1 means Add a student if he has this score [1 represents number of student]; increment

        elif value >= 80:
            distribution["80-89"] += 1

        elif value >= 70:
            distribution["70-79"] += 1

        elif value >= 60:
            distribution["60-69"] += 1

        elif value >= 50:
            distribution["50-59"] += 1

        else:
            distribution["0-49"] += 1

    return [
        {
            "grade_range": grade_range,
            "student_count": count
        }
        for grade_range, count in distribution.items()
    ]


# Top performing students [phase 8.1 sttep 4]
@router.get(
    "/courses/{course_id}/top-students",
    response_model=list[TopStudentResponse]
)
def get_top_students(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):

    teacher = db.query(Teacher).filter(
        Teacher.user_id == current_user.id
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found"
        )

    course = db.query(Course).filter(
        Course.id == course_id,
        Course.teacher_id == teacher.id
    ).first()

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    enrollments = db.query(Enrollment).filter(
        Enrollment.course_id == course.id
    ).all()

    results = []

    for enrollment in enrollments:

        student = db.query(Student).filter(
            Student.id == enrollment.student_id
        ).first()

        grades = db.query(Grade).join(
            Submission
        ).filter(
            Submission.student_id == student.id
        ).all()

        average_grade = 0.0

        if grades:
            average_grade = (
                sum(g.grade_value for g in grades)
                / len(grades)
            )

        results.append(
            {
                "student_id": student.id,
                "student_name": student.full_name,
                "average_grade": round(
                    average_grade,
                    2
                )
            }
        )

    results.sort(
        key=lambda x: x["average_grade"],
        reverse=True
    )

    return results


# At-risk students [phase 8.1 step 5]
@router.get(
    "/courses/{course_id}/at-risk-students",
    response_model=list[AtRiskStudentResponse]
)
def get_at_risk_students(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):

    teacher = db.query(Teacher).filter(
        Teacher.user_id == current_user.id
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found"
        )

    course = db.query(Course).filter(
        Course.id == course_id,
        Course.teacher_id == teacher.id
    ).first()

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    enrollments = db.query(Enrollment).filter(
        Enrollment.course_id == course.id
    ).all()

    results = []

    for enrollment in enrollments:

        student = db.query(Student).filter(
            Student.id == enrollment.student_id
        ).first()

        grades = db.query(Grade).join(
            Submission
        ).filter(
            Submission.student_id == student.id
        ).all()

        if not grades:
            continue

        average_grade = (
            sum(g.grade_value for g in grades)
            / len(grades)
        )

        if average_grade < 50:

            results.append(
                {
                    "student_id": student.id,
                    "student_name": student.full_name,
                    "average_grade": round(
                        average_grade,
                        2
                    )
                }
            )

    return results

# Mark student attendance
@router.post(
    "/attendance",
    response_model=AttendanceResponse
)
def mark_attendance(
    attendance: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):

    teacher = db.query(Teacher).filter(
        Teacher.user_id == current_user.id
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found"
        )

    course = db.query(Course).filter(
        Course.id == attendance.course_id,
        Course.teacher_id == teacher.id
    ).first()

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    new_attendance = Attendance(
        student_id=attendance.student_id,
        course_id=attendance.course_id,
        attendance_date=attendance.attendance_date,
        status=attendance.status
    )

    db.add(new_attendance)
    db.commit()
    db.refresh(new_attendance)

    return new_attendance

# Teacher performance dashboard
@router.get(
    "/performance-dashboard",
    response_model=TeacherPerformanceDashboardResponse
)
def get_teacher_performance_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
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
            status_code=404,
            detail="Teacher profile not found"
        )

    courses = (
        db.query(Course)
        .filter(
            Course.teacher_id == teacher.id
        )
        .all()
    )

    course_ids = [course.id for course in courses]

    # -----------------------------------------
    # Average Grade
    # -----------------------------------------

    grades = (
        db.query(Grade)
        .join(
            Submission,
            Grade.submission_id == Submission.id
        )
        .join(
            Enrollment,
            Enrollment.student_id == Submission.student_id
        )
        .filter(
            Enrollment.course_id.in_(course_ids)
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

    # -----------------------------------------
    # Attendance
    # -----------------------------------------

    attendance_records = (
        db.query(Attendance)
        .filter(
            Attendance.course_id.in_(course_ids)
        )
        .all()
    )

    average_attendance = 0.0

    if attendance_records:

        present_count = sum(
            1
            for record in attendance_records
            if record.status.lower() == "present"
        )

        average_attendance = (
            present_count
            / len(attendance_records)
        ) * 100

    # -----------------------------------------
    # Risk Students
    # -----------------------------------------

    at_risk_students = 0

    student_ids = {
        enrollment.student_id
        for enrollment in (
            db.query(Enrollment)
            .filter(
                Enrollment.course_id.in_(course_ids)
            )
            .all()
        )
    }

    for student_id in student_ids:

        student_grades = (
            db.query(Grade)
            .join(
                Submission,
                Grade.submission_id == Submission.id
            )
            .filter(
                Submission.student_id == student_id
            )
            .all()
        )

        if not student_grades:
            continue

        avg_grade = (
            sum(
                grade.grade_value
                for grade in student_grades
            )
            / len(student_grades)
        )

        if avg_grade < 50:
            at_risk_students += 1

    return {
        "average_grade": round(
            average_grade,
            2
        ),
        "average_attendance": round(
            average_attendance,
            2
        ),
        "at_risk_students": at_risk_students
    }