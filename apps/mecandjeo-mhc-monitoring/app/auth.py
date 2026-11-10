from datetime import datetime, timedelta, timezone
from typing import Iterable

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .config import JWT_EXPIRE_HOURS, SECRET_KEY
from .database import get_db
from .models import User


# Role constants keep route guards consistent across the application.
ROLE_OPERATOR = "operator"
ROLE_MANAGER = "manager"
ROLE_ADMIN = "admin"
ALLOWED_ROLES = {ROLE_OPERATOR, ROLE_MANAGER, ROLE_ADMIN}

# Password hashing context. bcrypt keeps plaintext passwords out of storage.
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Reads the bearer token from the Authorization header; auto_error=False lets us return our own consistent 401.
bearer_scheme = HTTPBearer(auto_error=False)

# Generic error avoids revealing whether the email, password, or token failed.
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


# Validate role values before storing or checking them.
def validate_role(role: str) -> str:
    normalized_role = role.lower().strip()
    if normalized_role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user role",
        )
    return normalized_role


# Convert a plaintext password into a secure hash for database storage.
def get_password_hash(password: str) -> str:
    return password_context.hash(password)


# Compare a submitted password with the stored password hash.
def verify_password(plain_password: str, password_hash: str) -> bool:
    return password_context.verify(plain_password, password_hash)


# Look up a user by email for registration duplicate checks and login.
def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email.lower()).first()


# Check login credentials without revealing which part failed.
def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    if not user.is_active:
        return None
    return user


# Create a signed JWT access token with user identity and role claims.
def create_access_token(user: User) -> str:
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY environment variable is required")

    expires_at = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS)
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "exp": expires_at,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


# Decode and validate a JWT access token.
def decode_access_token(token: str) -> dict:
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY environment variable is required")

    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except InvalidTokenError as exc:
        raise credentials_exception from exc


# Resolve the currently authenticated active user from the bearer token.
def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise credentials_exception
    payload = decode_access_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise credentials_exception

    try:
        user_pk = int(user_id)
    except ValueError as exc:
        raise credentials_exception from exc

    user = db.query(User).filter(User.id == user_pk).first()
    if not user or not user.is_active:
        raise credentials_exception
    return user


# Create a dependency that permits only users with one of the required roles.
def require_roles(*roles: str):
    allowed_roles = {validate_role(role) for role in roles}

    def role_dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return role_dependency


# Convenience dependency for routes available to any authenticated user.
def require_authenticated_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user


# Convenience helper for checking a user role in service-layer code.
def user_has_role(user: User, roles: Iterable[str]) -> bool:
    return user.role in {validate_role(role) for role in roles}
