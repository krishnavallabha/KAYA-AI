"""
FlowSense Role 2 - Config
Handles LLM client setup. Falls back to heuristic/regex extraction when
no OPENAI_API_KEY is present, so the whole pipeline runs standalone for
demo purposes and swaps to real GPT-4o calls the moment a key is set.
"""

import os
from dotenv import load_dotenv

# Load environment variables from local .env file
load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

LIVE_MODE = bool(OPENAI_API_KEY or GROQ_API_KEY)
USING_GROQ = bool(GROQ_API_KEY and not OPENAI_API_KEY)

if USING_GROQ:
    EMAIL_MODEL = "llama-3.3-70b-versatile"
    VISION_MODEL = "llama-3.2-11b-vision-preview"
    DOC_MODEL = "llama-3.3-70b-versatile"
else:
    EMAIL_MODEL = "gpt-4o"
    VISION_MODEL = "gpt-4o"
    DOC_MODEL = "gpt-4o"

_client = None


def get_openai_client():
    """Lazily construct an OpenAI or Groq client. Returns None in fallback mode."""
    global _client
    if not LIVE_MODE:
        return None
    if _client is None:
        from openai import OpenAI
        if USING_GROQ:
            _client = OpenAI(
                api_key=GROQ_API_KEY,
                base_url="https://api.groq.com/openai/v1"
            )
        else:
            _client = OpenAI(api_key=OPENAI_API_KEY)
    return _client


def mode_banner():
    if USING_GROQ:
        return f"[LIVE] No OPENAI_API_KEY found. Falling back to Groq ({EMAIL_MODEL}) Llama models."
    return (
        f"[LIVE] Using GPT-4o ({EMAIL_MODEL}) for extraction" if LIVE_MODE
        else "[FALLBACK] No API key set — using heuristic extraction. "
             "Set OPENAI_API_KEY or GROQ_API_KEY to switch every agent to real LLM calls."
    )
