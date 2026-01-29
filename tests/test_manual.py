#!/usr/bin/env python3
"""
Manual test script to parse the credit report PDF and validate against schema.
"""

import json
import jsonschema
from pathlib import Path
from fastapi.testclient import TestClient
from src.main import app

def main():
    """Run manual test of PDF parsing."""
    client = TestClient(app)
    
    # Path to test files
    pdf_path = Path("tests/test_files/credit-report.pdf")
    schema_path = Path("tests/test_files/expected-output.json")
    
    print("=" * 80)
    print("TransUnion PDF to JSON - Manual Test")
    print("=" * 80)
    print(f"\nPDF File: {pdf_path}")
    print(f"Schema File: {schema_path}")
    
    # Parse the PDF
    print("\n[1] Parsing PDF...")
    with open(pdf_path, "rb") as f:
        files = {"file": ("credit-report.pdf", f, "application/pdf")}
        response = client.post("/v1/parse", files=files)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Error: {response.json()}")
        return
    
    # Get parsed data
    parsed_data = response.json()
    
    # Load schema
    print("\n[2] Loading JSON Schema...")
    with open(schema_path, "r") as f:
        schema = json.load(f)
    
    # Validate against schema
    print("\n[3] Validating against schema...")
    try:
        jsonschema.validate(instance=parsed_data, schema=schema)
        print("✅ Validation PASSED - Output matches schema!")
    except jsonschema.ValidationError as e:
        print(f"❌ Validation FAILED: {e.message}")
        print(f"Failed at: {' -> '.join(str(p) for p in e.path)}")
        return
    
    # Display parsed data
    print("\n[4] Parsed Data Preview:")
    print("-" * 80)
    print(json.dumps(parsed_data, indent=2, ensure_ascii=False))
    
    # Summary
    print("\n" + "=" * 80)
    print("Summary:")
    print("=" * 80)
    print(f"✅ PDF parsed successfully")
    print(f"✅ Schema validation passed")
    print(f"✅ PII scrubbing applied: {check_pii_scrubbing(parsed_data)}")
    print(f"\nData structure:")
    print(f"  - Inquirer: {parsed_data.get('inquirer', {}).get('suscriptor', 'N/A')}")
    print(f"  - Personal Data: {len(parsed_data.get('personal_data', {}))} fields")
    print(f"  - Score: {parsed_data.get('score', {}).get('score', 'N/A')}")
    print(f"  - Open Accounts Summary: {len(parsed_data.get('summary_open_accounts', []))} entries")
    print(f"  - Open Accounts Details: {len(parsed_data.get('details_open_accounts', []))} entries")
    print("=" * 80)

def check_pii_scrubbing(data):
    """Check if PII scrubbing was applied."""
    personal_data = data.get("personal_data", {})
    
    # Check cedula/identification
    cedula = personal_data.get("cedula", "")
    if "X" in cedula or "*" in cedula:
        return "Yes (cedula masked)"
    
    identification = personal_data.get("identification", "")
    if "X" in identification or "*" in identification:
        return "Yes (identification masked)"
    
    return "Unknown"

if __name__ == "__main__":
    main()
