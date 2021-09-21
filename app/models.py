from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.sqltypes import TIMESTAMP, Boolean
from .database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    surname = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    phone_number = Column(String)
    verified = Column(Boolean)

    def __init__(self, name, surname, email, hashed_password, phone_number, verified):
        self.name = name
        self.surname = surname
        self.email = email
        self.hashed_password = hashed_password
        self.phone_number = phone_number
        self.verified = verified


class LoginVerification(Base):
    __tablename__ = "login_verification"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False)
    code = Column(Integer, nullable=False)
    expiry_timestamp = Column(TIMESTAMP)

    def __init__(self, email, code, expiry_timestamp):
        self.email = email
        self.code = code
        self.expiry_timestamp = expiry_timestamp
