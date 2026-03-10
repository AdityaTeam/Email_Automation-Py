import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
import os

# Email Accounts Configuration with passwords
EMAIL_ACCOUNTS = {
    "admissions": {
        "email": "admissions@company.com",
        "password": "YOUR_APP_PASSWORD",
        "name": "Admissions Team",
        "position": "Admissions Executive"
    },
    "info": {
        "email": "info@company.com",
        "password": "YOUR_APP_PASSWORD",
        "name": "Info Team",
        "position": "Information Desk"
    },
    "support": {
        "email": "support@company.com",
        "password": "YOUR_APP_PASSWORD",
        "name": "Support Team",
        "position": "Support Lead"
    },
    "contact": {
        "email": "contact@company.com",
        "password": "YOUR_APP_PASSWORD",
        "name": "Contact Team",
        "position": "Customer Relations"
    },
    "dhrupal": {
        "email": "dhrupalmakwana149@gmail.com",
        "password": "uzai vlxp tqjx odlf",
        "name": "Dhrupal Makwana",
        "position": "Business Development Manager"
    }
}

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def send_email(receiver_email, subject, body, sender_key="dhrupal"):
    """
    Send an email using the specified sender account.
    
    Args:
        receiver_email: Recipient email address
        subject: Email subject
        body: Email body content
        sender_key: Key to identify sender account (default: 'dhrupal')
    
    Returns:
        Tuple (success: bool, error: str or None)
    """
    
    sender = EMAIL_ACCOUNTS.get(sender_key)
    
    if not sender:
        return False, "Invalid sender key"
    
    sender_email = sender["email"]
    sender_password = sender["password"]
    
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    
    # Attach body as plain text
    msg.attach(MIMEText(body, "plain"))
    
    try:
        # Connect to SMTP server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(sender_email, sender_password)
        
        # Send email
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        
        return True, None
    
    except Exception as e:
        return False, str(e)


def send_email_with_details(receiver_email, subject, body, from_email, from_name, cc_email=None, logo_url=None):
    """
    Enhanced email sending function with custom From name, CC support, and logo.
    
    Args:
        receiver_email: Recipient email address
        subject: Email subject
        body: Email body content
        from_email: Sender email address
        from_name: Sender display name
        cc_email: CC recipient email (optional)
        logo_url: URL of company logo (optional)
    
    Returns:
        Tuple (success: bool, error: str or None)
    """
    
    # Find sender account by email
    sender_account = None
    for key, account in EMAIL_ACCOUNTS.items():
        if account['email'] == from_email:
            sender_account = account
            break
    
    if not sender_account:
        return False, "Sender email not configured"
    
    sender_email = sender_account["email"]
    sender_password = sender_account["password"]
    
    # Create message
    msg = MIMEMultipart('mixed')
    msg["From"] = f"{from_name} <{sender_email}>"
    msg["To"] = receiver_email
    msg["Subject"] = subject
    
    if cc_email:
        msg["CC"] = cc_email
    
    # Create text part
    text_part = MIMEText(body, "plain")
    msg.attach(text_part)
    
    # If logo URL provided, add it as embedded image (optional)
    if logo_url:
        try:
            # Note: In production, you might want to fetch and embed the actual logo
            # This is a simplified version
            pass
        except Exception:
            pass
    
    try:
        # Connect to SMTP server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(sender_email, sender_password)
        
        # Prepare recipients
        recipients = [receiver_email]
        if cc_email:
            recipients.append(cc_email)
        
        # Send email
        server.sendmail(sender_email, recipients, msg.as_string())
        server.quit()
        
        return True, None
    
    except Exception as e:
        return False, str(e)


def get_email_accounts():
    """
    Get all configured email accounts (without passwords).
    
    Returns:
        Dictionary of email accounts with public info
    """
    accounts = {}
    for key, account in EMAIL_ACCOUNTS.items():
        accounts[key] = {
            "email": account["email"],
            "name": account.get("name", key.title())
        }
    return accounts


def send_email_with_attachment(receiver_email, subject, body, from_email, from_name, cc_email=None, attachment_path=None, attachment_name=None):
    """
    Enhanced email sending function with attachment support.
    
    Args:
        receiver_email: Recipient email address
        subject: Email subject
        body: Email body content
        from_email: Sender email address
        from_name: Sender display name
        cc_email: CC recipient email (optional)
        attachment_path: Path to attachment file (optional)
        attachment_name: Name for the attachment (optional)
    
    Returns:
        Tuple (success: bool, error: str or None)
    """
    
    # Find sender account by email
    sender_account = None
    for key, account in EMAIL_ACCOUNTS.items():
        if account['email'] == from_email:
            sender_account = account
            break
    
    if not sender_account:
        return False, "Sender email not configured"
    
    sender_email = sender_account["email"]
    sender_password = sender_account["password"]
    
    # Create message
    msg = MIMEMultipart('mixed')
    msg["From"] = f"{from_name} <{sender_email}>"
    msg["To"] = receiver_email
    msg["Subject"] = subject
    
    if cc_email:
        msg["CC"] = cc_email
    
    # Create text part
    text_part = MIMEText(body, "plain")
    msg.attach(text_part)
    
    # Add attachment if provided
    if attachment_path and os.path.exists(attachment_path):
        try:
            with open(attachment_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                
                # Use provided name or extract from path
                filename = attachment_name or os.path.basename(attachment_path)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {filename}'
                )
                msg.attach(part)
        except Exception as e:
            return False, f"Error attaching file: {str(e)}"
    
    try:
        # Connect to SMTP server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(sender_email, sender_password)
        
        # Prepare recipients
        recipients = [receiver_email]
        if cc_email:
            recipients.append(cc_email)
        
        # Send email
        server.sendmail(sender_email, recipients, msg.as_string())
        server.quit()
        
        return True, None
    
    except Exception as e:
        return False, str(e)
