from fastapi import FastAPI
import os

app = FastAPI()


@app.get("/")
def read_root():
    return {"status": "Running smoothly!", "database_host": os.getenv("DATABASE_URL")}
