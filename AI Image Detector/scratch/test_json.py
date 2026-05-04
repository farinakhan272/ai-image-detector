import json
try:
    print(json.dumps({"test": True}))
except TypeError as e:
    print(f"Error: {e}")
