import requests

# URL of the Flask app endpoint
url = 'http://localhost:5000/send_email'

# JSON data for the POST request
data = {
    'receiver_email': 'write2smitapatel@gmail.com',  
    'subject': 'Test Email',
    'body': 'This is a test email sent automatically via Flask.'
}

# Send the POST request
response = requests.post(url, json=data)

# Print the response
print(f'Status Code: {response.status_code}')
print(f'Response: {response.json()}')
