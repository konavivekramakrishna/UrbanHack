from pydantic import BaseModel
from typing import List

class UserBase(BaseModel):
    name: str
    age: int
    gender: str
    email: str
    city: str
    interests: List[str]

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

