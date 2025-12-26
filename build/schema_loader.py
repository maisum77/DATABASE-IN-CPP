# schema_loader.py
import requests
import time

from typing import Dict, List, Any

class SchemaLoader:
    def __init__(self, base_url: str, refresh_interval: int = 30):
        """
        Args:
            base_url: C++ server URL
            refresh_interval: Auto-refresh schema every N seconds
        """
        self.base_url = base_url
        self.refresh_interval = refresh_interval
        self.last_refresh = 0
        self.schema_cache = {}
        self.table_list_cache = []
    
    def get_tables(self, force_refresh: bool = False) -> List[str]:
        """Get all table names (auto-cached)"""
        if force_refresh or self._needs_refresh():
            try:
                response = requests.get(f"{self.base_url}/tables")
                if response.status_code == 200:
                    self.table_list_cache = response.json()
                    self.last_refresh = time.time()
                else:
                    print(f"Warning: Failed to fetch tables: {response.text}")
            except Exception as e:
                print(f"Warning: Could not connect to server: {e}")
        
        return self.table_list_cache
    
    def get_schema(self, table_name: str, force_refresh: bool = False) -> Dict:
        """Get schema for specific table (cached)"""
        if force_refresh or table_name not in self.schema_cache or self._needs_refresh():
            try:
                response = requests.get(f"{self.base_url}/table/{table_name}/schema")
                if response.status_code == 200:
                    self.schema_cache[table_name] = response.json()
                else:
                    print(f"Warning: Failed to fetch schema for {table_name}: {response.text}")
                    return {"columns": [], "error": "Table not found"}
            except Exception as e:
                print(f"Warning: Could not fetch schema for {table_name}: {e}")
                return {"columns": [], "error": str(e)}
        
        return self.schema_cache[table_name]
    
    def get_full_schema(self, force_refresh: bool = False) -> Dict:
        """Get complete schema for all tables"""
        tables = self.get_tables(force_refresh)
        full_schema = {}
        
        for table in tables:
            schema = self.get_schema(table, force_refresh)
            if "columns" in schema:
                full_schema[table] = schema["columns"]
        
        return full_schema
    
    def refresh(self):
        """Manually trigger schema refresh"""
        print("🔄 Refreshing schema cache...")
        self.schema_cache.clear()
        self.table_list_cache.clear()
        self.get_tables(force_refresh=True)
        for table in self.table_list_cache:
            self.get_schema(table, force_refresh=True)
        print(f"✅ Schema refreshed: {list(self.schema.keys())}")
    
    def _needs_refresh(self) -> bool:
        """Check if cache is stale"""
        return time.time() - self.last_refresh > self.refresh_interval
    
    @property
    def schema(self):
        """Convenience property to get full schema dict"""
        return self.get_full_schema()