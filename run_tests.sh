#!/bin/bash
# Exit immediately if a command exits with a non-zero status
set -e

# Load environment variables from .env if it exists
if [ -f .env ]; then
    # export lines that are not comments or empty
    export $(grep -v '^#' .env | xargs)
fi


echo "=========================================="
echo "Running FlowSense AI Backend Unit/Integration Tests"
echo "=========================================="

if [ -z "$OPENAI_API_KEY" ] && [ -z "$GROQ_API_KEY" ]; then
    echo -e "\033[1;33m⚠️  WARNING: Neither OPENAI_API_KEY nor GROQ_API_KEY is set.\033[0m"
    echo -e "\033[1;33m   All ML agents will run in OFFLINE/HEURISTIC fallback mode.\033[0m"
    echo "=========================================="
elif [ -n "$GROQ_API_KEY" ] && [ -z "$OPENAI_API_KEY" ]; then
    echo -e "\033[1;33m⚠️  NOTICE: No OPENAI_API_KEY found. Falling back to Groq Llama models.\033[0m"
    echo "=========================================="
else
    echo -e "\033[1;32m✅  OPENAI_API_KEY is configured. Running agents in LIVE OpenAI mode!\033[0m"
    echo "=========================================="
fi

# Run pytest with PYTHONPATH set to root workspace
PYTHONPATH=. ./venv/bin/pytest backend/tests/ "$@"

echo "All tests passed successfully! ✅"