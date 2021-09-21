from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from .registration import pwd_context
from .twilio_func import client
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import Response
from sqlalchemy.orm.session import Session
from .. import schemas, database
from app.registration import reg_env
from datetime import timedelta
from ..auth.token import (
    create_access_token,
    validate_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from ..services.user_service import UserService
import random


router = APIRouter(prefix="/auth-api", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
user_service = UserService()


@router.get("/hello")
def hello():
    return {"Hello": "world!"}


@router.post("/login", response_model=schemas.Token)
def login(
    user_login: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db),
):
    user = user_service.get_user_by_email(db, user_login.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such user, please register!",
        )

    if not pwd_context.verify(user_login.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password!"
        )

    if user.verified is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User not verified!"
        )

    code = round(random.random() * 10000)
    user_service.create_login_verification_obj(db, user.email, code)
    client.messages.create(
        messaging_service_sid=reg_env.TWILIO_MESSAGING_LOGIN_SERVICE_SID,
        body=f"Your login code is {code}",
        to=user.phone_number,
    )

    return Response(status=status.HTTP_201_CREATED)


@router.post("/logincode")
def login_code(
    verification_obj: schemas.VerificationObject, db: Session = Depends(database.get_db)
):

    user_service.verify_login(verification_obj.email, verification_obj.code)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"email": verification_obj.email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/myprofile", response_model=schemas.User)
def get_myprofile(
    user_token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)
):
    token_data = validate_access_token(user_token)
    user = user_service.get_user_by_email(db, token_data.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid email!"
        )

    return user


@router.delete("/user/{user_id}", response_model=schemas.User)
def delete_user(user_id: int, db: Session = Depends(database.get_db)):
    db_user = user_service.delete_user(db, user_id)
    return db_user
