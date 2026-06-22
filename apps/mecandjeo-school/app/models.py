
# "back_populates" means: This relationship is connected to another relationship on the other model. It creates a two-way relationship.
# It allows you to navigate from one model to the other in both directions. 

# Database tables and ORM models
from datetime import datetime

from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    ForeignKey,
    Boolean,
    Date,
    DateTime
)
from sqlalchemy.orm import relationship

from .database import Base


# Authentication and authorization model
class User(Base):
    __tablename__ = "users"

    # Primary unique user ID
    id = Column(Integer, primary_key=True, index=True)

    # User email for authentication
    email = Column(String, unique=True, index=True, nullable=False)

    # Hashed password storage
    password = Column(String, nullable=False)

    # User role (student, teacher, admin)
    role = Column(String, default="student", nullable=False)

    # One-to-one relationship with student profile
    student_profile = relationship(
        "Student",
        back_populates="user",
        uselist=False
    )

    # One-to-one relationship with teacher profile
    teacher_profile = relationship(
        "Teacher",
        back_populates="user",
        uselist=False
    )


# Student domain model
class Student(Base):
    __tablename__ = "students"

    # Primary student ID
    id = Column(Integer, primary_key=True, index=True)

    # Link student to authenticated user. Foreign key= (connects tables together)
    user_id = Column(Integer, ForeignKey("users.id"))

    # Student academic grade
    grade = Column(String, nullable=False)

    # Optional student full name
    full_name = Column(String, nullable=True)

    # Relationship back to user
    user = relationship(
        "User",
        back_populates="student_profile"
    )

    # One student can have many enrollments (phase 5.2-step 5)
    enrollments = relationship(
        "Enrollment",
        back_populates="student"
    )

    # One student can have many submissions (Phase 5.2 Step 7)
    submissions = relationship(
        "Submission",
        back_populates="student"
    )


# Teacher domain model (phase 5.2-step 3) - to be expanded with course relationships in next step
class Teacher(Base):
    __tablename__ = "teachers"

    # Primary teacher ID
    id = Column(Integer, primary_key=True, index=True)

    # Link teacher to authenticated user
    user_id = Column(Integer, ForeignKey("users.id"))

    # Teacher full name
    full_name = Column(String, nullable=False)

    # Subject specialization
    subject = Column(String, nullable=False)

    # Relationship back to user
    user = relationship(
        "User",
        back_populates="teacher_profile"
    )

    # One teacher can teach many courses (phase 5.2-step 4)
    courses = relationship(
        "Course",
        back_populates="teacher"
    )


# ==========================================================
# PARENT MODEL
# (Phase 10.1 Step 1)
# ==========================================================

class Parent(Base):
    __tablename__ = "parents"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        unique=True           # One User account, One Parent profile 
    )

    full_name = Column(
        String,
        nullable=False
    )

    phone_number = Column(
        String,
        nullable=True
    )
    

# Course domain model  (phase 5.2-step 4)
class Course(Base):
    __tablename__ = "courses"

    # Primary course ID
    id = Column(Integer, primary_key=True, index=True)

    # Link course to teacher (creates the database relationship between courses and teachers)
    teacher_id = Column(
        Integer,
        ForeignKey("teachers.id")
    )

    # Course title
    title = Column(
        String,
        nullable=False
    )

    # Optional course description
    description = Column(
        String,
        nullable=True
    )

    # Relationship back to teacher
    teacher = relationship(
        "Teacher",
        back_populates="courses"
    )

    # One course can have many enrollments (phase 5.2-step 5)
    enrollments = relationship(
        "Enrollment",
        back_populates="course"
    )

    # One course can have many assignments (Phase 5.2 Step 6)
    assignments = relationship(
        "Assignment",
        back_populates="course"
    )


# Enrollment domain model (phase 5.2-step 5)
class Enrollment(Base):
    __tablename__ = "enrollments"

    # Primary enrollment ID
    id = Column(Integer, primary_key=True, index=True)

    # Link enrollment to student (This enrollment belongs to a specific student, and a specific course)
    student_id = Column(
        Integer,
        ForeignKey("students.id")
    )

    # Link enrollment to course (This enrollment belongs to a specific course, and a specific student)
    course_id = Column(
        Integer,
        ForeignKey("courses.id")
    )

    # Relationship back to student 
    student = relationship(
        "Student",
        back_populates="enrollments"
    )

    # Relationship back to course
    course = relationship(
        "Course",
        back_populates="enrollments"
    )


# Assignment domain model (Phase 5.2 Step 6)
class Assignment(Base):
    __tablename__ = "assignments"

    # Primary assignment ID
    id = Column(Integer, primary_key=True, index=True)

    # Link assignment to course
    course_id = Column(
        Integer,
        ForeignKey("courses.id")
    )

    # Assignment title
    title = Column(
        String,
        nullable=False
    )

    # Assignment instructions
    description = Column(
        String,
        nullable=True
    )

    # Relationship back to course
    course = relationship(
        "Course",
        back_populates="assignments"
    )

    # One assignment can have many submissions (Phase 5.2 Step 7)
    submissions = relationship(
        "Submission",
        back_populates="assignment"
    )


# Submission domain model (Phase 5.2 Step 7)
class Submission(Base):
    __tablename__ = "submissions"

    # Primary submission ID
    id = Column(Integer, primary_key=True, index=True)

    # Link submission to student
    student_id = Column(
        Integer,
        ForeignKey("students.id")
    )

    # Link submission to assignment
    assignment_id = Column(
        Integer,
        ForeignKey("assignments.id")
    )

    # Submission content   # Content could be a text answer, a file path to an uploaded document (PDF, Word documents,et ), or a link to an external resource depending on how you want to implement it later
    content = Column(
        String,
        nullable=False
    )

    # Relationship back to student
    student = relationship(
        "Student",
        back_populates="submissions"
    )

    # Relationship back to assignment
    assignment = relationship(
        "Assignment",
        back_populates="submissions"
    )

    # One submission can have one grade (Phase 5.2 Step 8)
    grade = relationship(
        "Grade",
        back_populates="submission",   # This creates the relationship between submissions and grades, allowing you to access the grade for a submission and vice versa.
        uselist=False                  # This indicates that each submission can have only one grade, enforcing a one-to-one relationship between submissions and grades.
    )


# Grade domain model (Phase 5.2 Step 8)
class Grade(Base):
    __tablename__ = "grades"

    # Primary grade ID
    id = Column(Integer, primary_key=True, index=True)

    # Link grade to submission
    submission_id = Column(
        Integer,
        ForeignKey("submissions.id")
    )

    # Numeric score
    grade_value = Column(
        Integer,
        nullable=False
    )

    # Teacher feedback
    feedback = Column(
        String,
        nullable=True
    )

    # Relationship back to submission
    submission = relationship(
        "Submission",
        back_populates="grade"
    )

# Announcement domain model (phase 7)
class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)

    teacher_id = Column(
        Integer,
        ForeignKey("teachers.id"),
        nullable=False
    )

    # Course that owns the announcement
    course_id = Column(
        Integer,
        ForeignKey("courses.id"),
        nullable=False
    )


    title = Column(String, nullable=False)

    message = Column(String, nullable=False)


class AnnouncementRead(Base):
    __tablename__ = "announcement_reads"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(
        Integer,
        ForeignKey("students.id"),
        nullable=False
    )

    announcement_id = Column(
        Integer,
        ForeignKey("announcements.id"),
        nullable=False
    )


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(
        Integer,
        ForeignKey("students.id"),
        nullable=False
    )

    message = Column(
        String,
        nullable=False
    )

    is_read = Column(
        Boolean,
        default=False
    )
# ==========================================================
# ATTENDANCE MODEL
# (Phase 9.1 Step 1)
# ==========================================================

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    student_id = Column(
        Integer,
        ForeignKey("students.id"),
        nullable=False
    )

    course_id = Column(
        Integer,
        ForeignKey("courses.id"),
        nullable=False
    )

    attendance_date = Column(
        Date,
        nullable=False
    )

    status = Column(
        String,
        nullable=False
    )

# ==========================================================
# PARENT STUDENT LINK
# (Phase 10.1 Step 3)
# ==========================================================

class ParentStudentLink(Base):
    __tablename__ = "parent_student_links"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    parent_id = Column(
        Integer,
        ForeignKey("parents.id"),
        nullable=False
    )

    student_id = Column(
        Integer,
        ForeignKey("students.id"),
        nullable=False
    )


# ==========================================================
# MESSAGE MODEL
# (Phase 11.1 Step 1)
# ==========================================================

class Message(Base):
    __tablename__ = "messages"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    sender_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    receiver_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    message = Column(
        String,
        nullable=False
    )

    is_read = Column(
        Boolean,
        default=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

# ==========================================================
# MEETING REQUEST MODEL
# (Phase 11.2 Step 1)
# ==========================================================

class MeetingRequest(Base):
    __tablename__ = "meeting_requests"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    parent_id = Column(
        Integer,
        ForeignKey("parents.id"),
        nullable=False
    )

    teacher_id = Column(
        Integer,
        ForeignKey("teachers.id"),
        nullable=False
    )

    subject = Column(
        String,
        nullable=False
    )

    message = Column(
        String,
        nullable=False
    )

    status = Column(
        String,
        default="Pending"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
#=================================================================
# FIRST BASIC MODEL FOR A SINGLE USER ROLE (STUDENT) - TO BE EXPANDED WITH TEACHER AND ADMIN ROLES LATER (SCALABLE DESIGN), ETC.

# # database tables and models for user authentication and roles
# from sqlalchemy import Column, Integer, String
# from .database import Base


# class User(Base):
#     __tablename__ = "users"

#     # Primary unique user ID
#     id = Column(Integer, primary_key=True, index=True)

#     # User email for authentication
#     email = Column(String, unique=True, index=True, nullable=False)

#     # Hashed password storage
#     password = Column(String, nullable=False)

#     # User role (student, teacher, admin)
#     role = Column(String, default="student", nullable=False)

#     # Student grade/class level
#     grade = Column(String, nullable=True)