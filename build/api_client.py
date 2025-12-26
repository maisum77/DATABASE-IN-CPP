# api_client.py
import requests
import json
from typing import Dict, List, Any

class DatabaseAPI:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
    
    def health_check(self) -> Dict:
        """Health check endpoint"""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def get_tables(self) -> List[str]:
        """Get all table names"""
        response = requests.get(f"{self.base_url}/tables")
        response.raise_for_status()
        return response.json()
    
    def get_schema(self, table_name: str) -> Dict:
        """Get table structure"""
        response = requests.get(f"{self.base_url}/table/{table_name}/schema")
        response.raise_for_status()
        return response.json()
    
    def get_table(self, table_name: str) -> Any:
        """Get all table data"""
        response = requests.get(f"{self.base_url}/table/{table_name}")
        response.raise_for_status()
        return response.json()
    
    def query(self, table: str, column: str, operator: str, value: str) -> Any:
        """Execute WHERE query"""
        response = requests.post(
            f"{self.base_url}/query",
            json={"table": table, "column": column, "operator": operator, "value": str(value)}
        )
        response.raise_for_status()
        return response.json()
    
    def search(self, table: str, column: str, keyword: str) -> Any:
        """Execute search query"""
        response = requests.post(
            f"{self.base_url}/table/{table}/search",
            json={"column": column, "keyword": keyword}
        )
        response.raise_for_status()
        return response.json()
    
    def join(self, left_table: str, right_table: str) -> Any:
        """Execute JOIN"""
        response = requests.post(
            f"{self.base_url}/join",
            json={"left_table": left_table, "right_table": right_table}
        )
        response.raise_for_status()
        return response.json()
    
    def get_stats(self, table_name: str) -> Dict:
        """Get table statistics"""
        response = requests.get(f"{self.base_url}/table/{table_name}/stats")
        response.raise_for_status()
        return response.json()
    
    def get_column(self, table_name, column):
        """Extract text data for NLP"""
        response = requests.post(
            f"{self.base_url}/table/{table_name}/column",
            json={"column": column}
        )
        response.raise_for_status()
        return response.json()
    
    def batch_insert(self, table_name, rows):
        """Store NLP results in bulk"""
        response = requests.post(
            f"{self.base_url}/table/{table_name}/batch_insert",
            json={"rows": rows}
        )
        response.raise_for_status()
        return response.json()
    
    def update_rows(self, table_name, update_col, new_value, where_col, where_val):
        """Update with classification results"""
        response = requests.put(
            f"{self.base_url}/table/{table_name}/update",
            json={
                "column": update_col,
                "new_value": new_value,
                "where_column": where_col,
                "where_val": where_val
            }
        )
        response.raise_for_status()
        return response.json()