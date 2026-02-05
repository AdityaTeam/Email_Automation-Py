from flask import Flask, request, jsonify, render_template, redirect, url_for
from send_email import send_email
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
        print("No file part")
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        print("No selected file")
        return jsonify({'error': 'No selected file'}), 400
    if file and file.filename.endswith('.xlsx'):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        print(f"File saved to {filepath}")

        # Read Excel file
        try:
            df = pd.read_excel(filepath)
            print(f"Excel file read successfully. Shape: {df.shape}")
            print(f"Columns: {list(df.columns)}")
        except Exception as e:
            print(f"Error reading Excel file: {e}")
            os.remove(filepath)
            return jsonify({'error': f'Error reading Excel file: {str(e)}'}), 400

        # Assume columns: email, subject, body
        emails = []
        for _, row in df.iterrows():
            email_data = {
                'email': row.get('email'),
                'subject': row.get('subject', 'Automatic Email'),
                'body': row.get('body', 'Hello, this email was sent automatically using Python!')
            }
            emails.append(email_data)

        print(f"Prepared {len(emails)} emails for insertion")

        # Insert into MongoDB
        try:
            result = collection.insert_many(emails)
            print(f"Inserted {len(result.inserted_ids)} documents into MongoDB")
        except Exception as e:
            print(f"Error inserting into MongoDB: {e}")
            os.remove(filepath)
            return jsonify({'error': f'Error inserting into MongoDB: {str(e)}'}), 500

        # Clean up file
        os.remove(filepath)

        return jsonify({'message': f'Uploaded and stored {len(emails)} emails successfully!'}), 200
    else:
        print("Invalid file type")
        return jsonify({'error': 'Invalid file type. Please upload an Excel file (.xlsx)'}), 400

@app.route('/send_bulk_emails', methods=['POST'])
def send_bulk_emails():
    emails = list(collection.find({}, {'_id': 0}))
    if not emails:
        return jsonify({'error': 'No emails found in database'}), 400
    
    results = []
    for email_data in emails:
        success, error = send_email(email_data['email'], email_data['subject'], email_data['body'])
        results.append({
            'email': email_data['email'],
            'success': success,
            'error': error if not success else None
        })
    
    # Clear the collection after sending
    collection.delete_many({})
    
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
