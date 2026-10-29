# generate draft vendor escalation emails or purchase order amendaments


from typing import cast
from openai import OpenAI
from backend.config import settings


def draft_vendor_escalation_email(
    vendor_name: str, 
    sku: str, 
    delay_days: int, 
    new_eta_str: str, 
    impacted_activities_names: list
) -> str:
    impact_list_str = ", ".join(impacted_activities_names)
    if not settings.OPENAI_API_KEY:
        return f"""

Subject: URGENT: Delivery Delay Escalation - SKU: {sku}

Dear {vendor_name} Delivery Management Team,

We are writing to urgently escalate a delayed shipment status for Item/PO: {sku}.

Our tracking indicators show that this shipment is currently running {delay_days} days behind schedule, with a revised forecast arrival date of {new_eta_str}.

This delay has a direct, cascading impact on our critical path construction operations, specifically delaying:
- {impact_list_str}

Please provide an immediate update confirming:
1. The exact current location and status of this order.
2. The guaranteed arrival date on-site.
3. Any expedited transport options available to mitigate this schedule impact.

We look forward to your prompt response.

Sincerely,
Project Management Office (PMO)
FlowSense Construction Operations

"""
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    prompt = f"""
        Draft a highly professional, firm, yet collaborative logistics escalation email.
        Sender: FlowSense Project Management Office
        Recipient: {vendor_name}
        Delayed Item: {sku}
        Delay duration: {delay_days} days
        New Expected Delivery Date: {new_eta_str}
        At-risk downstream construction activities: {impact_list_str}
        
        Ensure the email:
        - Clear Subject line containing 'URGENT' and the SKU number.
        - Mentions the specific construction delays the project will suffer if this material doesn't arrive.
        - Asks for immediate action, tracking verification, or expedited shipping options.
        - Maintains a professional tone suitable for senior vendor relationships.
        
        Return ONLY the raw email subject and body text.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a senior construction contracts and logistics manager."},
                {"role": "user", "content": prompt}
            ]
        )
        content = response.choices[0].message.content
        if content is None:
             raise ValueError("OpenAI response was empty.")
        return content
    except Exception as e:
        return f"Error drafting email via LLM: {str(e)}"
