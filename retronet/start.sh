#!/usr/bin/env bash
# Start retroNet on http://localhost:65000
# Usage: ./start.sh   (run from anywhere)
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(cd .. && pwd)"   # absolute path to the repo root (avoids a "../" sys.prefix warning)
exec "$ROOT"/bin/python run.py
