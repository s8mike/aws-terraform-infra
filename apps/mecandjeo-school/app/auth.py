from passlib.context import CryptContext
import jwt
import os

SECRET = os.getenv("SECRET_KEY", "secret")

pwd_context = CryptContext(schemes=["bcrypt"])

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(password, hashed):
    return pwd_context.verify(password, hashed)

def create_token(data: dict):
    return jwt.encode(data, SECRET, algorithm="HS256")