import smtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load the .env file
load_dotenv()

# Mapping variables correctly to match your .env file
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
# Note: Changed these to match your .env keys
SMTP_USER = os.getenv("SMTP_EMAIL") 
SMTP_PASS = os.getenv("SMTP_PASSWORD")
INFO_EMAIL = os.getenv("ADMIN_EMAIL")



def send_mail(subject, body):
    try:
        
        if not all([SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASS]):
            print("ERROR: One or more SMTP environment variables are missing!")
            return False

        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = INFO_EMAIL
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        print("DEBUG: Email object created.")

        # Logic for Port 465 (SSL) vs 587 (TLS)
        port = int(SMTP_PORT)
        if port == 465:
            print(f"DEBUG: Connecting to {SMTP_SERVER} via SSL (Port 465)...")
            server = smtplib.SMTP_SSL(SMTP_SERVER, port)
        else:
            print(f"DEBUG: Connecting to {SMTP_SERVER} via TLS (Port {port})...")
            server = smtplib.SMTP(SMTP_SERVER, port)
            server.starttls()

        server.login(SMTP_USER, SMTP_PASS)

        server.send_message(msg)
        print("DEBUG: Message sent.")
        
        server.quit()
        print("DEBUG: Connection closed successfully.")
        return True

    except Exception as e:
        print(f"!!! Mail Error Debugger !!!")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {e}")
        return False