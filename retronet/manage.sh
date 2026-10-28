#!/usr/bin/env bash
# Run Flask's command line for retroNet, from anywhere.
#   retronet/manage.sh create-invite            print one new invite code
#   retronet/manage.sh create-invite --count 5  print five
#   retronet/manage.sh init-db                  create any missing tables
#   retronet/manage.sh --help                   list every command
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(cd .. && pwd)"   # absolute path to the repo root (avoids a "../" sys.prefix warning)
exec "$ROOT"/bin/flask --app 'retroApp:create_retroNet()' "$@"
