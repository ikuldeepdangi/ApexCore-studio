import smtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load the .env file
load_dotenv()

# Configuration from Environment Variables
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
INFO_EMAIL = os.getenv("INFO_EMAIL")

def send_mail(subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = INFO_EMAIL
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls() 
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
        print("Email sent successfully via .env config!")
        return True
    except Exception as e:
        print(f"Mail Error: {e}")
        return False