#!/usr/bin/env python3
"""
Export OpenAPI schema for Phase 1 API

This script generates the OpenAPI JSON schema for documentation
and integration purposes.
"""

import json
import os
import sys

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.main import app

def export_openapi_schema():
    """Export OpenAPI schema to JSON file"""
    
    # Get the OpenAPI schema
    openapi_schema = app.openapi()
    
    # Create openapi directory if it doesn't exist
    os.makedirs("openapi", exist_ok=True)
    
    # Write to file
    with open("openapi/contextual-search.yaml", "w", encoding="utf-8") as f:
        # Convert to YAML-like JSON (readable format)
        json.dump(openapi_schema, f, indent=2, ensure_ascii=False)
    
    print("✅ OpenAPI schema exported to openapi/contextual-search.yaml")
    print(f"📊 API has {len(openapi_schema.get('paths', {}))} endpoints")
    print(f"🏷️  API version: {openapi_schema.get('info', {}).get('version', 'unknown')}")
    
    # Print endpoint summary
    paths = openapi_schema.get('paths', {})
    print("\n📋 Available Endpoints:")
    for path, methods in paths.items():
        for method, details in methods.items():
            if method in ['get', 'post', 'put', 'delete']:
                summary = details.get('summary', 'No summary')
                print(f"  {method.upper():<6} {path:<30} - {summary}")

if __name__ == "__main__":
    export_openapi_schema()