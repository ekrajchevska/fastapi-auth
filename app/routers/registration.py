from fastapi.openapi.models import Response
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm.session import Session
from .. import schemas, database
from passlib.context import CryptContext
from . import twilio_func
from app.services.user_service import UserService


router = APIRouter(prefix="/auth-api", tags=["Registration"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

user_service = UserService()


@router.post("/register")
async def handle_register(
    user_request: schemas.UserCreate, db: Session = Depends(database.get_db)
):
    twilio_func.send_verification_code(user_request.email)
    user_request.password = pwd_context.hash(user_request.password)
    user_service.create_user(db, user_request)

    return Response(status=status.HTTP_201_CREATED)


@router.post("/verify")
async def verify_code(
    verification_obj: schemas.VerificationObject, db: Session = Depends(database.get_db)
):
    verified = twilio_func.check_verification_code(
        verification_obj.email, verification_obj.code
    )

    if verified:
        user_service.verify_user(db, verification_obj.email)
        return Response(status=status.HTTP_202_ACCEPTED)

    return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
