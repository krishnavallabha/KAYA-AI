from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from backend.config import settings
from backend.rag.config import CHAT_MODEL


def draft_vendor_escalation_email(
    vendor_name: str,
    sku: str,
    delay_days: int,
    new_eta_str: str,
    impacted_activities_names: list,
) -> str:
    impact_list_str = ", ".join(impacted_activities_names)

    fallback = f"""Subject: URGENT: Delivery Delay Escalation - SKU: {sku}

Dear {vendor_name} Delivery Management Team,

We are writing to urgently escalate a delayed shipment for Item/PO: {sku}.

Our tracking indicators show that this shipment is {delay_days} days behind schedule, with a revised expected arrival date of {new_eta_str}.

This delay directly impacts the following construction activities:
- {impact_list_str}

Please provide an immediate update confirming:
1. The current location and status of this order.
2. The guaranteed arrival date on-site.
3. Any expedited transport options available.

We look forward to your prompt response.

Sincerely,
Project Management Office (PMO)
FlowSense Construction Operations
"""

    if not settings.GROQ_API_KEY:
        return fallback

    prompt = f"""Draft a professional, firm, collaborative logistics escalation email.

Sender: FlowSense Project Management Office
Recipient: {vendor_name}
Delayed item: {sku}
Delay: {delay_days} days
Expected delivery date: {new_eta_str}
Impacted construction activities: {impact_list_str}

Include a subject line containing URGENT and the SKU.
Request immediate status verification and expedited shipping options.
Return only the email subject and body.
"""

    try:
        llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=CHAT_MODEL,
            temperature=0.2,
        )
        response = llm.invoke([
            SystemMessage(
                content="You are a senior construction contracts and logistics manager."
            ),
            HumanMessage(content=prompt),
        ])

        content = response.content
        if isinstance(content, str) and content.strip():
            return content.strip()

        return fallback

    except Exception:
        return fallback
