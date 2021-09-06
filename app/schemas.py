from app.database import Base
from typing import List, Optional
from pydantic import BaseModel

class UserCreate(BaseModel):
    name : str
    surname : str
    email : str
    password : str
    phone_number : str

class UserLogin(BaseModel):
    email : str
    password : str

class User(BaseModel):
    id : int
    name : str
    surname : str
    email : str
    hashed_password : str
    phone_number : str

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class VerificationCode(BaseModel):
    code : Optional[str] = None
