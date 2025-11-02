#!/bin/bash
# Clear all Python cache files

echo "🧹 Cleaning Python cache files..."

cd /home/kai/dev/retroNet/retronet

# Remove __pycache__ directories
echo "Removing __pycache__ directories..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Remove .pyc files
echo "Removing .pyc files..."
find . -name "*.pyc" -delete 2>/dev/null

# Remove .pyo files
echo "Removing .pyo files..."
find . -name "*.pyo" -delete 2>/dev/null

echo "✅ Cache cleared!"
echo ""
echo "Now check these files manually:"
echo "1. retroApp/__init__.py - look for 'endpoint=' or 'add_url_rule'"
echo "2. retroApp/landing.py - check function name"
echo "3. retroApp/templates/base.html - search for 'landing.'"
echo ""
echo "Run: grep -r 'landing\.index' retroApp/"
