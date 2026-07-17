import contextlib

from fastapi import FastAPI
import os
from app.endpoints.authentication_endpoints import router as auth_router
from app.scripts.database import init_db


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    """Brief explanation of the function.

    Args:
        app: FastAPI: Description of the arguments.

    Returns:
        None: Description of the return value.
    """
    await init_db()
    yield


app = FastAPI(title="Expenses Manager", lifespan=lifespan)


@app.get("/")
def read_root():
    return {"status": "Running smoothly!", "database_host": os.getenv("DATABASE_URL")}


app.include_router(auth_router)
