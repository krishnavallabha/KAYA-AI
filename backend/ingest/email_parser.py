from datetime import datetime, timezone
from agents.email_agent import EmailAgent


def parse_vendor_email(email_text: str) -> dict:
    agent = EmailAgent()
    received_at_str = datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
    event = agent.extract({"body": email_text, "received_at": received_at_str})
    return event.to_dict()