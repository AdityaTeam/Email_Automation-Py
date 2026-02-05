import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config_email import SENDER_EMAIL, APP_PASSWORD, SMTP_SERVER, SMTP_PORT

def send_email(receiver_email, subject="Automatic Email", body="Hello, this email was sent automatically using Python!"):
    """
    Function to send an email using the configured SMTP settings.
    
    :param receiver_email: Email address of the recipient
    :param subject: Subject of the email
    :param body: Body of the email
    """
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
        return True, None
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False, str(e)
