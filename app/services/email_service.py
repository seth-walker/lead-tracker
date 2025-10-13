import os
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import load_dotenv
from app.models.lead import Lead as DBLead 

load_dotenv()

# Configuration for the email server, loaded from .env
conf = ConnectionConfig(
    MAIL_USERNAME = os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD"),
    MAIL_FROM = os.getenv("MAIL_FROM"),
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER = os.getenv("MAIL_SERVER"),
    MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME"),
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

async def send_new_lead_emails(lead: DBLead):
    """
    Sends two emails after a new lead is created:
    1. A confirmation email to the prospect.
    2. A notification email to the internal attorney.
    """
    # 1. Create the confirmation email for the prospect
    prospect_body = f"""
    <html>
    <body>
        <h2>Thank you for your application, {lead.first_name}!</h2>
        <p>We have successfully received your information and resume.</p>
        <p>Our team will review your application and an attorney will reach out to you shortly.</p>
        <p>Best regards,<br>Lead Tracking Service</p>
    </body>
    </html>
    """
    
    prospect_message = MessageSchema(
        subject="Application Received",
        recipients=[lead.email],
        body=prospect_body,
        subtype="html"
    )

    # 2. Create the notification email for the attorney
    attorney_email_address = os.getenv("ATTORNEY_EMAIL")
    if not attorney_email_address:
        print("ATTORNEY_EMAIL environment variable not set. Skipping attorney notification.")
        return

    attorney_body = f"""
    <html>
    <body>
        <h2>New Lead Submission</h2>
        <p>A new lead has submitted their information:</p>
        <ul>
            <li><strong>Name:</strong> {lead.first_name} {lead.last_name}</li>
            <li><strong>Email:</strong> {lead.email}</li>
            <li><strong>Resume Path:</strong> {lead.resume_path}</li>
        </ul>
        <p>Please review and update status as needed.</p>
    </body>
    </html>
    """

    attorney_message = MessageSchema(
        subject="New Lead Received",
        recipients=[attorney_email_address],
        body=attorney_body,
        subtype="html"
    )

    # 3. Send both emails
    fm = FastMail(conf)
    try:
        await fm.send_message(prospect_message)
        await fm.send_message(attorney_message)
        print("Emails sent successfully.")
    except Exception as e:
        print(f"Failed to send emails: {e}")