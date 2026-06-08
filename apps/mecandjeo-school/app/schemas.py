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
