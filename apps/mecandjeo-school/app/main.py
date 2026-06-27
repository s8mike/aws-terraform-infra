from fastapi import (
    FastAPI,
    Request
)
from fastapi.responses import HTMLResponse

from .database import Base, engine
from .routes import (
    auth,
    users,
    admin,
    students,
    teachers,
    courses,
    enrollments,
    assignments,
    submissions,
    grades,
    parents,
    messages,
    meetings,
    announcements
)            # from .routes import auth, users, admin, etc



# ✅ Create DB tables
Base.metadata.create_all(bind=engine)  # Look at all SQLAlchemy models, Check the database and Create any missing tables

# ✅ CREATE APP FIRST (this was your issue)
app = FastAPI(
    title="School Platform", 
    version="0.1.0")

# ==========================================================
# Security Headers Middleware
# [A security or processing checkpoint that every request
# passes through before reaching your API, and every response
# passes through before going back to user]
# (Phase 12.1 - Step 7)
# ==========================================================

@app.middleware("http")  # fnx is HTTP middleware=Run the fxn for every http request
async def add_security_headers(
    request: Request,
    call_next
):
    """
    Add security headers to every HTTP response.
    """

    response = await call_next(request)

    # Prevent browsers from MIME type sniffing 
    
    response.headers["X-Content-Type-Options"] = "nosniff" # [Do not guess, no executing. The browser must Trust the file type declared by the server. The server is the true source of files]
    response.headers["X-Frame-Options"] = "DENY" # protect a browser attack called Clickjacking
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin" # Protect information leakage from your site to another linked site. Does not send paths, etc when external link is clicked
    
    response.headers["Permission-Policy"] = (
        "camera=(), "
        "microphone=(), "
        "geolocation=()"  # Deny access to any of these features [current MVP does not include these]
    )
    # Security guard standing at the browser's entrance 
    # validate the source of files in question]. If from unapproved source, if wont run.
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "img-src 'self' data:; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "frame-ancestors 'none';"
    )


    return response


# ─────────────────────────────────────────
# Health Check
# ─────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok"}


# ─────────────────────────────────────────
# Simple Homepage (Optional UI)
# ─────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head>
            <title>School Platform</title>
        </head>
        <body>
            <h1>Welcome to School Platform</h1>
            <p>Backend is running ✅</p>
            <ul>
                <li><a href="/docs">API Docs</a></li>
                <li><a href="/api/users">Users</a></li>
                <li><a href="/admin/dashboard">Admin</a></li>
            </ul>
        </body>
    </html>
    """


# ─────────────────────────────────────────
# Routes
# ─────────────────────────────────────────
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api/users")
app.include_router(admin.router)
app.include_router(students.router)
app.include_router(teachers.router)
app.include_router(courses.router)
app.include_router(enrollments.router)
app.include_router(assignments.router)
app.include_router(submissions.router)
app.include_router(grades.router)
app.include_router(parents.router)
app.include_router(messages.router)
app.include_router(meetings.router)
app.include_router(announcements.router)