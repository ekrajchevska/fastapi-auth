from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

postgres_user = os.getenv("POSTGRES_USER")
postgres_password = os.getenv("POSTGRES_PASSWORD")
postgres_host = os.getenv("POSTGRES_HOST")
postgres_port = os.getenv("POSTGRES_PORT")
postgres_database = os.getenv("POSTGRES_DATABASE_FASTAPI")


# SQLALCHEMY_DATABASE_URL = "sqlite:///./auth_app.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:admin@0.0.0.0:5432/auth_users"
SQLALCHEMY_DATABASE_URL = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_database}"

# for docker localhost on windows is host.docker.internal
# if we also run postgres container then with docker-compose the host is service_name
# for kubernetes is almost the same, the host name is service_name.namespace

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # nov session obj za sekoj request (za razlika od flask)
