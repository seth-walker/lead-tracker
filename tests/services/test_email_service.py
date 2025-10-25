import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.email_service import send_new_lead_emails
from app.models.lead import Lead as DBLead


@pytest.mark.asyncio
async def test_send_new_lead_emails_success(sample_lead, monkeypatch):
    """Test that both prospect and attorney emails are sent successfully."""
    # Set the ATTORNEY_EMAIL environment variable
    monkeypatch.setenv("ATTORNEY_EMAIL", "attorney@lawfirm.com")

    # Mock the FastMail instance and its send_message method
    mock_fm = MagicMock()
    mock_fm.send_message = AsyncMock()

    # Mock MessageSchema to capture its arguments
    mock_message_schema = MagicMock()

    with patch('app.services.email_service.FastMail', return_value=mock_fm), \
         patch('app.services.email_service.MessageSchema', mock_message_schema):
        # Call the function
        await send_new_lead_emails(sample_lead)

        # Verify MessageSchema was called twice (once for prospect, once for attorney)
        assert mock_message_schema.call_count == 2

        # Verify the first call was for the prospect
        first_call_kwargs = mock_message_schema.call_args_list[0][1]
        assert first_call_kwargs['subject'] == "Application Received"
        assert sample_lead.email in first_call_kwargs['recipients']
        assert sample_lead.first_name in first_call_kwargs['body']

        # Verify the second call was for the attorney
        second_call_kwargs = mock_message_schema.call_args_list[1][1]
        assert second_call_kwargs['subject'] == "New Lead Received"
        assert "attorney@lawfirm.com" in second_call_kwargs['recipients']
        assert sample_lead.first_name in second_call_kwargs['body']
        assert sample_lead.last_name in second_call_kwargs['body']
        assert sample_lead.email in second_call_kwargs['body']

        # Verify send_message was called twice
        assert mock_fm.send_message.call_count == 2


@pytest.mark.asyncio
async def test_send_new_lead_emails_missing_attorney_email(sample_lead, monkeypatch, capsys):
    """Test that function returns early when ATTORNEY_EMAIL is not set."""
    # Unset the ATTORNEY_EMAIL environment variable
    monkeypatch.delenv("ATTORNEY_EMAIL", raising=False)

    # Mock the FastMail instance
    mock_fm = MagicMock()
    mock_fm.send_message = AsyncMock()
    mock_message_schema = MagicMock()

    with patch('app.services.email_service.FastMail', return_value=mock_fm), \
         patch('app.services.email_service.MessageSchema', mock_message_schema):
        # Call the function
        await send_new_lead_emails(sample_lead)

        # Verify send_message was NOT called (function returned early)
        mock_fm.send_message.assert_not_called()

        # Verify the warning message was printed
        captured = capsys.readouterr()
        assert "ATTORNEY_EMAIL environment variable not set" in captured.out


@pytest.mark.asyncio
async def test_send_new_lead_emails_exception_handling(sample_lead, monkeypatch, capsys):
    """Test that exceptions during email sending are caught and logged."""
    # Set the ATTORNEY_EMAIL environment variable
    monkeypatch.setenv("ATTORNEY_EMAIL", "attorney@lawfirm.com")

    # Mock the FastMail instance to raise an exception
    mock_fm = MagicMock()
    mock_fm.send_message = AsyncMock(side_effect=Exception("SMTP connection failed"))
    mock_message_schema = MagicMock()

    with patch('app.services.email_service.FastMail', return_value=mock_fm), \
         patch('app.services.email_service.MessageSchema', mock_message_schema):
        # Call the function (should not raise exception)
        await send_new_lead_emails(sample_lead)

        # Verify the error message was printed
        captured = capsys.readouterr()
        assert "Failed to send emails" in captured.out
        assert "SMTP connection failed" in captured.out


@pytest.mark.asyncio
async def test_prospect_email_content(sample_lead, monkeypatch):
    """Test that the prospect email contains correct personalized content."""
    monkeypatch.setenv("ATTORNEY_EMAIL", "attorney@lawfirm.com")

    mock_fm = MagicMock()
    mock_fm.send_message = AsyncMock()
    mock_message_schema = MagicMock()

    with patch('app.services.email_service.FastMail', return_value=mock_fm), \
         patch('app.services.email_service.MessageSchema', mock_message_schema):
        await send_new_lead_emails(sample_lead)

        # Get the prospect email (first call)
        prospect_call_kwargs = mock_message_schema.call_args_list[0][1]

        # Verify email properties
        assert prospect_call_kwargs['subject'] == "Application Received"
        assert prospect_call_kwargs['recipients'] == [sample_lead.email]
        assert prospect_call_kwargs['subtype'] == "html"

        # Verify body contains expected content
        body = prospect_call_kwargs['body']
        assert f"Thank you for your application, {sample_lead.first_name}!" in body
        assert "We have successfully received your information and resume" in body
        assert "attorney will reach out to you shortly" in body


@pytest.mark.asyncio
async def test_attorney_email_content(sample_lead, monkeypatch):
    """Test that the attorney email contains correct lead information."""
    attorney_email = "attorney@lawfirm.com"
    monkeypatch.setenv("ATTORNEY_EMAIL", attorney_email)

    mock_fm = MagicMock()
    mock_fm.send_message = AsyncMock()
    mock_message_schema = MagicMock()

    with patch('app.services.email_service.FastMail', return_value=mock_fm), \
         patch('app.services.email_service.MessageSchema', mock_message_schema):
        await send_new_lead_emails(sample_lead)

        # Get the attorney email (second call)
        attorney_call_kwargs = mock_message_schema.call_args_list[1][1]

        # Verify email properties
        assert attorney_call_kwargs['subject'] == "New Lead Received"
        assert attorney_call_kwargs['recipients'] == [attorney_email]
        assert attorney_call_kwargs['subtype'] == "html"

        # Verify body contains lead details
        body = attorney_call_kwargs['body']
        assert "New Lead Submission" in body
        assert f"{sample_lead.first_name} {sample_lead.last_name}" in body
        assert sample_lead.email in body
        assert sample_lead.resume_path in body
        assert "Please review and update status as needed" in body


@pytest.mark.asyncio
async def test_send_new_lead_emails_with_special_characters(monkeypatch):
    """Test email sending with names containing special characters."""
    monkeypatch.setenv("ATTORNEY_EMAIL", "attorney@lawfirm.com")

    # Create a lead with special characters in name
    lead = DBLead()
    lead.first_name = "María"
    lead.last_name = "O'Brien"
    lead.email = "maria.obrien@example.com"
    lead.resume_path = "/uploads/resume_maria.pdf"

    mock_fm = MagicMock()
    mock_fm.send_message = AsyncMock()
    mock_message_schema = MagicMock()

    with patch('app.services.email_service.FastMail', return_value=mock_fm), \
         patch('app.services.email_service.MessageSchema', mock_message_schema):
        # Should not raise any exceptions
        await send_new_lead_emails(lead)

        # Verify MessageSchema was called twice
        assert mock_message_schema.call_count == 2

        # Verify names are properly included in email bodies
        prospect_body = mock_message_schema.call_args_list[0][1]['body']
        assert "María" in prospect_body

        attorney_body = mock_message_schema.call_args_list[1][1]['body']
        assert "María O'Brien" in attorney_body


@pytest.mark.asyncio
async def test_success_message_printed(sample_lead, monkeypatch, capsys):
    """Test that success message is printed when emails are sent successfully."""
    monkeypatch.setenv("ATTORNEY_EMAIL", "attorney@lawfirm.com")

    mock_fm = MagicMock()
    mock_fm.send_message = AsyncMock()
    mock_message_schema = MagicMock()

    with patch('app.services.email_service.FastMail', return_value=mock_fm), \
         patch('app.services.email_service.MessageSchema', mock_message_schema):
        await send_new_lead_emails(sample_lead)

        # Verify the success message was printed
        captured = capsys.readouterr()
        assert "Emails sent successfully" in captured.out


@pytest.mark.asyncio
async def test_send_emails_for_leads_with_same_name(monkeypatch):
    """Test that emails are sent correctly for multiple leads with the same name but different emails."""
    monkeypatch.setenv("ATTORNEY_EMAIL", "attorney@lawfirm.com")

    # Create two leads with the same name but different emails
    lead1 = DBLead()
    lead1.id = 1
    lead1.first_name = "John"
    lead1.last_name = "Smith"
    lead1.email = "john.smith@email1.com"
    lead1.resume_path = "/uploads/resume_john_smith_1.pdf"

    lead2 = DBLead()
    lead2.id = 2
    lead2.first_name = "John"
    lead2.last_name = "Smith"
    lead2.email = "john.smith@email2.com"
    lead2.resume_path = "/uploads/resume_john_smith_2.pdf"

    mock_fm = MagicMock()
    mock_fm.send_message = AsyncMock()
    mock_message_schema = MagicMock()

    with patch('app.services.email_service.FastMail', return_value=mock_fm), \
         patch('app.services.email_service.MessageSchema', mock_message_schema):

        # Send emails for first lead
        await send_new_lead_emails(lead1)

        # Verify first lead's emails
        assert mock_message_schema.call_count == 2
        first_lead_prospect = mock_message_schema.call_args_list[0][1]
        first_lead_attorney = mock_message_schema.call_args_list[1][1]

        # Verify first lead prospect email goes to correct address
        assert first_lead_prospect['recipients'] == [lead1.email]
        assert lead1.email in first_lead_attorney['body']
        assert lead1.resume_path in first_lead_attorney['body']

        # Reset mocks for second lead
        mock_message_schema.reset_mock()
        mock_fm.send_message.reset_mock()

        # Send emails for second lead
        await send_new_lead_emails(lead2)

        # Verify second lead's emails
        assert mock_message_schema.call_count == 2
        second_lead_prospect = mock_message_schema.call_args_list[0][1]
        second_lead_attorney = mock_message_schema.call_args_list[1][1]

        # Verify second lead prospect email goes to correct address
        assert second_lead_prospect['recipients'] == [lead2.email]
        assert lead2.email in second_lead_attorney['body']
        assert lead2.resume_path in second_lead_attorney['body']

        # Verify both have the same name in emails but different email addresses
        assert "John Smith" in first_lead_attorney['body']
        assert "John Smith" in second_lead_attorney['body']
        assert lead1.email != lead2.email  # Emails are different
        assert first_lead_prospect['recipients'] != second_lead_prospect['recipients']
