# extract structured data pt from complex procurement logs, bulls of lading, submittal pdfs


import json
from openai import OpenAI 
from backend.config import settings


def parse_procurement_document(file_text: str) -> dict:
    if not settings.OPENAI_API_KEY:
        return {
            "sku": "SKU-STEEL-99",
            "vendor": "SteelCorp Ltd",
            "quantity": 100.0,
            "promised_delivery_date": "2026-07-28",
            "explanation": "Mocked document parse."
        }
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    prompt = f"""
        Analyze this text content parsed from a Bill of Lading, submittal, or procurement document.
        Extract the key data fields in a strict JSON format:
        - sku: Item code/SKU
        - vendor: Supplier/Manufacturer name
        - quantity: Total items ordered
        - promised_delivery_date: Date promised by vendor (YYYY-MM-DD), if any
        - explanation: Brief notes
        
        Document text:
        ---
        {file_text}
        ---
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a database intake parser. Output strict JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        if content is None:
            raise ValueError("OpenAI response content was empty.")
        return json.loads(content)
    except Exception as e:
        return {"error": str(e), "explanation": "Failed parsing document."}
