from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    password: str
    grade: str

class UserLogin(BaseModel):
    email: str
    password: str