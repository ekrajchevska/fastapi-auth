from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLALCHEMY_DATABASE_URL = "sqlite:///./auth_app.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:admin@localhost:5432/auth-users"
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:admin@postgres:5432/auth-users"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()      # nov session obj za sekoj request (za razlika od flask)