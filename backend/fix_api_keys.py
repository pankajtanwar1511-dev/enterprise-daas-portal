import json
from app.database import SessionLocal
from app.models_integrations import APIKey

db = SessionLocal()

# Get all API keys
keys = db.query(APIKey).all()

for key in keys:
    if isinstance(key.scopes, str):
        # Parse the JSON string to get actual list
        key.scopes = json.loads(key.scopes)
        print(f"Fixed key {key.key_id}: {key.key_name} - scopes: {key.scopes}")

db.commit()
db.close()
print("\nAll API keys fixed!")
