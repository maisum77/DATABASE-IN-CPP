# ============================================================================
# MODULE: data_fetcher.py
# PURPOSE: Fetch data from the C++ database server via REST API
# ============================================================================

import requests
import json
import pandas as pd
from typing import List, Dict, Optional, Any


# ============================================================================
# CLASS: DatabaseFetcher
# PURPOSE: Fetches data from the C++ database server
# ============================================================================
class DatabaseFetcher:
    """
    This class handles all communication with the C++ database server.
    
    It provides methods to:
    - Get list of all tables
    - Fetch table data
    - Get table schema
    - Execute queries
    - Perform searches
    
    All data is returned as Pandas DataFrames for easy analysis.
    """

    def __init__(self, server_url: str = "http://localhost:8080"):
        """
        Initialize the database fetcher.
        
        Parameters:
            server_url (str): URL of the database server
        """
        self.server_url = server_url
        self.is_connected = False
        self.test_connection()

    def test_connection(self) -> bool:
        """
        Test if the server is accessible.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            if response.status_code == 200:
                self.is_connected = True
                print(f"[OK] Connected to database at {self.server_url}")
                return True
            return False
        except Exception as error:
            print(f"[Error] Cannot connect to server: {error}")
            self.is_connected = False
            return False

    def get_tables(self) -> List[str]:
        """
        Get list of all tables in the database.
        
        Returns:
            List[str]: List of table names
        """
        try:
            response = requests.get(f"{self.server_url}/tables", timeout=5)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as error:
            print(f"[Error] Failed to get tables: {error}")
            return []

    def get_table_data(self, table_name: str) -> pd.DataFrame:
        """
        Fetch all data from a table.
        
        Parameters:
            table_name (str): Name of the table
            
        Returns:
            pd.DataFrame: Table data with columns as headers
        """
        try:
            response = requests.get(
                f"{self.server_url}/table/{table_name}",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                if data:
                    df = pd.DataFrame(data[1:], columns=data[0])
                    return df
                return pd.DataFrame()
            else:
                print(f"[Error] Failed to get table: {response.json().get('error', 'Unknown')}")
                return pd.DataFrame()
        except Exception as error:
            print(f"[Error] Failed to fetch table: {error}")
            return pd.DataFrame()

    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """
        Get schema information for a table.
        
        Parameters:
            table_name (str): Name of the table
            
        Returns:
            Dict: Schema information including columns, keys, row count
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

    def get_all_data(self) -> Dict[str, pd.DataFrame]:
        """
        Fetch data from all tables in the database.
        
        Returns:
            Dict[str, pd.DataFrame]: Dictionary mapping table names to DataFrames
        """
        tables = self.get_tables()
        all_data = {}

        for table_name in tables:
            df = self.get_table_data(table_name)
            if not df.empty:
                all_data[table_name] = df

        return all_data

    def execute_query(self, table_name: str, column: str, operator: str, value: str) -> pd.DataFrame:
        """
        Execute a SELECT query with WHERE clause.
        
        Parameters:
            table_name (str): Table to query
            column (str): Column to filter on
            operator (str): Comparison operator (=, >, <, >=, <=, !=)
            value (str): Value to compare
            
        Returns:
            pd.DataFrame: Query results
        """
        try:
            query_data = {
                "table": table_name,
                "column": column,
                "operator": operator,
                "value": value
            }

            response = requests.post(
                f"{self.server_url}/query",
                json=query_data,
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                if data:
                    return pd.DataFrame(data[1:], columns=data[0])
                return pd.DataFrame()
            else:
                print(f"[Error] Query failed: {response.json().get('error', 'Unknown')}")
                return pd.DataFrame()
        except Exception as error:
            print(f"[Error] Query failed: {error}")
            return pd.DataFrame()

    def search_table(self, table_name: str, column: str, keyword: str) -> pd.DataFrame:
        """
        Search for text in a column.
        
        Parameters:
            table_name (str): Table to search
            column (str): Column to search in
            keyword (str): Text to search for
            
        Returns:
            pd.DataFrame: Search results
        """
        try:
            search_data = {
                "column": column,
                "keyword": keyword
            }

            response = requests.post(
                f"{self.server_url}/table/{table_name}/search",
                json=search_data,
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                if data:
                    return pd.DataFrame(data[1:], columns=data[0])
                return pd.DataFrame()
            else:
                print(f"[Error] Search failed: {response.json().get('error', 'Unknown')}")
                return pd.DataFrame()
        except Exception as error:
            print(f"[Error] Search failed: {error}")
            return pd.DataFrame()

    def get_table_stats(self, table_name: str) -> Dict[str, Any]:
        """
        Get statistics for a table.
        
        Parameters:
            table_name (str): Name of the table
            
        Returns:
            Dict: Statistics including row count, column count, non-null counts
        """
        try:
            response = requests.get(
                f"{self.server_url}/table/{table_name}/stats",
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as error:
            print(f"[Error] Failed to get stats: {error}")
            return {}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def fetch_all_database_data(server_url: str = "http://localhost:8080") -> Dict[str, pd.DataFrame]:
    """
    Convenience function to fetch all data from the database.
    
    Parameters:
        server_url (str): URL of the database server
        
    Returns:
        Dict[str, pd.DataFrame]: Dictionary mapping table names to DataFrames
    """
    fetcher = DatabaseFetcher(server_url)
    return fetcher.get_all_data()


def print_database_summary(server_url: str = "http://localhost:8080") -> None:
    """
    Print a summary of the database.
    
    Parameters:
        server_url (str): URL of the database server
    """
    fetcher = DatabaseFetcher(server_url)
    
    if not fetcher.is_connected:
        print("[Error] Cannot connect to database")
        return

    tables = fetcher.get_tables()
    
    print("\n" + "=" * 60)
    print("   Database Summary")
    print("=" * 60)
    print(f"\nTotal tables: {len(tables)}")
    
    for table_name in tables:
        schema = fetcher.get_table_schema(table_name)
        df = fetcher.get_table_data(table_name)
        
        print(f"\n{table_name}:")
        print(f"  Columns: {schema.get('columns', [])}")
        print(f"  Rows: {len(df)}")
        print(f"  Primary Key: {schema.get('primary_key', 'None')}")
    
    print("\n" + "=" * 60)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Print database summary
    print_database_summary()
