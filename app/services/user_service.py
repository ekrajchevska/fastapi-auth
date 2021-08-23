from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas

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
    db_user = models.User(name=user.name, surname=user.surname, email=user.email, hashed_password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"No user with id: {user_id} exists!")
    db.delete(db_user)
    db.commit()
    return db_user