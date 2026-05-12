import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

MODELS = [
    "mistral:latest",
    "phi3:latest"
]


def generate_email(data, prompt_template=None):

    name = str(data.get("name", "") or "").strip()

    if not name or name.lower() in ["nan", "none"]:
        name = "Sir/Madam"

    greeting = f"Dear {name}"

    company = str(data.get("company", "") or "").strip()
    requirement_data = str(data.get("requirement", "") or "").strip()

    if prompt_template is None:

        prompt_template = """
You are writing the BODY of a professional B2B recruitment email.

IMPORTANT RULES:
- Do NOT write greeting
- Do NOT write subject
- Do NOT write signature
- Do NOT use bullet points
- Do NOT use markdown
- Write only professional email body

Context:
The sender is Hansraj Ventures Private Limited,
a recruitment and staffing company.

The email should:
- acknowledge hiring requirement
- explain staffing capability
- mention Contract / C2H / Full-time hiring
- mention screening process
- request short meeting
- mention attached company profile

Company: {company}

Requirement:
{requirement}

Write a complete professional email body.
"""

    prompt_text = prompt_template.format(
        company=company,
        requirement=requirement_data
    )

    last_error = None

    for model in MODELS:

        try:

            print(f"\nTrying Model: {model}")

            payload = {
                "model": model,
                "prompt": prompt_text,
                "stream": False,
                "options": {
                    "temperature": 0.15,
                    "top_p": 0.8,
                    "repeat_penalty": 1.05,
                    "num_predict": 120,
                    "num_ctx": 1024
                }
            }

            response = requests.post(
                OLLAMA_URL,
                json=payload,
                timeout=40
            )

            print("Status Code:", response.status_code)

            response.raise_for_status()

            result = response.json()

            email_text = result.get(
                "response", ""
            ).strip()

            if not email_text:
                raise RuntimeError(
                    f"Empty response from {model}"
                )

            if len(email_text.split()) < 40:
                raise RuntimeError(
                    f"Low quality response from {model}"
                )

            print(f"Success with {model}")

            return f"{greeting}\n\n{email_text}"

        except Exception as e:

            print(f"Failed model: {model}")
            print(e)

            last_error = str(e)

    raise RuntimeError(
        f"All models failed. Last error: {last_error}"
    )
