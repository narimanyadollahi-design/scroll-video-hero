#!/bin/bash
cd "$(dirname "$0")"
if command -v node >/dev/null 2>&1; then
  node server.js
elif command -v python3 >/dev/null 2>&1; then
  python3 server.py
else
  echo "Install Node.js (nodejs.org) or Python 3, then run this again."; read -p "Press Enter"
fi
