from fastapi import FastAPI
from app.api.v1 import leads
from app.db.session import engine
from app.models.lead import Base
from dotenv import load_dotenv

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Lead Management API")

app.include_router(leads.router, prefix="/api/v1/leads", tags=["leads"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Lead Management API"}