from unittest import result

from distro import name
import requests
from sympy import re
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenRouter API Key from environment variable
API_KEY = os.getenv("OPENROUTER_API_KEY")


def generate_email(data, prompt_template=None):
    """
    Generate an email using OpenRouter AI API.
    
    Args:
        data: Dictionary containing recipient details (name, email, company, requirement)
        prompt_template: Optional custom prompt template. If not provided, uses default.
    
    Returns:
        Generated email body string
    """
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Extract data fields
    name = data.get('name', '')
    # Convert to string to avoid function objects
    if callable(name):
        name = ""

    name = str(name).strip()

    if not name or name.lower() in ["nan", "none"]:
        name = "Sir/Madam"
    greeting = f"Dear {name}"
    email_addr = data.get('email', '')
    company = data.get('company', '')
    requirement_data = data.get('requirement', '')
    
    # Use provided template or create default one
    if prompt_template is None:
        prompt_template = """ You are writing the BODY of a professional B2B recruitment email.

IMPORTANT RULES:
- Do NOT write the greeting.
- Do NOT write "Dear".
- Do NOT include "Best Regards" or signature.
- Do NOT include subject.
- Do NOT include headings, markdown, or bullet points.
- Do NOT add explanations.

Write only the email body in natural paragraph format.

Context:
The sender is Hansraj Ventures Private Limited, a recruitment and staffing company that provides skilled professionals.

The email should:
- Briefly acknowledge the hiring requirement
- Mention Hansraj Ventures staffing capability
- Mention hiring models (Contract / Contract-to-hire / Full-time)
- Mention candidate screening process
- Request a short meeting
- Mention company profile attachment

Company: {company}

Hiring Requirement:
{requirement}
"""
    
    # Format the prompt with actual data
    prompt_text = prompt_template.format(
        name=name,
        email=email_addr,
        company=company,
        requirement=requirement_data
    )
    
    data_json = {
        "model": "meta-llama/llama-3.1-8b-instruct",
        "messages": [
            {
                "role": "system",
                "content": "You are a professional business email writer who writes B2B recruitment proposal emails."
            },
            {
                "role": "user",
                "content": prompt_text
            }
        ],
        "max_tokens": 600
    }
    
    try:
        response = requests.post(url, headers=headers, json=data_json)
        
        if response.status_code == 200:
            result = response.json()
            email_text = result["choices"][0]["message"]["content"].strip()

            final_email = f"{greeting}\n\n{email_text}"

            return final_email
        else:
            print(f"Error generating email: {response.status_code} - {response.text}")
            return "Thank you for your interest in our services."
    
    except Exception as e:
        print(f"Exception in generate_email: {str(e)}")
        return "Thank you for your interest in our services."

