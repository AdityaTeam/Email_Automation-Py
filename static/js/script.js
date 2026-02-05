document.getElementById('uploadForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    const messageDiv = document.getElementById('message');
    const sendBtn = document.getElementById('sendEmailsBtn');

    messageDiv.textContent = 'Uploading...';
    messageDiv.style.color = 'blue';

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            messageDiv.textContent = data.message;
            messageDiv.style.color = 'green';
            sendBtn.style.display = 'block';
        } else if (data.error) {
            messageDiv.textContent = data.error;
            messageDiv.style.color = 'red';
        }
    })
    .catch(error => {
        messageDiv.textContent = 'An error occurred: ' + error.message;
        messageDiv.style.color = 'red';
    });
});

document.getElementById('sendEmailsBtn').addEventListener('click', function() {
    const messageDiv = document.getElementById('message');
    messageDiv.textContent = 'Sending emails...';
    messageDiv.style.color = 'blue';

    fetch('/send_bulk_emails', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.results) {
            messageDiv.textContent = 'Emails sent. Check console for details.';
            messageDiv.style.color = 'green';
            console.log(data.results);
        } else if (data.error) {
            messageDiv.textContent = data.error;
            messageDiv.style.color = 'red';
        }
    })
    .catch(error => {
        messageDiv.textContent = 'An error occurred: ' + error.message;
        messageDiv.style.color = 'red';
    });
});
