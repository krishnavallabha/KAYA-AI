"""
FlowSense Role 2 - Config
Handles LLM client setup. Falls back to heuristic/regex extraction when
no OPENAI_API_KEY is present, so the whole pipeline runs standalone for
demo purposes and swaps to real GPT-4o calls the moment a key is set.
"""

import os

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
LIVE_MODE = bool(OPENAI_API_KEY)

EMAIL_MODEL = "gpt-4o"
VISION_MODEL = "gpt-4o"
DOC_MODEL = "gpt-4o"

_client = None


def get_openai_client():
    """Lazily construct an OpenAI client. Returns None in fallback mode."""
    global _client
    if not LIVE_MODE:
        return None
    if _client is None:
        from openai import OpenAI
        _client = OpenAI(api_key=OPENAI_API_KEY)
    return _client


def mode_banner():
    return (
        "[LIVE] Using GPT-4o for extraction" if LIVE_MODE
        else "[FALLBACK] No OPENAI_API_KEY set — using heuristic extraction. "
             "Set OPENAI_API_KEY to switch every agent to real GPT-4o calls "
             "with zero code changes."
    )
