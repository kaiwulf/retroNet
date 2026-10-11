#!/usr/bin/env bash
# Start retroNet on http://localhost:65000
# Usage: ./start.sh   (run from anywhere)
set -euo pipefail
cd "$(dirname "$0")"
exec ../bin/python run.py
