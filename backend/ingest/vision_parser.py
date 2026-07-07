import os
from agents.vision_agent import VisionAgent


def parse_delivery_image(image_bytes: bytes) -> dict:
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    temp_dir = os.path.join(os.path.dirname(backend_dir), "temp_uploads")
    os.makedirs(temp_dir, exist_ok=True)
    temp_file_path = os.path.join(temp_dir, "temp_upload.png")
    try:
        with open(temp_file_path, "wb") as f:
            f.write(image_bytes)
        agent = VisionAgent()
        event = agent.extract({"path": temp_file_path})
        return event.to_dict()
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)