# use openai chat completion to parse unstructured email text and extract key fields in a json schema


import json 
from openai import OpenAI
from backend.config import settings 


def parse_vendor_email(email_text:str) -> dict:
    if not settings.OPENAI_API_KEY: # mock fallback
        return {
            "sku": "SKU-UNKNOWN",
            "status": "IN_TRANSIT",
            "current_location": "En route from factory",
            "estimated_delivery_date": "2026-07-20T00:00:00",
            "confidence_weight": 0.8,
            "explanation": "Mocked response (no OpenAI API Key provided)"
        }
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    prompt = f"""
        Analyze the following email from a construction supply chain vendor. 
        Extract the following information in strict JSON format:
        - sku: The identifier of the material (e.g. SKU-482 or PO number)
        - status: Reconciled status. Must be exactly one of: ORDERED, FABRICATING, SHIPPED, IN_TRANSIT, DELIVERED
        - current_location: Mentioned location of the shipment (e.g. Pune, Port, Hub)
        - estimated_delivery_date: ISO 8601 date string if mentioned, else null
        - confidence_weight: Assessment of signal reliability (0.0 to 1.0)
        - explanation: Brief summary of the reasoning
        
        Email content:
        ---
        {email_text}
        ---
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert logistics coordinator. Return ONLY strict JSON."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={
                "type":"json_object"
            }
        )
        content = response.choices[0].message.content
        if content is None:
            raise ValueError("OpenAI response content was empty.")
        return json.loads(content) 
    except Exception as e:
        return {
            "error": str(e),
            "status": "ORDERED",
            "explanation": "Failed to parse email using LLM."
        }