from flask import Flask, request, jsonify, render_template, redirect, url_for
from send_email import send_email
from ai_email_generator import generate_email
import pandas as pd
from pymongo import MongoClient
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['email_generator']
collection = db['emails']

# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    print("Upload endpoint called")

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and file.filename.endswith('.xlsx'):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        try:
            df = pd.read_excel(filepath)
            print("Excel read:", df.shape)

            df = pd.read_excel(filepath)

            # 🔥 CLEAN COLUMN NAMES
            df.columns = df.columns.str.strip().str.lower()

            emails = df.to_dict(orient='records')

            collection.delete_many({})
            collection.insert_many(emails)


            # 🔥 IMPORTANT FIX — clear old data first
            collection.delete_many({})

            # Insert only once
            collection.insert_many(emails)

            os.remove(filepath)

            return jsonify({
                'message': f'Successfully stored {len(emails)} records in database!'
            }), 200

        except Exception as e:
            print("Error:", e)
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Invalid file type'}), 400


@app.route('/send_bulk_emails', methods=['POST'])
def send_bulk_emails():

    # 🟢 sender selected from frontend
    sender_key = request.form.get('sender', 'company')

    emails = list(collection.find({}, {'_id': 0}))

    if not emails:
        return jsonify({'error': 'No data found in database'}), 400

    results = []

    for email_data in emails:
        ai_body = generate_email(email_data)

        success, error = send_email(
            email_data['email'],
            "AI Generated Email",
            ai_body,
            sender_key   # 🔥 selected sender
        )

        results.append({
            'email': email_data['email'],
            'success': success,
            'error': error
        })

    return jsonify({'results': results}), 200


@app.route('/send_email', methods=['POST'])
def send_email_endpoint():
    """
    Endpoint to send an email automatically.
    Expects JSON payload with 'receiver_email', optional 'subject' and 'body'.
    """
    data = request.get_json()
    if not data or 'receiver_email' not in data:
        return jsonify({'error': 'receiver_email is required'}), 400
    
    receiver_email = data['receiver_email']
    subject = data.get('subject', 'Automatic Email')
    body = data.get('body', 'Hello, this email was sent automatically using Python!')
    
    success, error = send_email(receiver_email, subject, body)
    if success:
        return jsonify({'message': 'Email sent successfully!'}), 200
    else:
        return jsonify({'error': f'Failed to send email: {error}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
