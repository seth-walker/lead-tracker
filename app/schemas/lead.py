import enum
from pydantic import BaseModel, EmailStr
from datetime import datetime

class LeadState(str, enum.Enum):
    PENDING = "PENDING"
    REACHED_OUT = "REACHED_OUT"

class LeadBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr

class LeadUpdateState(BaseModel):
    state: LeadState = LeadState.REACHED_OUT

class Lead(LeadBase):
    id: int
    resume_path: str
    state: LeadState
    created_at: datetime

    class Config:
        orm_mode = True 