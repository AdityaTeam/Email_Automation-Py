from unittest import result

from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_from_directory
from prompt_toolkit import prompt
from send_email import send_email, send_email_with_attachment
from ai_email_generator import generate_email
import pandas as pd
from pymongo import MongoClient
import os
from datetime import datetime
import random
import time
from functools import wraps

# Import ObjectId for MongoDB _id conversion:
try:
    from bson.objectid import ObjectId
except ImportError:
    from bson import ObjectId

app = Flask(__name__)
app.secret_key = "your_secret_key_here"
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["ATTACHMENTS_FOLDER"] = "attachments"

# Create folders if they don't exist
if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])
if not os.path.exists(app.config["ATTACHMENTS_FOLDER"]):
    os.makedirs(app.config["ATTACHMENTS_FOLDER"])

# MongoDB Connection:
client = MongoClient("mongodb+srv://Prompt_em:asdfghjkl@cluster0.o9em7j3.mongodb.net/")
db = client["email_generator"]
collection = db["emails"]
users_collection = db["users"]
settings_collection = db["settings"]
prompts_collection = db["prompts"]  # New: prompts stored in MongoDB

# Initialize default prompts in MongoDB if empty
def initialize_prompts():
    default_prompts = [
        {"id": 1, "name": "Business Proposal","template": """You are writing the email as Hansraj Ventures Private Limited, a staffing and recruitment company that provides skilled professionals to businesses.

Your task is to draft a professional hiring support email responding to the following requirement.

Instructions:
• The email must be addressed to the client who posted the requirement (NOT to candidates).
• Position Hansraj Ventures as a staffing partner that can provide qualified professionals.
• Keep the email concise, professional, and business-focused (150–180 words).
• Avoid placeholders like [Client Name], [Job Board], etc.
• Do not repeat the requirement text exactly; summarize it naturally.
• Maintain a confident but polite tone.

The email must include these sections:
1. Professional greeting
2. Brief understanding of the hiring requirement
3. Hiring models offered by Hansraj Ventures:
   - Contractual
   - Contract-to-hire
   - Full-time staffing
4. Screening and validation approach
5. Short meeting request
6. Mention that the company profile is attached
7. Professional closing such as "Looking forward to connecting."

Do NOT include any signature because it will be added automatically.

Hiring Requirement:
{requirement}
"""
},
        {"id": 2, "name": "Quick Hiring Support Pitch", "template": "Draft a short and sharp hiring support email for the below requirement from Hansraj Ventures. Include: Quick understanding of roles Immediate sourcing capability Flexible engagement models 15-minute alignment meeting request Mention attachments Keep it crisp, under 200 words, and professional. Do NOT include any signature because it will be added automatically. Requirement: {requirement}"},
        {"id": 3, "name": "Strategic Staffing Partnership Proposal", "template": "Write a professional hiring collaboration email positioning Hansraj Ventures as a long-term staffing partner for the below requirement. Include: Strategic hiring approach Performance-driven screening model Contractual + permanent hiring options Mutual business benefits Meeting proposal for commercial discussion Attachment reference Tone: Confident, structured, and business-driven. Do NOT include any signature because it will be added automatically. Requirement: {requirement}"},
        {"id": 4, "name": "Contractual Hiring Proposal", "template": "Prepare a hiring proposal email focused mainly on contractual on-site and task-based hiring for the below requirement. Include: Risk reduction benefits Cost optimization Flexible scaling Quick meeting request Attachments mention Keep it simple and professional. Do NOT include any signature because it will be added automatically. Requirement: {requirement}"},
        {"id": 5, "name": "Urgent Hiring Support Email", "template": "Draft a professional hiring support email for urgent / immediate joiner requirement below. Emphasize: Fast-track sourcing Pre-screened talent pool Immediate interview coordination 24-hour initiation timeline Request for quick discussion Attachments reference Keep it short and impactful. Do NOT include any signature because it will be added automatically. Requirement: {requirement}"},
        {"id": 6, "name": "Structured Hiring Proposal Email", "template": "Generate a structured hiring proposal email with the following sections: Greeting Understanding of hiring requirement Our engagement models Screening process Meeting request for alignment and commercial discussion Mention attachments Professional closing Keep it concise and ready to send. Do NOT include any signature because it will be added automatically. Requirement: {requirement}"},
        {"id": 7, "name": "Short Hiring Collaboration Pitch", "template": "Write a compact hiring collaboration email that can also be used as a LinkedIn or WhatsApp pitch. Include: Understanding of roles Contractual + full staffing support Quick meeting request Attachments mention Under 170 words. Do NOT include any signature because it will be added automatically. Requirement: {requirement}"}
    ]
    
    if prompts_collection.count_documents({}) == 0:
        prompts_collection.insert_many(default_prompts)
        print("Default prompts initialized in MongoDB")

# Get AI_PROMPTS from MongoDB
def get_prompts_from_db():
    prompts = list(prompts_collection.find({}))
    
    for p in prompts:
        p["_id"] = str(p["_id"])
    
    prompts.sort(key=lambda x: x.get("id", 0), reverse=True)
    return prompts

# Initialize prompts on startup
initialize_prompts()

# Company Information - Used in email signature
COMPANY_INFO = {
    "name": "Hansraj Ventures Pvt Ltd",
    "position": "Business Development Executive",
    "email": "contact@hansrajventures.com",
    "phone": "+91 9073663834",
    "website": "www.hansrajventures.com",
    "logo_url": "https://via.placeholder.com/150x50?text=Company+Logo"
}

# Sender email accounts with executive names and positions (4-5 company emails)
EMAIL_ACCOUNTS = {
    "admissions": {"email": "admissions@company.com", "name": "Admissions Team", "position": "Admissions Executive"},
    "info": {"email": "info@company.com", "name": "Info Team", "position": "Information Desk"},
    "support": {"email": "support@company.com", "name": "Support Team", "position": "Support Lead"},
    "contact": {"email": "contact@company.com", "name": "Contact Team", "position": "Customer Relations"},
    "dhrupal": {"email": "dhrupalmakwana149@gmail.com", "name": "Dhrupal Makwana", "position": "Business Development Manager"}
}

# CC email accounts (3-4 predefined options)
CC_ACCOUNTS = {
    "manager": {"email": "manager@company.com", "name": "Project Manager"},
    "hr": {"email": "hr@company.com", "name": "HR Department"},
    "marketing": {"email": "marketing@company.com", "name": "Marketing Team"},
    "dhrupal": {"email": "dhrupalmakwana149@gmail.com", "name": "Dhrupal Makwana"}
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        user = users_collection.find_one({"username": username, "password": password})
        if user:
            session["user_id"] = str(user["_id"])
            session["username"] = user["username"]
            last_sender = settings_collection.find_one({"user_id": session["user_id"]})
            if last_sender:
                session["last_sender"] = last_sender.get("last_sender", "dhrupal")
            else:
                session["last_sender"] = "dhrupal"
            return jsonify({"success": True, "redirect": url_for("index")})
        else:
            return jsonify({"success": False, "message": "Invalid username or password"})
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
@login_required
def index():
    last_sender = session.get("last_sender", "dhrupal")
    prompts = get_prompts_from_db()

    return render_template(
        "index.html",
        prompts=prompts,
        email_accounts=EMAIL_ACCOUNTS,
        cc_accounts=CC_ACCOUNTS,
        company_info=COMPANY_INFO,
        last_sender=last_sender
    )

@app.route("/api/prompts", methods=["GET"])
@login_required
def get_prompts():
    prompts = get_prompts_from_db()
    return jsonify(prompts)

@app.route("/api/prompts", methods=["POST"])
@login_required
def add_prompt():
    data = request.get_json()
    name = data.get("name")
    template = data.get("template")
    
    if not name or not template:
        return jsonify({"error": "Name and template are required"}), 400
    
    # Get the highest ID and add new prompt at the beginning
    existing_prompts = list(prompts_collection.find({}, {"id": 1}).sort("id", -1).limit(1))
    new_id = existing_prompts[0]["id"] + 1 if existing_prompts else 1
    
    prompt = {
        "id": new_id,
        "name": name,
        "template": template
    }
    
    # Insert at beginning (highest priority)
    result = prompts_collection.insert_one(prompt)

    prompt["_id"] = str(result.inserted_id)

    return jsonify({"success": True, "prompt":prompt})

@app.route("/api/prompts/<int:prompt_id>", methods=["PUT"])
@login_required
def update_prompt(prompt_id):
    data = request.get_json()
    name = data.get("name")
    template = data.get("template")
    
    if not name or not template:
        return jsonify({"error": "Name and template are required"}), 400
    
    result = prompts_collection.update_one(
        {"id": prompt_id},
        {"$set": {"name": name, "template": template}}
    )
    
    if result.matched_count == 0:
        return jsonify({"error": "Prompt not found"}), 404
    
    return jsonify({"success": True})

@app.route("/api/prompts/<int:prompt_id>", methods=["DELETE"])
@login_required
def delete_prompt(prompt_id):
    result = prompts_collection.delete_one({"id": prompt_id})
    
    if result.deleted_count == 0:
        return jsonify({"error": "Prompt not found"}), 404
    
    return jsonify({"success": True})

@app.route("/upload_attachment", methods=["POST"])
@login_required
def upload_attachment():
    if 'attachment' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['attachment']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # Save file to attachments folder
    filename = f"{datetime.now().timestamp()}_{file.filename}"
    filepath = os.path.join(app.config["ATTACHMENTS_FOLDER"], filename)
    file.save(filepath)
    
    return jsonify({
        "success": True, 
        "filename": filename,
        "filepath": filepath,
        "original_name": file.filename
    })

@app.route("/attachments/<filename>")
@login_required
def get_attachment(filename):
    return send_from_directory(app.config["ATTACHMENTS_FOLDER"], filename)

@app.route("/api/company-info", methods=["GET"])
@login_required
def get_company_info():
    return jsonify(COMPANY_INFO)

@app.route("/api/email-accounts", methods=["GET"])
@login_required
def get_email_accounts():
    return jsonify(EMAIL_ACCOUNTS)

@app.route("/api/cc-accounts", methods=["GET"])
@login_required
def get_cc_accounts():
    return jsonify(CC_ACCOUNTS)

@app.route("/upload", methods=["POST"])
@login_required
def upload_file():
    file = request.files["file"]
    if file and file.filename.endswith(".xlsx"):
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)
        df = pd.read_excel(filepath)
        df.columns = df.columns.str.strip().str.lower()
        column_mapping = {"name": "name", "first name": "name", "full name": "name", "email": "email", "email address": "email", "phone": "phone", "phone number": "phone", "company": "company", "company name": "company", "requirement": "requirement", "requirements": "requirement", "need": "requirement", "description": "requirement"}
        df = df.rename(columns=column_mapping)
        required_columns = ["name", "email", "phone", "company", "requirement"]
        df = df[[col for col in required_columns if col in df.columns]]
        df = df.fillna("")
        records = df.to_dict(orient="records")
        for r in records:
            r["status"] = "pending"
            r["created_at"] = datetime.now()
            r["sent_by"] = None
            r["sent_at"] = None
            r["prompt_used"] = None
            r["email_content"] = None
            r["subject"] = None
            r["user_id"] = session.get("user_id")
        if records:
            collection.insert_many(records)
        os.remove(filepath)
        return jsonify({"message": f"{len(records)} records stored successfully!"})
    return jsonify({"error": "Please upload .xlsx file only"}), 400

@app.route("/generate_email", methods=["POST"])
@login_required
def generate_single_email():

    data = request.get_json()

    recipient_id = data.get("recipient_id")
    prompt_id = data.get("prompt_id")
    custom_email = data.get("custom_email", "")
    subject = data.get("subject", "AI Generated Email")

    if not recipient_id:
        return jsonify({"error": "Recipient ID required"}), 400

    if not prompt_id:
        return jsonify({"error": "Prompt ID required"}), 400

    try:
        recipient = collection.find_one({"_id": ObjectId(recipient_id)})
    except:
        return jsonify({"error": "Invalid recipient ID"}), 400

    if not recipient:
        return jsonify({"error": "Recipient not found"}), 404

    prompts = get_prompts_from_db()
    prompt_obj = next((p for p in prompts if p["id"] == int(prompt_id)), None)

    if not prompt_obj:
        return jsonify({"error": "Prompt not found"}), 404


    # Fix recipient name
    recipient_name = recipient.get("name", "").strip()
    greeting_name = recipient_name if recipient_name else "Sir/Madam"
    recipient["name"] = greeting_name


    # Generate email
    if custom_email:
        email_body = custom_email
    else:
        try:
            email_body = generate_email(recipient, prompt_obj["template"])
        except Exception as e:
            return jsonify({"error": str(e)}), 500


    full_email = email_body


    # Save generated email
    collection.update_one(
        {"_id": recipient["_id"]},
        {"$set": {
            "email_content": full_email,
            "subject": subject,
            "prompt_used": prompt_obj["name"],
            "generated_at": datetime.now(),
            "generated_by": session.get("username", "admin"),
            "recipient_name": recipient.get("name"),
            "recipient_email": recipient.get("email")
        }}
    )


    return jsonify({
        "success": True,
        "email_content": full_email,
        "prompt_used": prompt_obj["name"],
        "subject": subject
    })
@app.route("/api/recipients", methods=["GET"])
@login_required
def get_recipients():
    status = request.args.get("status", "all")
    if status == "all":
        recipients = list(collection.find({"user_id": session.get("user_id")}))
    else:
        recipients = list(collection.find({"status": status, "user_id": session.get("user_id")}))
    for r in recipients:
        r["_id"] = str(r["_id"])
    return jsonify(recipients)

@app.route("/send_single_email", methods=["POST"])
@login_required
def send_single_email():

    data = request.get_json()

    recipient_id = data.get("recipient_id")
    sender_key = data.get("sender")
    cc_key = data.get("cc")
    subject = data.get("subject", "AI Generated Email")
    custom_email = data.get("custom_email", "")
    custom_from_name = data.get("from_name", "").strip()

    try:
        recipient = collection.find_one({"_id": ObjectId(recipient_id)})
    except:
        return jsonify({"error": "Invalid recipient ID"}), 400

    if not recipient:
        return jsonify({"error": "Recipient not found"}), 404


    sender_info = EMAIL_ACCOUNTS.get(sender_key)

    if not sender_info:
        return jsonify({"error": "Invalid sender"}), 400


    # From name
    from_name = custom_from_name if custom_from_name else sender_info["name"]


    # CC email
    cc_email = None
    if cc_key and cc_key in CC_ACCOUNTS:
        cc_email = CC_ACCOUNTS[cc_key]["email"]


    email_body = custom_email or recipient.get("email_content", "")

    if not email_body:
        return jsonify({"error": "No email content available"}), 400


    signature = f"""

Best Regards,
{from_name}
{sender_info['position']}

Company: {COMPANY_INFO['name']}
Website: {COMPANY_INFO['website']}
Email: {COMPANY_INFO['email']}
Phone: {COMPANY_INFO['phone']}

[Company Logo: {COMPANY_INFO['logo_url']}]
"""

    full_email = email_body + signature


    attachment_path = data.get("attachment_path")
    attachment_name = data.get("attachment_name")


    success, error = send_email_with_attachment(
        recipient["email"],
        subject,
        full_email,
        sender_info["email"],
        from_name,
        cc_email,
        attachment_path,
        attachment_name
    )


    if success:

        collection.update_one(
            {"_id": recipient["_id"]},
            {"$set": {
                "status": "sent",
                "sent_by": sender_key,
                "sender_email": sender_info["email"],
                "sender_name": from_name,
                "sent_at": datetime.now(),
                "cc_email": cc_email,
                "subject": subject,
                "email_body": full_email
            }}
        )

        return jsonify({
            "success": True,
            "message": "Email sent successfully"
        })


    else:

        collection.update_one(
            {"_id": recipient["_id"]},
            {"$set": {
                "status": "failed",
                "error": error
            }}
        )

        return jsonify({
            "success": False,
            "error": error
        }), 500

@app.route("/send_bulk_emails", methods=["POST"])
@login_required
def send_bulk_emails():
    # Bulk sending is disabled - single email flow only
    return jsonify({"message": "Bulk sending is disabled. Please use single email flow.", "results": []}), 200

def send_email_with_details(receiver_email, subject, body, from_email, from_name, cc_email=None):
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from send_email import EMAIL_ACCOUNTS, SMTP_SERVER, SMTP_PORT
    sender = EMAIL_ACCOUNTS.get(from_email, EMAIL_ACCOUNTS.get("dhrupal"))
    sender_email = sender["email"]
    sender_password = sender["password"]
    msg = MIMEMultipart()
    msg["From"] = from_name + " <" + sender_email + ">"
    msg["To"] = receiver_email
    msg["Subject"] = subject
    if cc_email:
        msg["CC"] = cc_email
    msg.attach(MIMEText(body, "plain"))
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(sender_email, sender_password)
        recipients = [receiver_email]
        if cc_email:
            recipients.append(cc_email)
        server.sendmail(sender_email, recipients, msg.as_string())
        server.quit()
        return True, None
    except Exception as e:
        return False, str(e)

@app.route("/status")
@login_required
def status():
    user_id = session.get("user_id")
    pending = collection.count_documents({"status": "pending", "user_id": user_id})
    sent = collection.count_documents({"status": "sent", "user_id": user_id})
    failed = collection.count_documents({"status": "failed", "user_id": user_id})
    total = collection.count_documents({"user_id": user_id})
    return jsonify({"pending": pending, "sent": sent, "failed": failed, "total": total})

@app.route("/clear_data", methods=["POST"])
@login_required
def clear_data():
    user_id = session.get("user_id")
    result = collection.delete_many({"user_id": user_id})
    return jsonify({"message": "Deleted " + str(result.deleted_count) + " records"})

@app.route("/update_last_sender", methods=["POST"])
@login_required
def update_last_sender():
    data = request.get_json()
    sender = data.get("sender")
    settings_collection.update_one({"user_id": session.get("user_id")}, {"$set": {"last_sender": sender}}, upsert=True)
    session["last_sender"] = sender
    return jsonify({"success": True})

if __name__ == "__main__":
    if not users_collection.find_one({"username": "admin"}):
        users_collection.insert_one({"username": "admin", "password": "admin123", "created_at": datetime.now()})
        print("Default user created: admin / admin123")
    app.run(debug=True, port=5003)