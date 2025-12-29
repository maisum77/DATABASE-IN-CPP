#!/usr/bin/env python3

# ============================================================================
# PROGRAM: quick_test.py
# PURPOSE: Quick test to verify dynamic schema fetching works
# ============================================================================

import requests

# Server URL
SERVER_URL = "http://localhost:8080"


def test_connection():
    """Test if server is running."""
    print("Testing connection to server...")
    try:
        response = requests.get(f"{SERVER_URL}/health", timeout=5)
        if response.status_code == 200:
            print("[OK] Server is running!")
            return True
        print("[FAIL] Server returned unexpected response")
        return False
    except Exception as error:
        print(f"[FAIL] Cannot connect to server: {error}")
        return False


def list_tables():
    """List all tables in the database."""
    print("\nListing tables...")
    try:
        response = requests.get(f"{SERVER_URL}/tables", timeout=5)
        if response.status_code == 200:
            tables = response.json()
            print(f"Tables: {tables}")
            return tables
        print(f"[FAIL] Error: {response.json().get('error', 'Unknown')}")
        return []
    except Exception as error:
        print(f"[FAIL] Error: {error}")
        return []


def get_table_schema(table_name):
    """Get schema for a specific table."""
    print(f"\nGetting schema for '{table_name}'...")
    try:
        response = requests.get(
            f"{SERVER_URL}/table/{table_name}/schema",
            timeout=5
        )
        if response.status_code == 200:
            schema = response.json()
            print(f"  Table: {schema.get('name')}")
            print(f"  Columns: {schema.get('columns')}")
            print(f"  Primary Key: {schema.get('primary_key')}")
            print(f"  Rows: {schema.get('row_count')}")
            return schema
        else:
            print(f"[FAIL] Table not found")
            return None
    except Exception as error:
        print(f"[FAIL] Error: {error}")
        return None


def create_table(table_name, columns, primary_key=None):
    """Create a new table."""
    print(f"\nCreating table '{table_name}'...")
    try:
        data = {
            "name": table_name,
            "columns": columns
        }
        if primary_key:
            data["primary_key"] = primary_key

        response = requests.post(
            f"{SERVER_URL}/table",
            json=data,
            timeout=5
        )
        if response.status_code == 200:
            print(f"[OK] Table '{table_name}' created!")
            return True
        else:
            print(f"[FAIL] {response.json().get('error', 'Unknown error')}")
            return False
    except Exception as error:
        print(f"[FAIL] Error: {error}")
        return False


def insert_data(table_name, rows):
    """Insert data into a table."""
    print(f"Inserting data into '{table_name}'...")
    try:
        data = {"rows": rows}
        response = requests.post(
            f"{SERVER_URL}/table/{table_name}/batch_insert",
            json=data,
            timeout=5
        )
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] Inserted {result.get('inserted', 0)} rows!")
            return True
        else:
            print(f"[FAIL] {response.json().get('error', 'Unknown error')}")
            return False
    except Exception as error:
        print(f"[FAIL] Error: {error}")
        return False


def run_query(table_name, column, operator, value):
    """Run a query on the server."""
    print(f"\nQuerying: SELECT * FROM {table_name} WHERE {column} {operator} {value}")
    try:
        data = {
            "table": table_name,
            "column": column,
            "operator": operator,
            "value": value
        }
        response = requests.post(
            f"{SERVER_URL}/query",
            json=data,
            timeout=5
        )
        if response.status_code == 200:
            results = response.json()
            print(f"Found {len(results) - 1} rows:")
            for row in results:
                print(f"  {row}")
            return results
        else:
            print(f"[FAIL] {response.json().get('error', 'Unknown error')}")
            return []
    except Exception as error:
        print(f"[FAIL] Error: {error}")
        return []


def main():
    """Run the quick test."""
    print("=" * 60)
    print("   Quick Dynamic Schema Test")
    print("=" * 60)

    # Step 1: Test connection
    if not test_connection():
        print("\nPlease start the C++ server first:")
        print("  ./main")
        return

    # Step 2: List existing tables
    tables = list_tables()

    # Step 3: Get schema for employees
    get_table_schema("employees")

    # Step 4: Create a new table
    print("\n" + "-" * 60)
    print("Creating a new table to test dynamic schema...")
    success = create_table(
        "test_products",
        ["id", "name", "price", "category"],
        "id"
    )

    if success:
        # Step 5: Insert data
        insert_data("test_products", [
            ["1", "Widget", "10.99", "General"],
            ["2", "Gadget", "25.99", "Electronics"],
            ["3", "Thingamajig", "15.99", "General"]
        ])

        # Step 6: List tables again (should include new table)
        print("\n" + "-" * 60)
        print("Listing tables after creating new table...")
        tables = list_tables()

        # Step 7: Get schema for new table
        get_table_schema("test_products")

        # Step 8: Run query on new table
        run_query("test_products", "price", ">", "15")

    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)
    print("\nThe new table 'test_products' is now in the database.")
    print("You can query it using the NLP client:")
    print("  python nlp_sql_client.py")
    print("  > Show all test_products")
    print("  > List test_products where price > 15")


if __name__ == "__main__":
    main()
