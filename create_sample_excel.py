import pandas as pd

# Create sample data
data = {
    'email': ['user1@example.com', 'user2@example.com', 'user3@example.com'],
    'subject': ['Test Subject 1', 'Test Subject 2', 'Test Subject 3'],
    'body': ['Hello, this is test email 1.', 'Hello, this is test email 2.', 'Hello, this is test email 3.']
}

df = pd.DataFrame(data)
df.to_excel('sample_emails.xlsx', index=False)
print("Sample Excel file created: sample_emails.xlsx")
