import pytest
from app.models.lead import Lead as DBLead
from app.schemas.lead import LeadState


@pytest.fixture
def sample_lead():
    """Fixture that provides a sample Lead instance for testing."""
    lead = DBLead()
    lead.id = 1
    lead.first_name = "John"
    lead.last_name = "Doe"
    lead.email = "john.doe@example.com"
    lead.resume_path = "/uploads/resume_john_doe.pdf"
    lead.state = LeadState.PENDING
    return lead


@pytest.fixture
def sample_lead_no_resume():
    """Fixture that provides a sample Lead instance without a resume."""
    lead = DBLead()
    lead.id = 2
    lead.first_name = "Jane"
    lead.last_name = "Smith"
    lead.email = "jane.smith@example.com"
    lead.resume_path = None
    lead.state = LeadState.PENDING
    return lead


@pytest.fixture
def leads_with_same_name():
    """Fixture that provides multiple Lead instances with the same name but different emails."""
    lead1 = DBLead()
    lead1.id = 3
    lead1.first_name = "John"
    lead1.last_name = "Smith"
    lead1.email = "john.smith@email1.com"
    lead1.resume_path = "/uploads/resume_john_smith_1.pdf"
    lead1.state = LeadState.PENDING

    lead2 = DBLead()
    lead2.id = 4
    lead2.first_name = "John"
    lead2.last_name = "Smith"
    lead2.email = "john.smith@email2.com"
    lead2.resume_path = "/uploads/resume_john_smith_2.pdf"
    lead2.state = LeadState.PENDING

    return [lead1, lead2]
