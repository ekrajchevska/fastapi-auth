from starlette.requests import Request
from starlette.status import HTTP_400_BAD_REQUEST
from app.registration import reg_env
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from sqlalchemy.orm.session import Session
from ..services import user_service
from ..auth import token
from twilio.rest import Client
from .. import schemas, database, models
from passlib.context import CryptContext
from datetime import timedelta
import asyncio
import random


router = APIRouter(prefix="/auth-api", tags=['Users'])
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
client = Client(reg_env.TWILIO_ACCOUNT_SID, reg_env.TWILIO_AUTH_TOKEN)

########## User Registration ###########

@router.post("/register")
async def handle_register(user_request: schemas.UserCreate):
    await asyncio.get_event_loop().run_in_executor(
        None, send_verification_code, user_request.email)
    response = RedirectResponse('/verify', status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie('email', user_request.email)
    response.set_cookie('password', pwd_context.hash(user_request.password))
    response.set_cookie('name', user_request.name)
    response.set_cookie('surname', user_request.surname)
    response.set_cookie('phone_number', user_request.phone_number)
    return response


def send_verification_code(email):
    verification = client.verify.services(
        reg_env.TWILIO_VERIFY_SERVICE).verifications.create(
            to=email, channel='email')
    assert verification.status == 'pending'

@router.get("/verify")
def verify():
    pass


@router.post('/verify')
async def verify_code(request : Request, verification_obj : schemas.VerificationCode):
    cookies = request.cookies
    verified = await asyncio.get_event_loop().run_in_executor(
        None, check_verification_code, cookies['email'], verification_obj.code)
    if verified:
        response = RedirectResponse('/success', status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie('email', cookies['email'])
        response.set_cookie('password', cookies['password'])
        response.set_cookie('name', cookies['name'])
        response.set_cookie('surname', cookies['surname'])
        response.set_cookie('phone_number', cookies['phone_number'])
        
    else:
        response = RedirectResponse('/failure', status_code=status.HTTP_303_SEE_OTHER)
        
    return response

def check_verification_code(email, code):
    verification = client.verify.services(
        reg_env.TWILIO_VERIFY_SERVICE).verification_checks.create(
            to=email, code=code)
    return verification.status == 'approved'


@router.get("/success")
def create_user(request : Request, db: Session = Depends(database.get_db)):
    cookies = request.cookies
    db_user = user_service.get_user_by_email(db, cookies['email'])
    if db_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already registered, please login!")
    return user_service.create_user(db=db, user=schemas.UserCreate.parse_obj(cookies))

@router.get("/failure", status_code=status.HTTP_400_BAD_REQUEST)
def failed_register():
    pass



############# User Authentication #################


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# koga se koristi ova OAuth2PasswordRequestForm treba da se smeni Content-Type : application/x-www-form-urlencoded
# isto taka vo Body da se koristi x-www-form-urlencoded so keys/values

@router.post("/login", response_model=schemas.Token)
def login(user_login: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):   # ako se koristi klasava OAuth2..
    user = db.query(models.User).filter(models.User.email == user_login.username).first()               # mora username i password da se keys polinjava, bez
                                                                                                        # razlika dali username-ot e email ili neso dr
    if not user:    
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such user, please register!")
        
    if not pwd_context.verify(user_login.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail="Invalid password!")

    code = round(random.random() * 10000)
    message = client.messages.create(  
        messaging_service_sid = reg_env.TWILIO_MESSAGING_LOGIN_SERVICE_SID, 
        body = f"Your login code is {code}",  
        to = user.phone_number 
    ) 

    response = RedirectResponse('/logincode', status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie('code', code)
    response.set_cookie('email', user.email)

    return response



@router.get("/logincode")
def redirect_login():
    pass


@router.post("/logincode")
def login_code(request : Request, verification_obj : schemas.VerificationCode):
    cookies = request.cookies
    if verification_obj.code == cookies['code']:
        access_token_expires = timedelta(minutes=token.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = token.create_access_token(
        data={"email": cookies['email']}, expires_delta=access_token_expires    # data shto se enkodira vo jwt tokenot, moze da se smeni primer moze id 
        )                                                                   # bitno: da ne e huge tokenot, ama moze pojke raboti da se stavaat 
    
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification code!")


@router.get("/myprofile", response_model=schemas.User)
def get_myprofile(user_token: str = Depends(oauth2_scheme), db : Session = Depends(database.get_db)):
    token_data = token.validate_access_token(user_token)
    user = user_service.get_user_by_email(db, token_data.email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid email!")

    return user



@router.delete("/user/{user_id}", response_model=schemas.User)
def delete_user(user_id : int, db: Session = Depends(database.get_db)):
    db_user = user_service.delete_user(db, user_id)
    return db_user
