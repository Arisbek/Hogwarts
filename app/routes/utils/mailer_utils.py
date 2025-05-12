import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env', override=True)

# SMTP configuration
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "arisalikbaev@gmail.com"
SMTP_PASS = "crqvkufqmnvupqtf"
MAIL_FROM = "arisalikbaev@gmail.com"

# Jinja2 template environment
templates_dir = Path(__file__).parent / 'templates'
env = Environment(loader=FileSystemLoader(str(templates_dir)))

def send_verification_email(to_address: str, token: str) -> bool:
    """
    Render the email verification HTML template and send it via SMTP using a single-part HTML message.

    :param to_address: recipient email address
    :param token: verification token to include in link
    :return: True if sent successfully, False otherwise
    """
    try:
        # Load template
        template = env.get_template('email_verification.html')
        # Build verification URL (frontend handles this path)
        verify_url = f"http://localhost:8000/auth/confirm-email/{token}/"
        # Render HTML body
        html_body = template.render(email=to_address, url=verify_url)

         # Build message
        msg = MIMEText(html_body, "html")
        msg["Subject"] = 'Verify your account'
        msg["From"]    = MAIL_FROM
        msg["To"]      = to_address

        # Send via SMTP with TLS
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()                        # identify to server
            server.starttls()                    # secure the connection
            server.login(SMTP_USER, SMTP_PASS)   # authenticate
            server.send_message(msg)             # send the HTML email

        return True
    except Exception as e:
        # Log the exception
        print(f"Failed to send verification email: {e}")
        return False
