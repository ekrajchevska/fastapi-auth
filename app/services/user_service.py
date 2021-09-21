from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas
from datetime import datetime, timedelta


class UserService:

    def get_users(db: Session, skip: int = 0, limit: int = 100):
        return db.query(models.User).offset(skip).limit(limit).all()


    def get_user_by_id(db: Session, user_id: int):
        db_user = db.query(models.User).filter(models.User.id == user_id).first()
        if db_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"No user with id: {user_id} exists!")
        return db_user


    def get_user_by_email(db: Session, email: str):
        db_user = db.query(models.User).filter(models.User.email == email).first()
        return db_user


    def create_user(db: Session, user: schemas.UserCreate):
        db_user = models.User(name=user.name, surname=user.surname, email=user.email, 
            hashed_password=user.password, phone_number=user.phone_number, verified=False)

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user


    def verify_user(db: Session, email: str):
        db_user = db.query(models.User).filter(models.User.email == email).first()
        db_user.verified = True
        db.refresh(db_user)

        return db_user


    def create_login_verification_obj(db: Session, email: str, code: str):
         db_old_login = db.query(models.LoginVerification).filter(models.LoginVerification.email == email).first()
         if db_old_login != None:
            db.delete(db_old_login)
            db.commit()

         expire = datetime.utcnow() + timedelta(minutes=20)
         db_login_obj = models.LoginVerification(email, code, expire)

         db.add(db_login_obj)
         db.commit()
         db.refresh()

         return db_login_obj

    
    def verify_login(db: Session, email: str, code: str):
        db_login_obj = db.query(models.LoginVerification).filter(models.LoginVerification.email == email).first()
        
        if code != db_login_obj.code:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Invalid code!")

        if db_login_obj.expiry_timestamp < datetime.utcnow():
            raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Login code expired!")

        db.delete(db_login_obj)
        db.commit()

        

    def delete_user(db: Session, user_id: int):
        db_user = db.query(models.User).filter(models.User.id == user_id).first()
        if db_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"No user with id: {user_id} exists!")
        db.delete(db_user)
        db.commit()
        return db_user