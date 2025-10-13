from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import shutil
import os

from app.schemas.lead import Lead, LeadBase, LeadUpdateState
from app.models.lead import Lead as DBLead
from app.db.session import get_db
from app.services.email_service import send_new_lead_emails
from app.api.v1.dependencies import get_api_key

router = APIRouter()

# Temp directory to save resumes locally
# TODO switch to S3/GCS for production
UPLOAD_DIRECTORY = "./uploads"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

@router.post("/", response_model=Lead)
async def create_lead(
    background_tasks: BackgroundTasks,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    resume: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Public endpoint to create a new lead.
    """
    # Check if email already exists
    db_lead = db.query(DBLead).filter(DBLead.email == email).first()
    if db_lead:
        raise HTTPException(status_code=400, detail="Email already registered.")

    # Save the resume file to the upload directory
    resume_path = os.path.join(UPLOAD_DIRECTORY, resume.filename)
    with open(resume_path, "wb") as buffer:
        shutil.copyfileobj(resume.file, buffer)

    # Create Lead schema object
    lead_in = LeadBase(first_name=first_name, last_name=last_name, email=email)

    # Create DB model instance
    new_lead = DBLead(**lead_in.model_dump(), resume_path=resume_path)
    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)
    
    # Send emails in the background
    background_tasks.add_task(send_new_lead_emails, new_lead)
    
    return new_lead

@router.get("/", response_model=List[Lead], dependencies=[Depends(get_api_key)])
def get_all_leads(db: Session = Depends(get_db)):
    """
    Authenticated endpoint to retrieve all leads.
    """
    return db.query(DBLead).all()

@router.patch("/{lead_id}/state", response_model=Lead, dependencies=[Depends(get_api_key)])
def update_lead_state(
    lead_id: int,
    lead_update: LeadUpdateState,
    db: Session = Depends(get_db)
):
    """
    Authenticated endpoint to update a lead's state.
    """
    db_lead = db.query(DBLead).filter(DBLead.id == lead_id).first()
    if not db_lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    db_lead.state = lead_update.state
    db.commit()
    db.refresh(db_lead)
    return db_lead