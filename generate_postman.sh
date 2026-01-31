#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting Postman Collection Generation..."

# Step 1: Export OpenAPI JSON from FastAPI
echo "1️⃣  Exporting OpenAPI schema..."
cd backend
# Check if venv exists and use it if possible, otherwise use python3
if [ -d "venv" ]; then
    source venv/bin/activate
fi
python3 scripts/export_openapi.py
cd ..

# Step 2: Convert OpenAPI to Postman Collection using npx
echo "2️⃣  Converting to Postman Collection..."

# Ensure destination directory exists
mkdir -p postman/collections

# Use npx to run openapi-to-postmanv2
# -s: source file
# -o: output file
# -p: pretty print
# -O: options (folderStrategy=Tags makes it organize by tags like 'Auth', 'Lessons')
npx -y openapi-to-postmanv2 \
    -s backend/openapi.json \
    -o "postman/collections/Vi-En Reflex Trainer API (Auto-Generated).postman_collection.json" \
    -p \
    -O folderStrategy=Tags,includeAuthInfo=true,requestParametersResolution=Example,enableOptionalParameters=false

echo "🎉 Success! New Postman collection generated at:"
echo "   postman/collections/Vi-En Reflex Trainer API (Auto-Generated).postman_collection.json"
echo ""
echo "👉 You can now import this file into Postman."
