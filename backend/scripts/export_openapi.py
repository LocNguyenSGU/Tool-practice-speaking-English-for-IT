import sys
import os
import json
from pathlib import Path

# Add backend directory to path so we can import app
sys.path.append(str(Path(__file__).parent.parent))

try:
    from app.main import app
except ImportError as e:
    print(f"Error importing app: {e}")
    sys.exit(1)

def export_openapi():
    print("Extracting OpenAPI schema from FastAPI app...")
    openapi_schema = app.openapi()
    
    # Save to file in the current directory (which will be backend/)
    output_path = Path("openapi.json")
    with open(output_path, "w") as f:
        json.dump(openapi_schema, f, indent=2)
    print(f"✅ OpenAPI schema exported to {output_path.absolute()}")

if __name__ == "__main__":
    export_openapi()
