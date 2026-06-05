import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

REQUEST_TIMEOUT = 7200

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
You are an expert B2B recruitment communication writer.

TASK:
Write ONLY the BODY of a professional recruitment email.

STRICT OUTPUT RULES (must follow exactly):
- Do NOT write subject line
- Do NOT write greeting (no "Dear", "Hello")
- Do NOT write signature or closing name
- Do NOT use bullet points or numbered lists
- Do NOT use markdown, formatting, or headings
- Output must be plain text only
- Do NOT add explanations or extra text
- Write in proper short paragraphs (2–4 lines each max)

COMPANY CONTEXT:
Sender: Hansraj Ventures Private Limited
Industry: Recruitment and Staffing Services

EMAIL OBJECTIVE:
Write a highly relevant outreach email based on the given company and job requirement.

MUST NATURALLY INCLUDE (do NOT list them):
- Acknowledge the client's hiring requirement clearly
- Position Hansraj Ventures as a reliable staffing partner
- Mention hiring support for Contract staffing, Contract-to-Hire (C2H), and Full-time hiring
- Briefly describe screening, evaluation, and shortlisting capability
- Express interest in scheduling a short discussion or meeting
- Mention that the company profile is attached for reference

STYLE REQUIREMENTS:
- Professional, polished, and business-appropriate tone
- Concise and impactful (no filler sentences)
- Human-like writing style (avoid AI-sounding repetition)
- Confident but not aggressive or sales-heavy

INPUT VARIABLES:
Company Name: {company}
Job Requirement / Context: {requirement}

WRITE:
A single continuous email body tailored specifically to the company and requirement.
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
                "system": "You are a precise business email writer. Always complete the full email body in proper paragraphs. Never cut off mid-response.",
                "prompt": prompt_text,
                "stream": False,
                "options": {
                    "temperature": 0.15,
                    "top_p": 0.8,
                    "repeat_penalty": 1.05,
                    "num_predict": 600,
                    "num_ctx": 1024
                }
            }

            response = requests.post(
                OLLAMA_URL,
                json=payload,
                timeout=REQUEST_TIMEOUT
            )

            print("Status Code:", response.status_code)

            response.raise_for_status()

            result = response.json()

            email_text = result.get("response", "").strip()

            if not email_text:
                raise RuntimeError(f"Empty response from {model}")

            if len(email_text.split()) < 40:
                raise RuntimeError(f"Low quality response from {model}")

            print(f"Success with {model}")

            return f"{greeting}\n\n{email_text}"

        except Exception as e:

            print(f"Failed model: {model}")
            print(e)

            last_error = str(e)

    raise RuntimeError(
        f"All models failed. Last error: {last_error}"
    )
