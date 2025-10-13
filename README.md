# lead-tracker

This is a lead tracking application. 

## Setup Instructions:

Clone the repository.

Create a virtual environment: `python -m venv venv`

Activate it: `source venv/bin/activate`

Install dependencies: `pip install -r requirements.txt`

Create a `.env` file and set the API_KEY and other email creditionals (sent via LastPass).

## To run the Application:

Run `uvicorn app.main:app --reload`

Example workflow:

### 1. User submits lead information:
```
curl -X POST \
  "http://127.0.0.1:8000/api/v1/leads/" \
  -F "first_name=lead" \
  -F "last_name=example" \
  -F "email=seths.lead.tracker@gmail.com" \
  -F "resume=@./resume_example.txt"
```
This command will send 1 email to the user confirming receipt of the lead, and 1 email to the attorney notifying them of the lead creation.

### 2. Attorney gets lead information
```
curl -X GET \
  "http://127.0.0.1:8000/api/v1/leads/" \
  -H "X-API-Key: my-secret-api-key" 
```

### 3. Attorney updates lead status to `REACHED_OUT`
```
curl -X PATCH \
  "http://127.0.0.1:8000/api/v1/leads/1/state" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: my-secret-api-key" \
  -d '{"state": "REACHED_OUT"}'
```


# Design Choices

I used FastAPI framework with SQLite as it is a light-weight storage for us to use for local use. I used SQLAlchemy as an ORM as it is relatively light weight way for Python to iteract with the DB. Currently the resume is simply uploaded to `/uploads` folder, though this would need to be moved to S3, GCS, etc. For the purposes of this exercise, I use API Key authentication, but would probably set up OAuth for a true production product. I tried to organized the code into a modular structure (separating API endpoints, database models, and Pydantic schemas) to enable maintainability and scalability, while avoiding over-engineering it. 
