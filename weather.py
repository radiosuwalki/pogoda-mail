import os
import smtplib
import ssl
from email.mime.text import MIMEText

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
RECIPIENTS = os.getenv("RECIPIENTS")

CITY = os.getenv("CITY", "Gdańsk")

if not all([SMTP_SERVER, SMTP_USER, SMTP_PASS, RECIPIENTS]):
    raise ValueError("Brakuje ENV")

def send():
    msg = MIMEText(f"Pogoda test - {CITY}")
    msg["Subject"] = "Pogoda"
    msg["From"] = SMTP_USER
    msg["To"] = RECIPIENTS

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, RECIPIENTS, msg.as_string())

send()
print("OK")
