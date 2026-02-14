# api_key="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"  (hugging face)
# api_key="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" (openrouter)

import requests

API_KEY = "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"

def generate_email(data):

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
Write ONLY the final professional email.

Use these details inside the email where appropriate.

Name: {data.get('name')}
Email: {data.get('email')}
Phone: {data.get('phone')}
Company: {data.get('company')}
Requirement: {data.get('requirement')}

Do NOT include explanations.
Do NOT include placeholders.
Only return the final email ready to send.
"""

    data_json = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(url, headers=headers, json=data_json)

    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"]

    return "AI could not generate email."

