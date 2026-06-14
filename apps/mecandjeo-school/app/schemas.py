# Validation schemas for authentication and school-domain entities

from pydantic import BaseModel, EmailStr
from typing import Optional


# ==========================================================
# USER AUTHENTICATION SCHEMAS (All user-related schemas, including registration, login, and API responses)
# ==========================================================

# Shared user fields 
class UserBase(BaseModel):
    email: EmailStr


# User registration
class UserCreate(UserBase):
    password: str


# User login
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# User API response
class UserResponse(UserBase):
    id: int
    role: str

    class Config:
        from_attributes = True


# ==========================================================
# STUDENT DOMAIN SCHEMAS
# ==========================================================

# Shared student fields
class StudentBase(BaseModel):
    grade: str
    full_name: Optional[str] = None


# Create student profile
class StudentCreate(StudentBase):
    pass


# Update student profile
class StudentUpdate(StudentBase):
    pass


# Student API response
class StudentResponse(StudentBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True



# ==========================================================
# TEACHER DOMAIN SCHEMAS
# ==========================================================

# Shared teacher fields
class TeacherBase(BaseModel):
    full_name: str
    subject: str


# Create teacher profile
class TeacherCreate(TeacherBase):
    pass


# Update teacher profile
class TeacherUpdate(TeacherBase):
    pass


# Teacher API response
class TeacherResponse(TeacherBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True



# ==========================================================
# COURSE DOMAIN SCHEMAS (Phase 5.2 Step 4)
# ==========================================================

# Shared course fields
class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None


# Create course
class CourseCreate(CourseBase):
    pass


# Update course
class CourseUpdate(CourseBase):
    pass


# Course API response
class CourseResponse(CourseBase):
    id: int
    teacher_id: int

    class Config:
        from_attributes = True


# ==========================================================
# ENROLLMENT DOMAIN SCHEMAS (Phase 5.2 Step 5)
# ==========================================================

# Shared enrollment fields
class EnrollmentBase(BaseModel):
    course_id: int


# Student enrollment request
class EnrollmentCreate(EnrollmentBase):
    pass


# Enrollment API response
class EnrollmentResponse(BaseModel):
    id: int
    student_id: int
    course_id: int

    class Config:
        from_attributes = True


# ==========================================================
# ASSIGNMENT DOMAIN SCHEMAS (Phase 5.2 Step 6)
# ==========================================================

# Shared assignment fields
class AssignmentBase(BaseModel):
    title: str
    description: Optional[str] = None


# Create assignment
class AssignmentCreate(AssignmentBase):
    pass


# Update assignment
class AssignmentUpdate(AssignmentBase):
    pass


# Assignment API response [Used when returning assignment data to clients]
class AssignmentResponse(AssignmentBase):
    id: int
    course_id: int

    class Config:
        from_attributes = True


# ==========================================================
# SUBMISSION DOMAIN SCHEMAS (Phase 5.2 Step 7)
# ==========================================================

# Shared submission fields
class SubmissionBase(BaseModel):
    content: str                  # Student's answer or work for the assignment, could be text, a link to a file, etc.


# Create submission
class SubmissionCreate(SubmissionBase):
    assignment_id: int                 # Student must specify which assignment they are submitting for among the ones created by teachers


# Update submission
class SubmissionUpdate(SubmissionBase):
    pass


# Submission API response
class SubmissionResponse(SubmissionBase):
    id: int
    student_id: int
    assignment_id: int

    class Config:
        from_attributes = True


# ==========================================================
# GRADE DOMAIN SCHEMAS (Phase 5.2 Step 8)
# ==========================================================

# Shared grade fields [Stores the actual grade value and optional feedback from the teacher]
class GradeBase(BaseModel):
    grade_value: int
    feedback: Optional[str] = None


# Create grade [Teacher must specify which submission they are grading among the ones submitted by students]
class GradeCreate(GradeBase):
    submission_id: int


# Update grade [Teacher can update the grade and feedback for a submission if needed]
class GradeUpdate(GradeBase):
    pass


# Grade API response
class GradeResponse(GradeBase):
    id: int
    submission_id: int       # Submission that this grade is associated with

    class Config:
        from_attributes = True


# Student grade view response  [Step 9]
class StudentGradeResponse(BaseModel):
    submission_id: int
    assignment_id: int     # To allow students to see which assignment the grade is for, we include the assignment_id in the response
    grade_value: int
    feedback: Optional[str] = None

    class Config:
        from_attributes = True

# ==========================================================
# TEACHER DASHBOARD SCHEMAS (Phase 6.1 Step 1) 
# ==========================================================
# Summarized information for teachers to see an overview of their courses, 
# assignments, submissions, and grades]

class TeacherDashboardResponse(BaseModel):
    total_courses: int
    total_assignments: int
    total_submissions: int
    total_grades: int

# ==========================================================
# COURSE ROSTER SCHEMAS (Phase 6.1 Step 2)
# ==========================================================

class CourseRosterResponse(BaseModel):      # Provides a list of students enrolled in a specific course.
    student_id: int

    class Config:
        from_attributes = True

# ==========================================================
# ASSIGNMENT SUBMISSION TRACKING SCHEMAS
# (Phase 6.1 Step 3)
# ==========================================================

class AssignmentSubmissionResponse(BaseModel):
    submission_id: int
    student_id: int

    class Config:
        from_attributes = True

# ==========================================================
# GRADING STATUS SCHEMAS
# (Phase 6.1 Step 4)
# ==========================================================

class GradingStatusResponse(BaseModel):
    submission_id: int
    student_id: int
    graded: bool       # Uses two possible values: "graded" or "not graded", "true or false" to indicate whether a submission has been graded by the teacher or not.

    class Config:
        from_attributes = True

# ==========================================================
# ASSIGNMENT PERFORMANCE SCHEMAS [This step answers the question: "How did my students perform on this assignment?"]
# (Phase 6.1 Step 5)
# ==========================================================

class AssignmentPerformanceResponse(BaseModel):
    student_id: int
    grade_value: int
    feedback: Optional[str] = None

    class Config:
        from_attributes = True

# ==========================================================
# COURSE PERFORMANCE SCHEMAS  [This step answers the question: "How did my students perform in this course overall?"]
# (Phase 6.1 Step 6)
# ==========================================================

class CoursePerformanceResponse(BaseModel):
    course_id: int
    average_grade: float   # The average_grade should be a decimal or expected to contain a decimal number e.g., 85.5

    class Config:
        from_attributes = True

# ==========================================================
# STUDENT PERFORMANCE SCHEMAS
# (Phase 6.1 Step 7)  [This step answers the question: "How am I performing as a student?"]
# ==========================================================

class StudentPerformanceResponse(BaseModel):
    student_id: int
    average_grade: float  # The average_grade should be a decimal or expected to contain a decimal number e.g., 88.2 to represent the average grade for the student across all their graded submissions.

    class Config:
        from_attributes = True

# ==========================================================
# TOP STUDENTS SCHEMAS
# (Phase 6.1 Step 8) [This step answers the question: "Who are the top-performing students in my course?"]
# ==========================================================

class TopStudentResponse(BaseModel):
    student_id: int
    average_grade: float

    class Config:
        from_attributes = True

# ==========================================================
# PASS / FAIL STATISTICS SCHEMAS
# (Phase 6.1 Step 9)
# ==========================================================

class PassFailStatisticsResponse(BaseModel):
    total_graded: int
    passed: int
    failed: int

    class Config:
        from_attributes = True

# ==========================================================
# GRADE DISTRIBUTION SCHEMAS
# (Phase 6.1 Step 10)
# ==========================================================

class GradeDistributionResponse(BaseModel):
    grade_range: str
    student_count: int

    class Config:
        from_attributes = True



# ==========================================================
# STUDENT DASHBOARD SCHEMAS
# (Phase 6.2 Step 1)
# ==========================================================

class StudentDashboardResponse(BaseModel):
    total_courses: int        # Number of courses the student is enrolled in.
    total_assignments: int
    total_submissions: int
    total_grades: int

    class Config:
        from_attributes = True


# ==========================================================
# MY COURSES SCHEMAS
# (Phase 6.2 Step 2)
# ==========================================================

class MyCourseResponse(BaseModel):
    course_id: int
    title: str

    class Config:
        from_attributes = True

# ==========================================================
# MY ASSIGNMENTS SCHEMAS
# (Phase 6.2 Step 3)
# ==========================================================

class MyAssignmentResponse(BaseModel):
    assignment_id: int
    title: str

    class Config:
        from_attributes = True

# ==========================================================
# ASSIGNMENT SUBMISSION STATUS SCHEMAS
# (Phase 6.2 Step 4)
# ==========================================================

class AssignmentSubmissionStatusResponse(BaseModel):
    assignment_id: int
    title: str
    submitted: bool

    class Config:
        from_attributes = True


# ==========================================================
# GRADE HISTORY SCHEMAS
# (Phase 6.2 Step 5)
# ==========================================================

class GradeHistoryResponse(BaseModel):
    assignment_id: int
    grade_value: int
    feedback: Optional[str] = None

    class Config:
        from_attributes = True


# ==========================================================
# STUDENT PERFORMANCE ANALYTICS SCHEMAS
# (Phase 6.2 Step 6)
# ==========================================================

class StudentAnalyticsResponse(BaseModel):
    student_id: int
    average_grade: float

    class Config:
        from_attributes = True


# ==========================================================
# STUDENT PASS / FAIL STATISTICS SCHEMAS
# (Phase 6.2 Step 7)
# ==========================================================

class StudentPassFailResponse(BaseModel):
    total_graded: int
    passed: int
    failed: int

    class Config:
        from_attributes = True


# ==========================================================
# STUDENT GRADE DISTRIBUTION SCHEMAS
# (Phase 6.2 Step 8)
# ==========================================================

class StudentGradeDistributionResponse(BaseModel):
    grade_range: str
    assignment_count: int

    class Config:
        from_attributes = True


# ==========================================================
# STUDENT PROGRESS REPORT SCHEMAS
# (Phase 6.2 Step 9)
# ==========================================================

class StudentProgressReportResponse(BaseModel):
    student_id: int
    average_grade: float
    total_graded: int
    passed: int
    failed: int

    class Config:
        from_attributes = True



#########################################################################################################

## Starting Point for Schemas.
# # validation schemas for user registration and login, ensuring data integrity and security best practices.
# from pydantic import BaseModel, EmailStr
# from typing import Optional


# # Base shared user fields
# class UserBase(BaseModel):
#     email: EmailStr                    # validate proper email format
#     grade: Optional[str] = None


# # Schema for creating new users
# class UserCreate(UserBase):
#     password: str


# # Schema for login requests
# class UserLogin(BaseModel):
#     email: EmailStr
#     password: str


# # Schema returned from API responses
# class UserResponse(UserBase):        # Password is intentionally excluded from response schema
#     id: int
#     role: str

#     class Config:
#         from_attributes = True  # allows Pydantic to read data from ORM models directly, enabling seamless integration with SQLAlchemy models.
