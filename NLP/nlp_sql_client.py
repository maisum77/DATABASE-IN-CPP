#!/usr/bin/env python3

# ============================================================================
# PROGRAM: nlp_sql_client.py
# PURPOSE: Convert natural language to SQL and execute on C++ HTTP server
# ============================================================================

import requests
import json
import sys
import re

# Import our custom modules
from sql_translator import SQLTranslator, TRANSFORMERS_AVAILABLE


# ============================================================================
# CLASS: NLPToSQLClient
# PURPOSE: Main application that converts NLP to SQL and executes on server
# ============================================================================
class NLPToSQLClient:
    """
    This class provides a complete interface for:
    1. Converting natural language to SQL queries
    2. Sending queries to the C++ HTTP server via REST API
    3. Displaying results in a readable format
    
    It uses the transformers library for NLP to SQL conversion
    and the requests library for HTTP communication.
    """

    def __init__(self, server_host="localhost", server_port=8080):
        """
        Initialize the NLP to SQL client.
        
        Parameters:
            server_host (str): Server hostname or IP
            server_port (int): Server port number
        """
        self.server_url = f"http://{server_host}:{server_port}"
        self.sql_translator = None
        self.is_connected = False

    def initialize(self):
        """
        Initialize all components.
        
        Returns:
            bool: True if successful, False otherwise
        """
        print("=" * 60)
        print("   Natural Language to SQL Converter")
        print("   Connects to C++ HTTP Database Server")
        print("=" * 60)
        print()

        # Test connection to server
        print("Step 1: Connecting to database server...")
        if not self.test_connection():
            print("\n[Error] Cannot connect to server.")
            print("Please start the C++ server first:")
            print("  ./main")
            print(f"  (Server should be running at {self.server_url})")
            return False

        # Initialize the SQL translator
        print("\nStep 2: Initializing SQL translator...")
        if TRANSFORMERS_AVAILABLE:
            self.sql_translator = SQLTranslator()
        else:
            print("[Info] Using rule-based SQL generation.")

        print()
        print("Step 3: Initialization complete!")
        print()
        print("Available tables in database:")
        self.print_available_tables()
        print()
        print("You can now enter natural language queries.")
        print("Type 'help' for examples, 'quit' to exit.")
        print("-" * 60)

        return True

    def test_connection(self):
        """
        Test if the server is running and accessible.
        
        Returns:
            bool: True if connection successful
        """
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            if response.status_code == 200:
                self.is_connected = True
                print(f"[OK] Connected to {self.server_url}")
                return True
            return False
        except Exception as error:
            print(f"[Error] Connection failed: {error}")
            self.is_connected = False
            return False

    def get_tables(self):
        """
        Get list of all tables in the database.
        
        Returns:
            list: List of table names
        """
        try:
            response = requests.get(f"{self.server_url}/tables", timeout=5)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as error:
            print(f"[Error] Failed to get tables: {error}")
            return []

    def print_available_tables(self):
        """
        Print list of available tables with their schemas.
        """
        tables = self.get_tables()
        for table_name in tables:
            schema = self.get_table_schema(table_name)
            columns = schema.get("columns", [])
            print(f"  - {table_name}: {', '.join(columns)}")

    def get_table_schema(self, table_name):
        """
        Get schema information for a table.
        
        Parameters:
            table_name (str): Name of the table
            
        Returns:
            dict: Schema information
        """
        try:
            response = requests.get(
                f"{self.server_url}/table/{table_name}/schema",
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as error:
            print(f"[Error] Failed to get schema: {error}")
            return {}

    def execute_query(self, table_name, column_name, operator_str, value):
        """
        Execute a SELECT query with WHERE clause.
        
        Parameters:
            table_name (str): Table to query
            column_name (str): Column to filter on
            operator_str (str): Operator (=, >, <, >=, <=, !=)
            value (str): Value to compare
            
        Returns:
            list: Query results
        """
        try:
            query_data = {
                "table": table_name,
                "column": column_name,
                "operator": operator_str,
                "value": value
            }
            
            response = requests.post(
                f"{self.server_url}/query",
                json=query_data,
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                error_msg = response.json().get("error", "Unknown error")
                print(f"[Error] Query failed: {error_msg}")
                return []
                
        except Exception as error:
            print(f"[Error] Query failed: {error}")
            return []

    def get_all_data(self, table_name):
        """
        Get all data from a table.
        
        Parameters:
            table_name (str): Name of the table
            
        Returns:
            list: Table data
        """
        try:
            response = requests.get(
                f"{self.server_url}/table/{table_name}",
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as error:
            print(f"[Error] Failed to get table: {error}")
            return []

    def search_table(self, table_name, column_name, keyword):
        """
        Search for text in a column.
        
        Parameters:
            table_name (str): Table to search
            column_name (str): Column to search in
            keyword (str): Text to search for
            
        Returns:
            list: Search results
        """
        try:
            search_data = {
                "column": column_name,
                "keyword": keyword
            }
            
            response = requests.post(
                f"{self.server_url}/table/{table_name}/search",
                json=search_data,
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                error_msg = response.json().get("error", "Unknown error")
                print(f"[Error] Search failed: {error_msg}")
                return []
                
        except Exception as error:
            print(f"[Error] Search failed: {error}")
            return []

    def perform_join(self, left_table, right_table):
        """
        Perform an inner join between two tables.
        
        Parameters:
            left_table (str): Left table name
            right_table (str): Right table name
            
        Returns:
            list: Joined results
        """
        try:
            join_data = {
                "left_table": left_table,
                "right_table": right_table
            }
            
            response = requests.post(
                f"{self.server_url}/join",
                json=join_data,
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                error_msg = response.json().get("error", "Unknown error")
                print(f"[Error] Join failed: {error_msg}")
                return []
                
        except Exception as error:
            print(f"[Error] Join failed: {error}")
            return []

    def convert_to_sql(self, natural_text):
        """
        Convert natural language to SQL using the translator.
        
        Parameters:
            natural_text (str): Natural language query
            
        Returns:
            str: SQL query or error message
        """
        if self.sql_translator:
            return self.sql_translator.convert_to_sql(natural_text)
        return self.simple_sql_generation(natural_text)

    def simple_sql_generation(self, text):
        """
        Simple rule-based SQL generation as fallback.
        
        Parameters:
            text (str): Natural language input
            
        Returns:
            str: SQL query
        """
        text_lower = text.lower()
        
        # Determine table
        if "department" in text_lower:
            table = "departments"
        elif "employee" in text_lower:
            table = "employees"
        else:
            table = "employees"  # default

        # Determine operation
        if "where" in text_lower or "with" in text_lower:
            # Extract condition
            condition = ""
            
            # Check for comparisons
            if "greater than" in text_lower or "more than" in text_lower:
                numbers = re.findall(r'\d+', text_lower)
                if numbers:
                    condition = "age > " + numbers[0]
            elif "less than" in text_lower or "fewer than" in text_lower:
                numbers = re.findall(r'\d+', text_lower)
                if numbers:
                    condition = "age < " + numbers[0]
            elif "equals" in text_lower or "equal to" in text_lower:
                numbers = re.findall(r'\d+', text_lower)
                if numbers:
                    condition = "age = " + numbers[0]
            
            if condition:
                return f"SELECT * FROM {table} WHERE {condition};"
            
            return f"SELECT * FROM {table};"
        
        return f"SELECT * FROM {table};"

    def parse_sql_query(self, sql_query):
        """
        Parse a SQL query to extract components for execution.
        
        This is a simple parser for basic SELECT queries.
        
        Parameters:
            sql_query (str): SQL query to parse
            
        Returns:
            dict: Parsed components or None if parsing fails
        """
        sql_lower = sql_query.lower().strip()
        
        # Basic SELECT parsing
        if not sql_lower.startswith("select"):
            return None

        # Remove semicolon if present
        if sql_lower.endswith(";"):
            sql_lower = sql_lower[:-1]
            sql_query = sql_query[:-1]

        # Parse SELECT clause
        select_end = sql_lower.find("from")
        if select_end == -1:
            return None

        select_clause = sql_lower[6:select_end].strip()
        
        # Parse FROM clause
        from_end = len(sql_lower)
        where_keyword = sql_lower.find("where")
        
        if where_keyword != -1:
            from_end = where_keyword
        else:
            # No WHERE clause
            from_keyword = sql_lower.find("from")
            table_name = sql_lower[from_keyword + 5:].strip()
            
            return {
                "type": "select",
                "table": table_name,
                "columns": select_clause,
                "where": None
            }

        table_name = sql_lower[select_end + 5:from_end].strip()
        where_clause = sql_lower[from_end + 6:].strip()

        # Parse WHERE clause: column operator value
        # Find operator
        operators = [" > ", " < ", " >= ", " <= ", " = ", " != "]
        operator_found = None
        operator_pos = -1
        
        for op in operators:
            pos = where_clause.find(op)
            if pos != -1:
                operator_found = op.strip()
                operator_pos = pos
                break

        if operator_found is None:
            return None

        column = where_clause[:operator_pos].strip()
        value = where_clause[operator_pos + len(operator_found):].strip()

        # Remove quotes from value if present
        if value.startswith("'") and value.endswith("'"):
            value = value[1:-1]
        elif value.startswith('"') and value.endswith('"'):
            value = value[1:-1]

        return {
            "type": "select",
            "table": table_name,
            "columns": select_clause,
            "where": {
                "column": column,
                "operator": operator_found,
                "value": value
            }
        }

    def execute_sql(self, sql_query):
        """
        Execute a SQL query on the server.
        
        Parameters:
            sql_query (str): SQL query to execute
            
        Returns:
            list: Query results
        """
        # Parse the SQL query
        parsed = self.parse_sql_query(sql_query)
        
        if parsed is None:
            print("[Error] Could not parse SQL query")
            return []

        if parsed["type"] != "select":
            print("[Error] Only SELECT queries are supported")
            return []

        table_name = parsed["table"]
        where = parsed.get("where")

        if where:
            return self.execute_query(
                table_name,
                where["column"],
                where["operator"],
                where["value"]
            )
        else:
            # No WHERE clause, get all data
            return self.get_all_data(table_name)

    def show_help(self):
        """
        Display help information.
        """
        print()
        print("Help - Example Queries:")
        print("-" * 40)
        print()
        print("Basic SELECT queries:")
        print('  "Show me all employees"')
        print('  "List all departments"')
        print('  "Display everything from employees"')
        print()
        print("SELECT with WHERE clause:")
        print('  "Show employees where age is 30"')
        print('  "Find employees with age greater than 30"')
        print('  "List departments where deptID is d10"')
        print('  "Show employees where age is less than 35"')
        print()
        print("Direct SQL queries:")
        print('  "SQL: SELECT * FROM employees"')
        print('  "SQL: SELECT * FROM employees WHERE age > 30"')
        print()
        print("Special commands:")
        print('  "tables" - List all tables')
        print('  "schema <table_name>" - Show table schema')
        print('  "join <table1> and <table2>" - Join two tables')
        print('  "quit" - Exit the application')
        print()
        print("Note: The translator uses AI which may not always")
        print("      produce perfect SQL. Review the generated query!")
        print("-" * 40)

    def print_results(self, results, sql_query):
        """
        Print query results in a formatted way.
        
        Parameters:
            results (list): Query results
            sql_query (str): The SQL query that was executed
        """
        print(f"\nSQL Query: {sql_query}")
        print("-" * 40)

        if not results or len(results) == 0:
            print("No results found.")
            return

        # Calculate column widths
        col_widths = []
        for row in results:
            for i, cell in enumerate(row):
                cell_str = str(cell)
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(cell_str))
                else:
                    col_widths.append(len(cell_str))

        # Print header
        header = results[0]
        for i, cell in enumerate(header):
            print(f" {str(cell):<{col_widths[i]}} ", end="")
        print()
        print("-" * (sum(col_widths) + len(col_widths) * 2))

        # Print data rows
        for row in results[1:]:
            for i, cell in enumerate(row):
                print(f" {str(cell):<{col_widths[i]}} ", end="")
            print()
        print()

    def run(self):
        """
        Main application loop.
        """
        while True:
            print()
            try:
                user_input = input("Enter your request (or 'help' or 'quit'): ").strip()

                # Check for exit
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break

                # Check for help
                if user_input.lower() == 'help':
                    self.show_help()
                    continue

                # Check for special commands
                if user_input.lower().startswith('tables'):
                    print("\nAvailable tables:")
                    for table in self.get_tables():
                        print(f"  - {table}")
                    continue

                if user_input.lower().startswith('schema'):
                    parts = user_input.split()
                    if len(parts) >= 2:
                        schema = self.get_table_schema(parts[1])
                        if schema:
                            print(f"\nSchema for {schema.get('name')}:")
                            print(f"  Columns: {schema.get('columns', [])}")
                            print(f"  Primary Key: {schema.get('primary_key', 'None')}")
                            print(f"  Row Count: {schema.get('row_count', 0)}")
                        else:
                            print(f"[Error] Table '{parts[1]}' not found")
                    else:
                        print("Usage: schema <table_name>")
                    continue

                if user_input.lower().startswith('join'):
                    parts = user_input.lower().split()
                    if len(parts) >= 4:
                        left_table = parts[1]
                        right_table = parts[3]
                        print(f"\nJoining {left_table} with {right_table}...")
                        results = self.perform_join(left_table, right_table)
                        self.print_results(results, f"JOIN {left_table} AND {right_table}")
                    else:
                        print("Usage: join <table1> and <table2>")
                    continue

                # Skip empty input
                if not user_input:
                    continue

                # Check for direct SQL
                if user_input.lower().startswith('sql:'):
                    sql_query = user_input[4:].strip()
                    print("\nUsing direct SQL query...")
                else:
                    # Convert natural language to SQL
                    print("\nTranslating...")
                    sql_query = self.convert_to_sql(user_input)

                print(f"Generated SQL: {sql_query}")
                print("\nExecuting query...")

                # Execute the query
                results = self.execute_sql(sql_query)
                self.print_results(results, sql_query)

            except KeyboardInterrupt:
                print("\n\nInterrupted by user. Goodbye!")
                break

            except Exception as e:
                print(f"[Error] An unexpected error occurred: {e}")


# ============================================================================
# MAIN FUNCTION
# ============================================================================
def main():
    """
    Main entry point for the application.
    """
    # Default settings
    server_host = "localhost"
    server_port = 8080

    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help']:
            print("Usage: python nlp_sql_client.py [host] [port]")
            print()
            print("Arguments:")
            print("  host    Server hostname (default: localhost)")
            print("  port    Server port (default: 8080)")
            print()
            print("Examples:")
            print("  python nlp_sql_client.py")
            print("  python nlp_sql_client.py localhost 8080")
            print("  python nlp_sql_client.py 192.168.1.100 8080")
            sys.exit(0)

        server_host = sys.argv[1]

    if len(sys.argv) > 2:
        try:
            server_port = int(sys.argv[2])
        except ValueError:
            print("[Error] Port must be a number.")
            sys.exit(1)

    # Create and run the application
    app = NLPToSQLClient(server_host, server_port)

    if app.initialize():
        app.run()


# ============================================================================
# ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    main()
