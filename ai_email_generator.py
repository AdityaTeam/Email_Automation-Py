import requests
import time

OLLAMA_URL = "http://localhost:11434/api/generate"

MODELS = [
    "phi3:latest",
    "mistral:latest",
    "llama3:latest"
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

        payload = {
            "model": model,
            "prompt": prompt_text,
            "stream": False
        }

        for attempt in range(3):

            try:

                print(f"\nTrying Model: {model}")
                print(f"Attempt: {attempt + 1}")

                response = requests.post(
                    OLLAMA_URL,
                    json=payload,
                    timeout=180
                )

                print("Status Code:", response.status_code)

                response.raise_for_status()

                result = response.json()

                email_text = result.get("response", "").strip()

                if not email_text:
                    raise RuntimeError(
                        f"Empty response from {model}"
                    )

                print(f"Success with {model}")

                return f"{greeting}\n\n{email_text}"

            except requests.exceptions.ConnectionError as e:

                print(e)

                last_error = (
                    "Ollama server is not running "
                    "on localhost:11434"
                )

            except requests.exceptions.Timeout as e:

                print(e)

                last_error = (
                    f"{model} timed out"
                )

            except requests.exceptions.HTTPError as e:

                print(e)

                try:
                    print(response.text)
                except:
                    pass

                last_error = (
                    f"HTTP error from {model}"
                )

            except Exception as e:

                print(e)

                last_error = str(e)

            time.sleep(3)

        print(f"Failed model: {model}")

    raise RuntimeError(
        f"All models failed. Last error: {last_error}"
    )
