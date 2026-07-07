# use openai's multimodal vision features to analyze uploaded delivery photographs, label scans, or receipt images to verify deliveries, counts, and conditions 


import json 
import base64
from openai import OpenAI
from backend.config import settings 


def encode_image(image_bytes:bytes) -> str:
    return base64.b64encode(image_bytes).decode('utf-8')


def parse_delivery_image(image_bytes:bytes) -> dict:
    if not settings.OPENAI_API_KEY: # mock fallback 
        return {
            "sku": "SKU-482",
            "quantity_verified": 25.0,
            "status": "DELIVERED",
            "condition": "GOOD",
            "explanation": "Mocked vision parsing (no API key)"
        }
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    base64_image = encode_image(image_bytes)
    prompt = """
        Analyze this photo of a delivery, packing slip, or product label.
        Extract the following details as a strict JSON object:
        - sku: Material identifier/PO code
        - quantity_verified: Number of items/units verified
        - status: Reconciled status. Must be exactly one of: SHIPPED, DELIVERED
        - condition: Item state (e.g., GOOD, DAMAGED)
        - explanation: Detail what is visible in the photo
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        if content is None:
            raise ValueError("OpenAI response content was empty.")
        return json.loads(content)
    except Exception as e:
        return {
            "error": str(e),
            "status": "DELIVERED",
            "explanation": "Failed to parse image via Vision LLM."
        }        