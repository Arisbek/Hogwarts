import os, smtplib
from email.mime.text import MIMEText

def send_via_gmail(subject, html_body, to_addr):
    smtp_host = "smtp.gmail.com"     # Gmail SMTP
    smtp_port = 587                  # TLS port
    username  = "arisalikbaev@gmail.com"
    password  = "crqvkufqmnvupqtf"    # 16-char app password
    from_addr = username

    # Build message
    msg = MIMEText(html_body, "html")
    msg["Subject"] = subject
    msg["From"]    = from_addr
    msg["To"]      = to_addr

    # Send
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.ehlo()
        server.starttls()              # upgrade to encrypted
        server.login(username, password)
        server.send_message(msg)

    print("Sent via Gmail SMTP")
    
send_via_gmail("Test Subject", "<h1>Test HTML Body</h1>", "manuchehrqoriev798@gmail.com")