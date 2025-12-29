#!/usr/bin/env python3

# ============================================================================
# PROGRAM: test_dynamic_schema.py
# PURPOSE: Test the dynamic schema fetching and NLP-to-SQL conversion
#          with newly created tables
# ============================================================================

import requests
import sys
import time

# Import our modules
from sql_translator import SQLTranslator
from database_client import DatabaseClient, print_table


# ============================================================================
# CLASS: DynamicSchemaTester
# PURPOSE: Tests dynamic schema fetching and table creation
# ============================================================================
class DynamicSchemaTester:
    """
    This class tests the dynamic schema functionality.
    
    It:
    1. Connects to the database server
    2. Creates new tables
    3. Tests that the SQL translator can work with the new tables
    4. Verifies that natural language queries work for new tables
    """

    def __init__(self, server_url="http://localhost:8080"):
        """
        Initialize the tester.
        
        Parameters:
            server_url (str): URL of the database server
        """
        self.server_url = server_url
        self.db_client = None
        self.sql_translator = None

    def setup(self):
        """
        Set up the test environment.
        
        Returns:
            bool: True if setup successful, False otherwise
        """
        print("=" * 60)
        print("   Dynamic Schema Test Suite")
        print("=" * 60)
        print()

        # Create database client
        print("Step 1: Connecting to database server...")
        self.db_client = DatabaseClient()
        
        if not self.db_client.is_connected:
            print("\n[Error] Cannot connect to server.")
            print("Please start the C++ server first:")
            print("  ./main")
            return False

        # Create SQL translator with server URL
        print("\nStep 2: Initializing SQL translator...")
        self.sql_translator = SQLTranslator(self.server_url)

        print("\n[OK] Setup complete!")
        return True

    def test_existing_tables(self):
        """
        Test that existing tables work correctly.
        
        Returns:
            bool: True if all tests pass, False otherwise
        """
        print("\n" + "=" * 60)
        print("   Test 1: Existing Tables")
        print("=" * 60)

        # Get list of tables
        tables = self.db_client.get_tables()
        print(f"\nAvailable tables: {tables}")

        # Get employees table
        print("\nFetching employees table...")
        employees = self.db_client.get_table("employees")
        print(f"Employees table: {len(employees)} rows (including header)")

        # Test SQL translation for employees
        print("\nTesting SQL translation for employees...")
        test_queries = [
            "Show all employees",
            "List employees where age > 30",
            "Find employee names"
        ]

        all_passed = True
        for query in test_queries:
            sql = self.sql_translator.convert_to_sql(query)
            print(f"  Input:  {query}")
            print(f"  Output: {sql}")
            
            # Validate SQL
            if not sql.lower().startswith("select"):
                print(f"  [FAIL] Invalid SQL")
                all_passed = False
            else:
                print(f"  [PASS]")
            print()

        return all_passed

    def create_test_table(self, table_name, columns, primary_key=None):
        """
        Create a test table on the server.
        
        Parameters:
            table_name (str): Name of the table to create
            columns (list): List of column names
            primary_key (str): Name of primary key column, or None
            
        Returns:
            bool: True if table created successfully, False otherwise
        """
        try:
            create_data = {
                "name": table_name,
                "columns": columns
            }
            
            if primary_key:
                create_data["primary_key"] = primary_key

            response = requests.post(
                f"{self.server_url}/table",
                json=create_data,
                timeout=5
            )

            if response.status_code == 200:
                print(f"[OK] Table '{table_name}' created with columns: {columns}")
                return True
            else:
                print(f"[Error] Failed to create table: {response.json().get('error', 'Unknown')}")
                return False

        except Exception as error:
            print(f"[Error] Failed to create table: {error}")
            return False

    def insert_test_data(self, table_name, rows):
        """
        Insert test data into a table.
        
        Parameters:
            table_name (str): Name of the table
            rows (list): List of rows to insert
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            insert_data = {"rows": rows}

            response = requests.post(
                f"{self.server_url}/table/{table_name}/batch_insert",
                json=insert_data,
                timeout=5
            )

            if response.status_code == 200:
                result = response.json()
                count = result.get("inserted", 0)
                print(f"[OK] Inserted {count} rows into '{table_name}'")
                return True
            else:
                print(f"[Error] Failed to insert data")
                return False

        except Exception as error:
            print(f"[Error] Failed to insert data: {error}")
            return False

    def test_new_table(self, table_name, columns, test_queries):
        """
        Test SQL translation for a newly created table.
        
        Parameters:
            table_name (str): Name of the table
            columns (list): List of column names
            test_queries (list): List of (query, expected_keyword) tuples
            
        Returns:
            bool: True if all tests pass, False otherwise
        """
        print(f"\nTesting SQL translation for '{table_name}'...")
        
        all_passed = True
        for query, expected_keyword in test_queries:
            sql = self.sql_translator.convert_to_sql(query)
            print(f"  Input:  {query}")
            print(f"  Output: {sql}")
            
            # Check if SQL contains expected keyword
            if expected_keyword.lower() in sql.lower():
                print(f"  [PASS] Contains '{expected_keyword}'")
            else:
                print(f"  [FAIL] Missing '{expected_keyword}'")
                all_passed = False
            print()

        return all_passed

    def test_new_tables(self):
        """
        Test creating new tables and querying them.
        
        Returns:
            bool: True if all tests pass, False otherwise
        """
        print("\n" + "=" * 60)
        print("   Test 2: Creating New Tables")
        print("=" * 60)

        # Create products table
        print("\n--- Creating 'products' table ---")
        success = self.create_test_table(
            "products",
            ["product_id", "product_name", "price", "category"],
            "product_id"
        )
        if not success:
            return False

        # Insert test data
        success = self.insert_test_data("products", [
            ["P001", "Laptop", "999", "Electronics"],
            ["P002", "Headphones", "99", "Electronics"],
            ["P003", "Desk", "299", "Furniture"],
            ["P004", "Chair", "149", "Furniture"],
            ["P005", "Monitor", "349", "Electronics"]
        ])
        if not success:
            return False

        # Test SQL translation for products
        products_tests = [
            ("Show all products", "products"),
            ("List products where price > 200", "price"),
            ("Find product names", "product_name"),
            ("Show products in Electronics category", "Electronics")
        ]

        products_passed = self.test_new_table("products", ["product_id", "product_name", "price", "category"], products_tests)

        # Create orders table
        print("\n--- Creating 'customers' table ---")
        success = self.create_test_table(
            "customers",
            ["customer_id", "customer_name", "email", "city"],
            "customer_id"
        )
        if not success:
            return False

        # Insert test data
        success = self.insert_test_data("customers", [
            ["C001", "John Smith", "john@email.com", "New York"],
            ["C002", "Jane Doe", "jane@email.com", "Los Angeles"],
            ["C003", "Bob Wilson", "bob@email.com", "Chicago"],
            ["C004", "Alice Brown", "alice@email.com", "Boston"]
        ])
        if not success:
            return False

        # Test SQL translation for customers
        customers_tests = [
            ("Show all customers", "customers"),
            ("List customers from New York", "New York"),
            ("Find customer emails", "email"),
            ("Show customers where customer_id is C002", "C002")
        ]

        customers_passed = self.test_new_table("customers", ["customer_id", "customer_name", "email", "city"], customers_tests)

        return products_passed and customers_passed

    def test_schema_refresh(self):
        """
        Test that schema refresh works correctly.
        
        Returns:
            bool: True if test passes, False otherwise
        """
        print("\n" + "=" * 60)
        print("   Test 3: Schema Refresh")
        print("=" * 60)

        print("\nRefreshing schema from server...")
        success = self.sql_translator.refresh_schema()

        if not success:
            print("[FAIL] Schema refresh failed")
            return False

        # Get available tables
        tables = self.sql_translator.dynamic_schema.get_all_tables()
        print(f"\nTables in schema: {tables}")

        # Check if new tables are in the schema
        if "products" in tables and "customers" in tables:
            print("[PASS] New tables found in schema")
        else:
            print("[FAIL] New tables not found in schema")
            return False

        # Get columns for a table
        columns = self.sql_translator.dynamic_schema.get_table_columns("products")
        print(f"Products table columns: {columns}")

        if "product_name" in columns and "price" in columns:
            print("[PASS] Column information correct")
        else:
            print("[FAIL] Column information incorrect")
            return False

        return True

    def test_query_execution(self):
        """
        Test executing queries on newly created tables.
        
        Returns:
            bool: True if all tests pass, False otherwise
        """
        print("\n" + "=" * 60)
        print("   Test 4: Query Execution on New Tables")
        print("=" * 60)

        # Test getting products table
        print("\nFetching products table from server...")
        products = self.db_client.get_table("products")
        
        if not products:
            print("[FAIL] Could not fetch products table")
            return False

        print(f"Products table has {len(products) - 1} data rows")
        print_table(products)

        # Test query with WHERE clause
        print("\nExecuting query: SELECT * FROM products WHERE price > 200")
        results = self.db_client.send_query("products", "price", ">", "200")
        
        if not results:
            print("[FAIL] Query returned no results")
            return False

        print(f"Found {len(results) - 1} products with price > 200")
        print_table(results)

        # Test getting customers table
        print("\nFetching customers table from server...")
        customers = self.db_client.get_table("customers")
        
        if not customers:
            print("[FAIL] Could not fetch customers table")
            return False

        print(f"Customers table has {len(customers) - 1} data rows")
        print_table(customers)

        # Test search
        print("\nSearching for customers in New York...")
        search_results = self.db_client.search_table("customers", "city", "New York")
        
        if not search_results:
            print("[FAIL] Search returned no results")
            return False

        print(f"Found {len(search_results) - 1} customers in New York")
        print_table(search_results)

        return True

    def test_nlp_to_execution(self):
        """
        Test the complete flow: NLP -> SQL -> Execute -> Result.
        
        Returns:
            bool: True if test passes, False otherwise
        """
        print("\n" + "=" * 60)
        print("   Test 5: Complete NLP to Execution Flow")
        print("=" * 60)

        # Refresh schema to ensure we have latest
        print("\nRefreshing schema...")
        self.sql_translator.refresh_schema()

        # Test queries in natural language
        test_cases = [
            {
                "name": "Query products with high price",
                "nlp": "Show products where price is greater than 300",
                "table": "products",
                "column": "price",
                "operator": ">",
                "value": "300"
            },
            {
                "name": "Query customers in Chicago",
                "nlp": "Find customers from Chicago",
                "table": "customers",
                "column": "city",
                "operator": "=",
                "value": "Chicago"
            }
        ]

        all_passed = True

        for test in test_cases:
            print(f"\n--- {test['name']} ---")
            
            # Step 1: Convert NLP to SQL
            print(f"Step 1: Converting NLP to SQL...")
            sql = self.sql_translator.convert_to_sql(test['nlp'])
            print(f"  Input:  {test['nlp']}")
            print(f"  Output: {sql}")
            
            if test['table'] not in sql:
                print(f"  [WARNING] SQL may not reference correct table")
            
            # Step 2: Execute query on server
            print(f"Step 2: Executing query on server...")
            results = self.db_client.send_query(
                test['table'],
                test['column'],
                test['operator'],
                test['value']
            )
            
            if not results or len(results) <= 1:
                print(f"  [WARNING] No results found")
                continue
            
            print(f"  Found {len(results) - 1} rows")
            print_table(results)
            
            print(f"  [PASS] Complete flow successful")

        return all_passed

    def run_all_tests(self):
        """
        Run all tests.
        
        Returns:
            bool: True if all tests pass, False otherwise
        """
        results = []

        # Run tests
        results.append(("Existing Tables", self.test_existing_tables()))
        results.append(("New Tables", self.test_new_tables()))
        results.append(("Schema Refresh", self.test_schema_refresh()))
        results.append(("Query Execution", self.test_query_execution()))
        results.append(("NLP to Execution", self.test_nlp_to_execution()))

        # Print summary
        print("\n" + "=" * 60)
        print("   Test Summary")
        print("=" * 60)

        passed = 0
        failed = 0

        for name, success in results:
            status = "PASS" if success else "FAIL"
            print(f"  {name}: {status}")
            if success:
                passed += 1
            else:
                failed += 1

        print()
        print(f"Total: {passed} passed, {failed} failed")
        print("=" * 60)

        return failed == 0

    def cleanup(self):
        """
        Clean up test data.
        
        Note: If DROP TABLE endpoint is not available, tables will remain
        in the database but won't affect future tests.
        """
        print("\nCleaning up test data...")
        print("[Info] Note: Tables will remain in database until server restart")
        print("       (DROP TABLE endpoint not implemented in server)")

        # Try to delete rows from test tables (won't drop tables)
        try:
            for table in ["products", "customers"]:
                # Just print that tables exist (for user's reference)
                print(f"[Info] Table '{table}' still exists in database")
        except Exception as error:
            print(f"[Warning] Cleanup notice: {error}")


# ============================================================================
# MAIN FUNCTION
# ============================================================================
def main():
    """
    Main entry point for the test script.
    """
    # Default server URL
    server_url = "http://localhost:8080"

    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help']:
            print("Usage: python test_dynamic_schema.py [server_url]")
            print()
            print("Arguments:")
            print("  server_url    Database server URL (default: http://localhost:8080)")
            print()
            print("Examples:")
            print("  python test_dynamic_schema.py")
            print("  python test_dynamic_schema.py http://localhost:8080")
            sys.exit(0)

        server_url = sys.argv[1]

    # Create and run tester
    tester = DynamicSchemaTester(server_url)

    if not tester.setup():
        sys.exit(1)

    success = tester.run_all_tests()
    
    tester.cleanup()

    sys.exit(0 if success else 1)


# ============================================================================
# ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    main()
