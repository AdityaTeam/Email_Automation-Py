import requests

def generate_email(data, prompt_template=None):
    name = str(data.get("name", "") or "").strip()
    if not name or name.lower() in ["nan", "none"]:
        name = "Sir/Madam"
    greeting = f"Dear {name}"

    email_addr = data.get("email", "")
    company = data.get("company", "")
    requirement_data = data.get("requirement", "")

    if prompt_template is None:
        prompt_template = """You are writing the BODY of a professional B2B recruitment email.

IMPORTANT RULES:
- Do NOT write the greeting.
- Do NOT write "Dear".
- Do NOT include "Best Regards" or signature.
- Do NOT include subject.
- Do NOT include headings, markdown, or bullet points.
- Do NOT add explanations.

STRICTLY follow all rules. Do not break format under any condition.

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

Write a complete, natural-sounding email body. Do not leave it empty.
"""

    prompt_text = prompt_template.format(
        company=company,
        requirement=requirement_data,
    )

    url = "http://localhost:11434/api/generate"

    models = ["mistral:latest", "phi3:latest", "llama3:latest"]

    last_error = None

    for model in models:
        payload = {
            "model": model,
            "prompt": prompt_text,
            "stream": False
        }

        try:
            for attempt in range(2):
                try:
                    print(f"Trying model: {model}, Attempt: {attempt+1}")

                    response = requests.post(url, json=payload, timeout=90)

                    print("Status Code:", response.status_code)
                    print("Raw Response:", response.text)

                    response.raise_for_status()
                    result = response.json()

                    email_text = result.get("response", "").strip()

                    if email_text:
                        return f"{greeting}\n\n{email_text}"
                    else:
                        raise RuntimeError("Empty response from Ollama")

                except requests.exceptions.RequestException as e:
                    print(f"Retry error ({model}):", e)
                    last_error = e
                    continue

        except Exception as e:
            print(f"Model failed: {model}, Error:", e)
            last_error = e
            continue

    raise RuntimeError(f"Error generating email: {str(last_error)}")