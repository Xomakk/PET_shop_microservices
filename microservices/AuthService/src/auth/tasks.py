"""Celery tasks for the AuthService."""

from celery_app import app
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from config import settings


@app.task(name="auth_service.send_email")
def send_email_task(subject: str, body: str, recipient_list: List[str]) -> None:
    """
    Send an email to the specified recipient list.

    Args:
        subject (str): Email subject.
        body (str): Email message body.
        recipient_list (list[str]): List of email addresses.
    """
    message = MIMEMultipart()
    message["From"] = settings.SMTP_USER
    message["To"] = ", ".join(recipient_list)
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, recipient_list, message.as_string())
            print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")
