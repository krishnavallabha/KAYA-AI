from agents.document_parser import DocumentParserAgent


def parse_procurement_document(file_text: str) -> dict:
    agent = DocumentParserAgent()
    event = agent.extract({"text": file_text})
    return event.to_dict()
