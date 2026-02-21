import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
EMAIL_ADDRESS = os.getenv("SMTP_USER")
EMAIL_PASSWORD = os.getenv("SMTP_PASSWORD")


def send_otp_email(to_email: str, otp: str):
    subject = "Your OTP Verification Code"
    body = f"""
Hello,

Your OTP is: {otp}

This OTP will expire in 5 minutes.

Do not share this with anyone.

Regards,
EvalBee Team
"""

    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()
