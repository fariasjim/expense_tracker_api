import contextlib
import jwt
import os
from fastapi import FastAPI, Request
from datetime import datetime, timezone
from app.endpoints.authentication_endpoints import router as auth_router
from app.endpoints.expenses import router as expense_router
from app.scripts.database import init_db
from app.scripts.authentication import SECRETKEY
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
LOG_FILE_PATH = LOG_DIR / "request_logs.txt"
os.makedirs(LOG_DIR, exist_ok=True)


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


@app.middleware("http")
async def log_request_time_middleware(request: Request, call_next):
    """Middleware for generating logs and request times."""
    request_url = request.url.path
    token = request.cookies.get("access-token")
    user = "No Token"
    if token:
        if token.startswith("Bearer "):
            token = token.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRETKEY, algorithms=["HS256"])
            user = payload.get("sub", "Unknown User")
        except Exception:
            user = "Invalid Token"
    starting_time = datetime.now(timezone.utc)
    try:
        response = await call_next(request)
        return response
    finally:
        ending_time = datetime.now(timezone.utc)
        elapsed_time = ending_time - starting_time
        timestamp = ending_time.strftime("%Y-%m-%d %H:%M:%S UTC")
        log_entry = (
            f"===================================\n"
            f"[{timestamp}]\n"
            f"URL: {request_url} \n"
            f"User: {user}\n"
            f"Elapsed Time: {elapsed_time.total_seconds():.4f}s\n"
            f"===================================\n"
            f"\n"
        )
        with open(LOG_FILE_PATH, "a", encoding="utf-8") as file:
            file.write(log_entry)


@app.get("/")
def read_root():
    return {"status": "Running smoothly!", "database_host": os.getenv("DATABASE_URL")}


app.include_router(auth_router)
app.include_router(expense_router)
