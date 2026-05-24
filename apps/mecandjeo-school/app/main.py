from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from .database import Base, engine
from .routes import auth, users, admin

# ✅ Create DB tables
Base.metadata.create_all(bind=engine)

# ✅ CREATE APP FIRST (this was your issue)
app = FastAPI(title="School Platform", version="0.1.0")


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