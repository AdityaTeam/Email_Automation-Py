import pandas as pd
import pdfplumber
from docx import Document
import os

def extract_metadata(filepath):

    metadata = {
        "file_name": os.path.basename(filepath),
        "file_type": filepath.split(".")[-1]
    }

    if filepath.endswith((".xlsx", ".xls")):

        excel = pd.ExcelFile(filepath)

        metadata["sheet_names"] = excel.sheet_names

        df = pd.read_excel(filepath)

        metadata["columns"] = list(df.columns)

        metadata["record_count"] = len(df)

    elif filepath.endswith(".csv"):

        df = pd.read_csv(filepath)

        metadata["columns"] = list(df.columns)

        metadata["record_count"] = len(df)

    elif filepath.endswith(".pdf"):

        text = ""

        with pdfplumber.open(filepath) as pdf:

            for page in pdf.pages:

                if page.extract_text():
                    text += page.extract_text()

        metadata["content_preview"] = text[:1000]

    elif filepath.endswith(".docx"):

        doc = Document(filepath)

        text = "\n".join(
            [p.text for p in doc.paragraphs]
        )

        metadata["content_preview"] = text[:1000]

    return metadata