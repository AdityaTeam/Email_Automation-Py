import smtplib 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 🔥 MULTIPLE SENDER EMAILS
EMAIL_ACCOUNTS = {
    "dhrupal": {
        "email": "dhrupalmakwana149@gmail.com",
        "password": "uzai vlxp tqjx odlf"
    },
    "company": {
        "email": "company@gmail.com",
        "password": "app_password1"
    },
    "hr": {
        "email": "hr@gmail.com",
        "password": "app_password2"
    },
    "support": {
        "email": "support@gmail.com",
        "password": "app_password3"
    }
}

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def send_email(receiver_email, subject, body, sender_key="company"):
    sender = EMAIL_ACCOUNTS[sender_key]

    SENDER_EMAIL = sender["email"]
    APP_PASSWORD = sender["password"]

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

        return True, None
    except Exception as e:
        return False, str(e)
