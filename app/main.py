from fastapi import FastAPI, Request
from app import models
from app.database import engine
from .routers import user
import logging


app = FastAPI()

logger = logging.getLogger(__name__)
#logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))

models.Base.metadata.create_all(bind=engine)
app.include_router(user.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    #logger.debug(request.headers)
    response = await call_next(request)
    #logger.debug(response.headers)
    return response

