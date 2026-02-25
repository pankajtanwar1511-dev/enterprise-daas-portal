#!/bin/bash

# Test CREATE asset endpoint

# First login to get a fresh token
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=demo123")

TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "Got token: ${TOKEN:0:50}..."

# Now create asset
echo "Creating new asset..."
curl -s -X POST http://localhost:8000/api/v1/assets/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"asset_name":"QA-DATA-ETL-v1","domain_id":6,"environment":"QA","owner_id":3,"version":"v1.0","lifecycle_stage":"Active","documentation_url":"https://docs.company.com/data-etl","description":"Data platform ETL testing environment","business_justification":"QA testing for data platform ETL pipelines"}' | python3 -m json.tool
