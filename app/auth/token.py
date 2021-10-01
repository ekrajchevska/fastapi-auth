from jose import jwt, JWTError
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import Optional
import app.schemas as schemas

# from dotenv import load_dotenv
import os

# load_dotenv()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=os.getenv("expire"))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, os.getenv("secret"), algorithm=os.getenv("algorithm")
    )
    return encoded_jwt


def validate_access_token(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, os.getenv("secret"), algorithms=[os.getenv("algorithm")]
        )
        email: str = payload.get("email")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception

    return token_data
