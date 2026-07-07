#!/bin/bash

set -e

echo "Running FlowSense AI Backend Unit/Integration Tests"

PYTHONPATH=. ./venv/bin/pytest backend/tests/ "$@"

echo "All tests passed successfully! ✅"