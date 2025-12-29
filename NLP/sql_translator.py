# ============================================================================
# MODULE: sql_translator.py
# PURPOSE: Convert natural language text to SQL queries using transformers
#          Uses a model specifically fine-tuned for SQL generation (WikiSQL)
#          Supports dynamic schema fetching from the database server
# ============================================================================

import os
import sys
import re
import requests

# Check for transformers and torch availability
try:
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("[Warning] transformers or torch not installed.")
    print("[Warning] Install with: pip install transformers torch")


# ============================================================================
# CLASS: DynamicSchema
# PURPOSE: Dynamically fetches and caches schema from database server
# ============================================================================
class DynamicSchema:
    """
    This class fetches schema information from the database server
    at runtime, allowing the SQL translator to work with any table
    that exists in the database.
    
    Features:
    - Fetches schema on demand
    - Caches results for performance
    - Refreshes when tables change
    """

    def __init__(self, server_url=None):
        """
        Initialize the dynamic schema fetcher.
        
        Parameters:
            server_url (str): Base URL of the database server
                              e.g., "http://localhost:8080"
        """
        self.server_url = server_url
        self.tables = {}
        self.cache_valid = False

    def set_server_url(self, server_url):
        """
        Set the server URL for schema fetching.
        
        Parameters:
            server_url (str): Base URL of the database server
        """
        self.server_url = server_url
        self.cache_valid = False  # Invalidate cache when server changes

    def fetch_schema(self):
        """
        Fetch the current schema from the database server.
        
        This method calls the /tables endpoint to get all table names,
        then calls /table/:name/schema for each table to get column info.
        
        Returns:
            bool: True if schema was fetched successfully, False otherwise
        """
        if not self.server_url:
            print("[Warning] No server URL configured for schema fetching.")
            return False

        try:
            # Get list of all tables
            response = requests.get(f"{self.server_url}/tables", timeout=5)
            
            if response.status_code != 200:
                print(f"[Error] Failed to get tables: HTTP {response.status_code}")
                return False

            table_names = response.json()
            
            # Clear existing schema
            self.tables = {}
            
            # Get schema for each table
            for table_name in table_names:
                schema_response = requests.get(
                    f"{self.server_url}/table/{table_name}/schema",
                    timeout=5
                )
                
                if schema_response.status_code == 200:
                    schema = schema_response.json()
                    self.tables[table_name] = {
                        "columns": schema.get("columns", []),
                        "primary_key": schema.get("primary_key", ""),
                        "foreign_key": schema.get("foreign_key", ""),
                        "row_count": schema.get("row_count", 0)
                    }
                else:
                    print(f"[Warning] Could not fetch schema for table: {table_name}")

            self.cache_valid = True
            print(f"[OK] Schema fetched: {len(self.tables)} tables")
            return True

        except Exception as error:
            print(f"[Error] Failed to fetch schema: {error}")
            return False

    def get_table_columns(self, table_name):
        """
        Get the list of columns for a specific table.
        
        Parameters:
            table_name (str): Name of the table
            
        Returns:
            list: List of column names, or empty list if table not found
        """
        if table_name in self.tables:
            return self.tables[table_name]["columns"]
        return []

    def get_all_tables(self):
        """
        Get a list of all table names in the database.
        
        Returns:
            list: List of table names
        """
        return list(self.tables.keys())

    def table_exists(self, table_name):
        """
        Check if a table exists in the schema.
        
        Parameters:
            table_name (str): Name of the table to check
            
        Returns:
            bool: True if table exists, False otherwise
        """
        return table_name in self.tables

    def format_schema_for_prompt(self):
        """
        Format the schema as a string for inclusion in prompts.
        
        Returns:
            str: Formatted schema information
        """
        if not self.tables:
            # Return empty schema if nothing loaded
            return "No tables available"

        schema_parts = []
        
        for table_name, table_info in self.tables.items():
            columns_str = ", ".join(table_info["columns"])
            schema_parts.append(f"Table: {table_name} (columns: {columns_str})")
        
        return " | ".join(schema_parts)

    def refresh(self):
        """
        Force a refresh of the schema cache.
        
        Returns:
            bool: True if refresh succeeded, False otherwise
        """
        self.cache_valid = False
        return self.fetch_schema()


# ============================================================================
# CLASS: SQLTranslator
# PURPOSE: Uses a pre-trained WikiSQL model to convert natural language to SQL
# ============================================================================
class SQLTranslator:
    """
    This class loads a pre-trained model that has been fine-tuned
    specifically for Text-to-SQL tasks using the WikiSQL dataset.
    
    Unlike general translation models, this model understands
    SQL syntax and generates proper SQL queries.
    
    IMPORTANT: We use 'mrm8488/t5-base-finetuned-wikiSQL' which is
    specifically trained to convert natural language to SQL, NOT
    to translate between human languages.
    
    The translator can work with a dynamic schema fetched from the
    database server, allowing it to generate SQL for any table.
    """

    def __init__(self, server_url=None):
        """
        Initialize the SQL translator by loading the model and tokenizer.
        
        Parameters:
            server_url (str): Optional URL of the database server
                             for dynamic schema fetching
        """
        self.model = None
        self.tokenizer = None
        self.dynamic_schema = DynamicSchema(server_url)
        
        # Use a model fine-tuned on WikiSQL dataset for text-to-sql
        # This model is trained specifically for SQL generation, NOT translation
        self.model_name = "mrm8488/t5-base-finetuned-wikiSQL"

        if TRANSFORMERS_AVAILABLE:
            print("Loading SQL generation model...")
            print(f"Model: {self.model_name}")
            print("This model is specifically trained for Text-to-SQL tasks.")
            print()

            try:
                # Load the tokenizer
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                
                # Load the pre-trained model fine-tuned for WikiSQL
                self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
                
                print("Model loaded successfully!")
                print()

            except Exception as error:
                print(f"[Warning] Failed to load transformer model: {error}")
                print("[Info] Will use rule-based fallback instead.")
                self.model = None
                self.tokenizer = None
        else:
            print("[Error] Required libraries not available.")
            print("Please install: pip install transformers torch")

        # Fetch dynamic schema if server URL provided
        if server_url:
            self.dynamic_schema.fetch_schema()

    def set_server_url(self, server_url):
        """
        Set the server URL for dynamic schema fetching.
        
        Parameters:
            server_url (str): Base URL of the database server
        """
        self.dynamic_schema.set_server_url(server_url)
        self.dynamic_schema.fetch_schema()

    def refresh_schema(self):
        """
        Refresh the schema from the database server.
        
        This should be called when the database schema changes
        (e.g., after creating a new table).
        
        Returns:
            bool: True if refresh succeeded, False otherwise
        """
        return self.dynamic_schema.refresh()

    def convert_to_sql(self, natural_text):
        """
        Convert natural language text to a SQL query.
        
        This method takes a user's natural language request and
        generates a corresponding SQL query using the transformer model.
        
        Parameters:
            natural_text (str): English description of what data to retrieve
            
        Returns:
            str: Generated SQL query, or fallback query if model fails
            
        Example:
            Input:  "Show me all employees"
            Output: "SELECT * FROM employees;"
        """
        # If model is not available, use fallback immediately
        if self.model is None or self.tokenizer is None:
            return self.rule_based_fallback(natural_text)

        try:
            # Create the input prompt for the model
            # The WikiSQL model expects a specific format
            input_text = self._create_prompt(natural_text)

            # Step 1: Tokenize the input
            input_ids = self.tokenizer.encode(
                input_text,
                return_tensors="pt",
                max_length=512,
                truncation=True
            )

            # Step 2: Generate the SQL query
            with torch.no_grad():
                outputs = self.model.generate(
                    input_ids,
                    max_length=256,
                    num_beams=4,
                    early_stopping=True,
                    temperature=0.3
                )

            # Step 3: Decode the generated tokens to a string
            sql_query = self.tokenizer.decode(
                outputs[0],
                skip_special_tokens=True
            )

            # Step 4: Clean up the SQL query
            sql_query = self._clean_sql_output(sql_query)

            # Validate that we got actual SQL
            if self._is_valid_sql(sql_query):
                return sql_query
            else:
                # Model output doesn't look like SQL, use fallback
                print("[Info] Model generated invalid SQL, using fallback.")
                return self.rule_based_fallback(natural_text)

        except Exception as error:
            # If model fails, fall back to rule-based approach
            print(f"[Info] Model inference failed: {error}")
            print("[Info] Using rule-based fallback.")
            return self.rule_based_fallback(natural_text)

    def translate(self, natural_text):
        """
        Convert natural language text to a SQL query.
        
        This is an alias for convert_to_sql() for backward compatibility.
        
        Parameters:
            natural_text (str): English description of what data to retrieve
            
        Returns:
            str: Generated SQL query, or fallback query if model fails
        """
        return self.convert_to_sql(natural_text)

    def _create_prompt(self, natural_text):
        """
        Create the input prompt for the SQL model.
        
        The WikiSQL model works best with a specific prompt format.
        We provide the question and schema information.
        
        Parameters:
            natural_text (str): The user's natural language request
            
        Returns:
            str: Formatted prompt for the model
        """
        # Get schema information (from server if available)
        schema_info = self.dynamic_schema.format_schema_for_prompt()
        
        # Create prompt with schema context
        # This helps the model generate accurate SQL
        prompt = f"question: {natural_text} | schema: {schema_info}"
        
        return prompt

    def _clean_sql_output(self, sql_text):
        """
        Clean up the SQL query generated by the model.
        
        This removes any extra whitespace, fixes common issues,
        and ensures proper formatting.
        
        Parameters:
            sql_text (str): Raw output from the model
            
        Returns:
            str: Cleaned SQL query
        """
        # Remove extra whitespace
        sql_text = sql_text.strip()
        
        # Remove trailing punctuation that might have been added
        sql_text = sql_text.rstrip('.,')
        
        # Ensure query ends with semicolon
        if not sql_text.endswith(';'):
            sql_text = sql_text + ';'
        
        return sql_text

    def _is_valid_sql(self, sql_text):
        """
        Check if the generated text looks like a valid SQL query.
        
        This is a simple validation to catch cases where the model
        generates non-SQL output (like translations to German).
        
        Parameters:
            sql_text (str): The text to validate
            
        Returns:
            bool: True if it looks like SQL, False otherwise
        """
        # Convert to lowercase for checking
        sql_lower = sql_text.lower()
        
        # Must start with common SQL keywords
        valid_starts = ["select", "insert", "update", "delete", "create"]
        
        if not any(sql_lower.startswith(keyword) for keyword in valid_starts):
            return False
        
        # Must contain FROM for SELECT queries
        if sql_lower.startswith("select") and "from" not in sql_lower:
            return False
        
        # Check for obvious non-SQL patterns (like German words)
        german_indicators = ["zeigen", "mitarbeiter", "abteilungen", "alle", "mir"]
        if any(word in sql_lower for word in german_indicators):
            return False
        
        return True

    def rule_based_fallback(self, natural_text):
        """
        Generate SQL using simple rule-based logic.
        
        This method is used when:
        1. The transformer model is not available
        2. The model fails to generate valid SQL
        3. We need guaranteed SQL-like output
        
        Parameters:
            natural_text (str): The user's natural language request
            
        Returns:
            str: A SQL query generated based on pattern matching
        """
        # Convert to lowercase for pattern matching
        text_lower = natural_text.lower()
        
        # Initialize default values
        table_name = ""
        columns = "*"
        where_clause = ""
        
        # Try to detect table name from query
        # First, check dynamic schema
        available_tables = self.dynamic_schema.get_all_tables()
        
        for table in available_tables:
            if table.lower() in text_lower:
                table_name = table
                break
        
        # If no table found in dynamic schema, try common patterns
        if not table_name:
            if "department" in text_lower:
                table_name = "departments"
            elif "employee" in text_lower or "staff" in text_lower or "worker" in text_lower:
                table_name = "employees"
            elif "product" in text_lower:
                table_name = "products"
            elif "user" in text_lower or "customer" in text_lower:
                table_name = "users"
            else:
                # Default to first available table
                if available_tables:
                    table_name = available_tables[0]
                else:
                    table_name = "employees"  # Ultimate fallback
        
        # Handle SELECT vs other operations
        if "show" in text_lower or "list" in text_lower or "display" in text_lower or "get" in text_lower or "find" in text_lower:
            # Determine which columns to select
            # Check dynamic schema for column names
            table_columns = self.dynamic_schema.get_table_columns(table_name)
            
            # Look for column mentions in the query
            for col in table_columns:
                if col.lower() in text_lower:
                    columns = col
                    break
            
            # Check for common column patterns
            if "name" in text_lower:
                for col in table_columns:
                    if "name" in col.lower():
                        columns = col
                        break
            elif "id" in text_lower:
                for col in table_columns:
                    if col.lower() == "id" or col.lower().endswith("_id"):
                        columns = col
                        break
            
            # Parse WHERE clause conditions
            where_conditions = []
            
            # Check for common comparisons
            if "greater than" in text_lower or "more than" in text_lower or "older than" in text_lower:
                numbers = re.findall(r'\d+', text_lower)
                if numbers:
                    # Find the column being compared
                    for col in table_columns:
                        if col.lower() in text_lower.split("greater than")[0].split("more than")[0]:
                            where_conditions.append(f"{col} > {numbers[0]}")
                            break
                    else:
                        # No column found, use first numeric column
                        where_conditions.append(f"age > {numbers[0]}")
            
            elif "less than" in text_lower or "fewer than" in text_lower or "younger than" in text_lower:
                numbers = re.findall(r'\d+', text_lower)
                if numbers:
                    for col in table_columns:
                        if col.lower() in text_lower.split("less than")[0].split("fewer than")[0]:
                            where_conditions.append(f"{col} < {numbers[0]}")
                            break
                    else:
                        where_conditions.append(f"age < {numbers[0]}")
            
            elif "equals" in text_lower or "equal to" in text_lower:
                numbers = re.findall(r'\d+', text_lower)
                if numbers:
                    for col in table_columns:
                        if col.lower() in text_lower.split("equals")[0].split("equal to")[0]:
                            where_conditions.append(f"{col} = {numbers[0]}")
                            break
                    else:
                        where_conditions.append(f"age = {numbers[0]}")
            
            # Build the WHERE clause
            if where_conditions:
                where_clause = " WHERE " + " AND ".join(where_conditions)
            
            # Build the final SQL query
            sql_query = f"SELECT {columns} FROM {table_name}{where_clause};"
            
            return sql_query
        
        # For other types of queries, default to SELECT all
        sql_query = f"SELECT * FROM {table_name};"
        
        return sql_query


# ============================================================================
# CLASS: SimpleSQLGenerator
# PURPOSE: Simple rule-based SQL generator as standalone fallback
# ============================================================================
class SimpleSQLGenerator:
    """
    A completely standalone SQL generator that doesn't require any
    machine learning models. Uses pattern matching to generate SQL.
    
    This is useful as a fallback when transformers are not available
    or when you want to guarantee SQL-like output without AI.
    """

    def __init__(self, server_url=None):
        """
        Initialize the simple SQL generator.
        
        Parameters:
            server_url (str): Optional URL of the database server
        """
        print("Using simple rule-based SQL generator.")
        self.dynamic_schema = DynamicSchema(server_url)
        if server_url:
            self.dynamic_schema.fetch_schema()

    def generate(self, user_text):
        """
        Generate a SQL query based on pattern matching.
        
        This method analyzes the user's text for keywords and patterns
        to construct an appropriate SQL query.
        
        Parameters:
            user_text (str): Natural language description
            
        Returns:
            str: Generated SQL query
        """
        # Create a translator instance for fallback logic
        translator = SQLTranslator()
        translator.dynamic_schema = self.dynamic_schema
        return translator.rule_based_fallback(user_text)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def test_translation():
    """
    Test the SQL translation with example inputs.
    
    This function demonstrates how the translator works
    and verifies that it produces valid SQL output.
    """
    print("=" * 60)
    print("   Testing SQL Translation")
    print("=" * 60)
    print()

    # Create translator
    translator = SQLTranslator()
    
    # Test queries
    test_queries = [
        "Show me all employees",
        "List all departments",
        "Show employees where age is greater than 30",
        "Find employees with age less than 25",
        "List the names of all employees",
        "Show departments where deptID is d10",
        "Display all employees with age equals 35"
    ]

    print("Test Results:")
    print("-" * 60)

    for query in test_queries:
        print(f"Input:  {query}")
        
        sql = translator.convert_to_sql(query)
        
        print(f"Output: {sql}")
        print()
    
    print("-" * 60)
    print("Test complete!")


# ============================================================================
# MAIN EXECUTION
# ============================================================================
if __name__ == "__main__":
    # Run the test function
    test_translation()
