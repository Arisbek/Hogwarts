from beanie import Document
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class User(Document):
    username: str
    email: EmailStr
    hashed_password: str
    is_verified: bool=False
    role: str = "student"  # "admin" or "student"
    marks: list[(datetime, float)] = []  # List of marks for the user

    class Settings:
        name = "users"

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None