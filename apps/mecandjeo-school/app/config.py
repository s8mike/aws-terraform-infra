import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")

JWT_EXPIRE_HOURS = int(
    os.getenv("JWT_EXPIRE_HOURS", "24")
)

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL environment variable is required"
    )

if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY environment variable is required"
    )