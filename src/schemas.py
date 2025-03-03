from pydantic import BaseModel, EmailStr
from typing import List

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    gender: str  # 'M' or 'F'
    city: str
    interests: List[str]

class UserUpdateInterests(BaseModel):
    interests: List[str]

class UserMatch(BaseModel):
    matched_user_id: int
    similarity: int
