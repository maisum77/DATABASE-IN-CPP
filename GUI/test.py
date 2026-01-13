#!/usr/bin/env python3
"""
Simple CSV Import Test - Creates CSV and tests import
"""

import requests
import os

print("=" * 70)
print("CSV Import Test")
print("=" * 70)

# Step 1: Create CSV file
print("\n[1] Creating test CSV file...")
csv_content = """id,name,email,age
1,Alice Johnson,alice@example.com,28
2,Bob Smith,bob@example.com,35
3,Carol White,carol@example.com,42"""

csv_filename = 'test_users.csv'

with open(csv_filename, 'w') as f:
    f.write(csv_content)

print(f"✓ Created {csv_filename}")
print(f"  Location: {os.path.abspath(csv_filename)}")

# Step 2: Check server
print("\n[2] Checking server...")
try:
    r = requests.get('http://localhost:8080/api/health', timeout=3)
    print(f"✓ Server is running (status {r.status_code})")
except Exception as e:
    print(f"✗ Server not running: {e}")
    print("\nStart server first:")
    print("  python server.py")
    exit(1)

# Step 3: Upload CSV
print("\n[3] Uploading CSV...")
table_name = 'test_users'

with open(csv_filename, 'rb') as f:
    files = {'file': (csv_filename, f, 'text/csv')}
    response = requests.post(
        f'http://localhost:8080/api/tables/{table_name}/import',
        files=files,
        timeout=30
    )

print(f"  Status: {response.status_code}")

if response.status_code in [200, 201]:
    print("✓ SUCCESS! CSV imported")
    try:
        data = response.json()
        print(f"  Rows: {data.get('row_count', 'unknown')}")
        print(f"  Columns: {data.get('columns', [])}")
    except:
        pass
    
    # Verify
    print("\n[4] Verifying data...")
    r = requests.get(f'http://localhost:8080/api/tables/{table_name}/data')
    if r.status_code == 200:
        data = r.json()
        print(f"✓ Table has {len(data['rows'])} rows")
        print("\n  Sample data:")
        for row in data['rows'][:2]:
            print(f"    {row}")
else:
    print(f"✗ FAILED")
    print(f"  Response: {response.text}")

print("\n" + "=" * 70)
print("Test complete!")
print("=" * 70)