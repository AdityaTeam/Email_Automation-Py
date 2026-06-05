import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"

VALID_CATEGORIES = {
    "Industry",
    "Doctor",
    "Play School",
    "General"
}


def build_prompt(metadata: dict) -> str:
    """
    Build classification prompt for Ollama Llama3.
    """

    return f"""
You are an enterprise data classification engine.

Your task is to classify uploaded files into EXACTLY ONE category.

The system supports ONLY these categories:

1. Industry
2. Doctor
3. Play School
4. General

Category Guidelines:

Industry:
- Manufacturing companies
- Factories
- Corporate businesses
- Vendors
- Sales records
- Finance records
- HR records
- Inventory
- Operations
- Employee data

Doctor:
- Hospitals
- Clinics
- Medical practices
- Patient records
- Healthcare providers
- Medical billing
- Doctors and nurses
- Healthcare administration

Play School:
- Preschools
- Kindergarten
- Play schools
- Child care centers
- Student records
- Teacher records
- Admissions
- Attendance
- Parent information

General:
- Uncategorized data
- Mixed datasets
- Unknown business type
- Unable to determine category

Return ONLY valid JSON.

Format:

{{
    "category": "",
    "data_type": "",
    "tags": []
}}

Rules:

1. category MUST be one of:
   - Industry
   - Doctor
   - Play School
   - General

2. data_type MUST be one of:
   - Structured
   - Semi-Structured
   - Unstructured

3. tags MUST contain 3 to 8 keywords

4. Do NOT return explanations.

5. Return JSON only.

Dataset Metadata:

{json.dumps(metadata, indent=2)}
"""


def classify_file(metadata: dict) -> dict:
    """
    Send metadata to Ollama and get classification.
    """

    try:

        prompt = build_prompt(metadata)

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            },
            timeout=120
        )

        response.raise_for_status()

        result = response.json()

        llm_output = result.get(
            "response",
            ""
        ).strip()

        return safe_parse(llm_output)

    except Exception as e:

        print(
            "CLASSIFICATION ERROR:",
            str(e)
        )

        return {
            "category": "General",
            "data_type": "Unknown",
            "tags": []
        }


def safe_parse(llm_output: str) -> dict:
    """
    Safely parse JSON returned by Ollama.
    """

    try:

        start = llm_output.find("{")
        end = llm_output.rfind("}")

        if start != -1 and end != -1:
            llm_output = llm_output[
                start:end + 1
            ]

        parsed = json.loads(
            llm_output
        )

        category = parsed.get(
            "category",
            "General"
        )

        if category not in VALID_CATEGORIES:
            category = "General"

        data_type = parsed.get(
            "data_type",
            "Unknown"
        )

        valid_types = [
            "Structured",
            "Semi-Structured",
            "Unstructured"
        ]

        if data_type not in valid_types:
            data_type = "Unknown"

        tags = parsed.get(
            "tags",
            []
        )

        if not isinstance(tags, list):
            tags = []

        tags = [
            str(tag).strip()
            for tag in tags
            if str(tag).strip()
        ]

        tags = tags[:8]

        return {
            "category": category,
            "data_type": data_type,
            "tags": tags
        }

    except Exception as e:

        print(
            "JSON PARSE ERROR:",
            str(e)
        )

        return {
            "category": "General",
            "data_type": "Unknown",
            "tags": []
        }


if __name__ == "__main__":

    sample_metadata = {

        "file_name":
            "hospital_patients.xlsx",

        "columns": [
            "Patient ID",
            "Doctor Name",
            "Diagnosis",
            "Treatment"
        ],

        "record_count":
            500,

        "content_preview":
            "Patient records, diagnosis reports, doctor consultation data"
    }

    result = classify_file(
        sample_metadata
    )

    print(
        json.dumps(
            result,
            indent=4
        )
    )