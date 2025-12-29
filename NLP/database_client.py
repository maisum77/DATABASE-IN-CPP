#!/usr/bin/env python3

# ============================================================================
# PROGRAM: database_client.py
# PURPOSE: Python client to communicate with C++ HTTP database server
#          Provides simple functions for sending queries and getting results
# ============================================================================

import requests
import json
import sys

# ============================================================================
# CLASS: DatabaseClient
# PURPOSE: Handles all HTTP communication with the C++ database server
# ============================================================================
class DatabaseClient:
    """
    This class manages the connection to the C++ HTTP database server.
    
    It provides simple methods to interact with the database:
    - send_query() - Execute a query and get results
    - get_table() - Get all data from a table
    - insert_row() - Add a new row to a table
    - And more...
    
    The server runs on localhost:8080 by default.
    """

    def __init__(self, host="localhost", port=8080):
        """
        Initialize the database client with server address.
        
        Parameters:
            host (str): Server hostname or IP address
            port (int): Server port number
        """
        self.base_url = f"http://{host}:{port}"
        self.is_connected = False
        self.test_connection()

    def test_connection(self):
        """
        Test if the server is running and accessible.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ok":
                    self.is_connected = True
                    print(f"[OK] Connected to database server at {self.base_url}")
                    return True
            return False
        except Exception as error:
            print(f"[Error] Cannot connect to server: {error}")
            print(f"Make sure the C++ server is running at {self.base_url}")
            self.is_connected = False
            return False

    def get_tables(self):
        """
        Get a list of all tables in the database.
        
        Returns:
            list: List of table names, or empty list if error
        """
        try:
            response = requests.get(f"{self.base_url}/tables", timeout=5)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as error:
            print(f"[Error] Failed to get tables: {error}")
            return []

    def get_table(self, table_name):
        """
        Get all data from a specific table.
        
        Parameters:
            table_name (str): Name of the table to retrieve
            
        Returns:
            list: Table data as a list of lists (rows), or empty list if error
        """
        try:
            response = requests.get(
                f"{self.base_url}/table/{table_name}", 
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"[Error] {response.json().get('error', 'Unknown error')}")
                return []
        except Exception as error:
            print(f"[Error] Failed to get table: {error}")
            return []

    def get_table_schema(self, table_name):
        """
        Get the schema (column information) for a table.
        
        Parameters:
            table_name (str): Name of the table
            
        Returns:
            dict: Schema information with keys: name, columns, primary_key, 
                  foreign_key, row_count, or empty dict if error
        """
        try:
            response = requests.get(
                f"{self.base_url}/table/{table_name}/schema",
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"[Error] {response.json().get('error', 'Unknown error')}")
                return {}
        except Exception as error:
            print(f"[Error] Failed to get schema: {error}")
            return {}

    def send_query(self, table_name, column_name, operator_str, value):
        """
        Execute a SELECT query with a WHERE clause.
        
        This is the main method for querying the database.
        
        Parameters:
            table_name (str): Name of the table to query
            column_name (str): Column to filter on
            operator_str (str): Comparison operator (=, >, <, >=, <=, !=)
            value (str): Value to compare against
            
        Returns:
            list: Query results as a list of rows, or empty list if no matches
        """
        try:
            query_data = {
                "table": table_name,
                "column": column_name,
                "operator": operator_str,
                "value": value
            }
            
            response = requests.post(
                f"{self.base_url}/query",
                json=query_data,
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"[Error] {response.json().get('error', 'Unknown error')}")
                return []
                
        except Exception as error:
            print(f"[Error] Query failed: {error}")
            return []

    def insert_row(self, table_name, values):
        """
        Insert a new row into a table.
        
        Parameters:
            table_name (str): Name of the table
            values (list): List of values to insert (in column order)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            insert_data = {"values": values}
            
            response = requests.post(
                f"{self.base_url}/table/{table_name}/insert",
                json=insert_data,
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print(f"[OK] Row inserted into {table_name}")
                    return True
            
            print(f"[Error] Insert failed")
            return False
            
        except Exception as error:
            print(f"[Error] Insert failed: {error}")
            return False

    def batch_insert(self, table_name, rows):
        """
        Insert multiple rows into a table at once.
        
        Parameters:
            table_name (str): Name of the table
            rows (list): List of rows, where each row is a list of values
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            insert_data = {"rows": rows}
            
            response = requests.post(
                f"{self.base_url}/table/{table_name}/batch_insert",
                json=insert_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    count = result.get("inserted", 0)
                    print(f"[OK] Inserted {count} rows into {table_name}")
                    return True
            
            print(f"[Error] Batch insert failed")
            return False
            
        except Exception as error:
            print(f"[Error] Batch insert failed: {error}")
            return False

    def perform_join(self, left_table, right_table):
        """
        Perform an inner join between two tables.
        
        The join is done using the foreign key of the left table
        and the primary key of the right table.
        
        Parameters:
            left_table (str): Name of the left table
            right_table (str): Name of the right table
            
        Returns:
            list: Joined data as a list of rows, or empty list if error
        """
        try:
            join_data = {
                "left_table": left_table,
                "right_table": right_table
            }
            
            response = requests.post(
                f"{self.base_url}/join",
                json=join_data,
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"[Error] {response.json().get('error', 'Unknown error')}")
                return []
                
        except Exception as error:
            print(f"[Error] Join failed: {error}")
            return []

    def search_table(self, table_name, column_name, keyword):
        """
        Search for rows where a column contains a keyword (case-insensitive).
        
        Parameters:
            table_name (str): Name of the table
            column_name (str): Column to search in
            keyword (str): Text to search for
            
        Returns:
            list: Matching rows, or empty list if none found
        """
        try:
            search_data = {
                "column": column_name,
                "keyword": keyword
            }
            
            response = requests.post(
                f"{self.base_url}/table/{table_name}/search",
                json=search_data,
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"[Error] {response.json().get('error', 'Unknown error')}")
                return []
                
        except Exception as error:
            print(f"[Error] Search failed: {error}")
            return []

    def get_table_stats(self, table_name):
        """
        Get statistics for a table.
        
        Parameters:
            table_name (str): Name of the table
            
        Returns:
            dict: Statistics with keys: row_count, column_count, non_null_counts
        """
        try:
            response = requests.get(
                f"{self.base_url}/table/{table_name}/stats",
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"[Error] {response.json().get('error', 'Unknown error')}")
                return {}
                
        except Exception as error:
            print(f"[Error] Failed to get stats: {error}")
            return {}

    def export_table(self, table_name):
        """
        Export a table to a CSV file.
        
        Parameters:
            table_name (str): Name of the table to export
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            response = requests.post(
                f"{self.base_url}/table/{table_name}/export",
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                filename = result.get("file", table_name + ".csv")
                print(f"[OK] Table exported to {filename}")
                return True
            else:
                print(f"[Error] Export failed")
                return False
                
        except Exception as error:
            print(f"[Error] Export failed: {error}")
            return False


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def print_table(table_data):
    """
    Print table data in a readable format.
    
    Parameters:
        table_data (list): List of rows, where first row is the header
    """
    if not table_data or len(table_data) == 0:
        print("No data to display")
        return

    # Calculate column widths
    col_widths = []
    for row in table_data:
        for i, cell in enumerate(row):
            cell_str = str(cell)
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(cell_str))
            else:
                col_widths.append(len(cell_str))

    # Print header
    print("\n" + "-" * (sum(col_widths) + len(col_widths) * 3))
    header = table_data[0]
    for i, cell in enumerate(header):
        print(f" {str(cell):<{col_widths[i]}} |", end="")
    print()

    # Print data rows
    print("-" * (sum(col_widths) + len(col_widths) * 3))
    for row in table_data[1:]:
        for i, cell in enumerate(row):
            print(f" {str(cell):<{col_widths[i]}} |", end="")
        print()
    print("-" * (sum(col_widths) + len(col_widths) * 3) + "\n")


def demo_client():
    """
    Demonstrate how to use the DatabaseClient class.
    """
    print("=" * 60)
    print("   Database Client Demo")
    print("=" * 60)
    print()

    # Create client instance
    db = DatabaseClient()

    if not db.is_connected:
        print("\n[Error] Could not connect to server.")
        print("Please start the C++ server first:")
        print("  ./main")
        return

    print()
    print("Available Tables:")
    print("-" * 40)

    tables = db.get_tables()
    for table in tables:
        print(f"  - {table}")

    print()
    print("Demo 1: Get All Employees")
    print("-" * 40)

    employees = db.get_table("employees")
    print_table(employees)

    print()
    print("Demo 2: Get Table Schema")
    print("-" * 40)

    schema = db.get_table_schema("employees")
    print(f"Table: {schema.get('name', 'Unknown')}")
    print(f"Columns: {schema.get('columns', [])}")
    print(f"Primary Key: {schema.get('primary_key', 'None')}")
    print(f"Row Count: {schema.get('row_count', 0)}")

    print()
    print("Demo 3: Query with WHERE Clause")
    print("-" * 40)
    print("Finding employees where age > 30...")
    print()

    results = db.send_query("employees", "age", ">", "30")
    print_table(results)

    print()
    print("Demo 4: Search for Text")
    print("-" * 40)
    print("Searching for 'Alice' in name column...")
    print()

    search_results = db.search_table("employees", "name", "Alice")
    print_table(search_results)

    print()
    print("Demo 5: Join Tables")
    print("-" * 40)
    print("Performing inner join between employees and departments...")
    print()

    joined = db.perform_join("employees", "departments")
    print_table(joined)

    print()
    print("Demo 6: Get Table Statistics")
    print("-" * 40)

    stats = db.get_table_stats("employees")
    print(f"Row Count: {stats.get('row_count', 0)}")
    print(f"Column Count: {stats.get('column_count', 0)}")
    print("Non-null counts per column:")
    for col, count in stats.get("non_null_counts", {}).items():
        print(f"  {col}: {count}")

    print()
    print("=" * 60)
    print("Demo Complete!")
    print("=" * 60)


# ============================================================================
# MAIN EXECUTION
# ============================================================================
if __name__ == "__main__":
    # If command line arguments provided, treat as single query
    if len(sys.argv) >= 4:
        table = sys.argv[1]
        column = sys.argv[2]
        operator = sys.argv[3]
        value = sys.argv[4] if len(sys.argv) > 4 else ""

        db = DatabaseClient()
        if db.is_connected:
            results = db.send_query(table, column, operator, value)
            print_table(results)
    else:
        # Run the demo
        demo_client()
