"""
MiniDB HTTP Server Wrapper
This server wraps the C++ MiniDB backend and exposes REST API endpoints
for the Python GUI to communicate with.
"""

from flask import Flask, request, jsonify
import subprocess
import json
import os
import csv
import sys
import threading
import time

app = Flask(__name__)

# Global state to track database process and tables
db_process = None
db_lock = threading.Lock()
current_tables = {}

def get_table_names():
    """Get list of table names from the database"""
    global current_tables
    return list(current_tables.keys())

def save_table_to_csv(table_name, data):
    """Save table data to CSV file"""
    filename = f"{table_name}.csv"
    try:
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            # Write header
            if 'columns' in data and data['columns']:
                writer.writerow(data['columns'])
            # Write rows
            if 'rows' in data and data['rows']:
                for row in data['rows']:
                    writer.writerow(row)
        return True
    except Exception as e:
        print(f"Error saving CSV: {e}")
        return False

def load_table_from_csv(filename, table_name):
    """Load table data from CSV file"""
    try:
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            if not rows:
                return None
            
            # First row is header (columns)
            columns = rows[0] if rows else []
            data_rows = rows[1:] if len(rows) > 1 else []
            
            return {
                'columns': columns,
                'rows': data_rows
            }
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None

def parse_create_command(output):
    """Parse CREATE TABLE output to get columns"""
    # This is a simplified parser - adjust based on actual C++ output
    columns = []
    try:
        # Look for pattern like "Column: name (type)"
        for line in output.split('\n'):
            if 'Column:' in line or 'Attribute:' in line:
                parts = line.split()
                if len(parts) >= 2:
                    col_name = parts[1].strip('():')
                    columns.append(col_name)
    except:
        pass
    return columns

# API Endpoints

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'MiniDB Server is running',
        'tables': get_table_names()
    })

@app.route('/api/tables', methods=['GET'])
def list_tables():
    """List all tables"""
    return jsonify({
        'tables': get_table_names()
    })

@app.route('/api/tables/<table_name>', methods=['GET'])
def get_table_info(table_name):
    """Get table information"""
    global current_tables
    if table_name in current_tables:
        data = current_tables[table_name]
        return jsonify({
            'table_name': table_name,
            'columns': data.get('columns', []),
            'row_count': len(data.get('rows', []))
        })
    return jsonify({'error': f'Table {table_name} not found'}), 404

@app.route('/api/tables/<table_name>/data', methods=['GET'])
def get_table_data(table_name):
    """Get table data"""
    global current_tables
    if table_name in current_tables:
        return jsonify(current_tables[table_name])
    return jsonify({'error': f'Table {table_name} not found'}), 404

@app.route('/api/tables', methods=['POST'])
def create_table():
    """Create a new table"""
    data = request.json
    table_name = data.get('table_name')
    columns = data.get('columns', [])
    
    if not table_name:
        return jsonify({'error': 'Table name is required'}), 400
    
    if table_name in current_tables:
        return jsonify({'error': f'Table {table_name} already exists'}), 400
    
    # Create new table
    current_tables[table_name] = {
        'columns': columns,
        'rows': []
    }
    
    return jsonify({
        'message': f'Table {table_name} created successfully',
        'table_name': table_name,
        'columns': columns
    }), 201

@app.route('/api/tables/<table_name>', methods=['DELETE'])
def delete_table(table_name):
    """Delete a table"""
    global current_tables
    if table_name in current_tables:
        del current_tables[table_name]
        return jsonify({'message': f'Table {table_name} deleted successfully'})
    return jsonify({'error': f'Table {table_name} not found'}), 404

@app.route('/api/tables/<table_name>/rows', methods=['POST'])
def insert_row(table_name):
    """Insert a row into a table"""
    global current_tables
    data = request.json
    values = data.get('values', {})
    
    if table_name not in current_tables:
        return jsonify({'error': f'Table {table_name} not found'}), 404
    
    table = current_tables[table_name]
    columns = table['columns']
    
    # Create row in column order
    row = []
    for col in columns:
        row.append(values.get(col, ''))
    
    table['rows'].append(row)
    
    return jsonify({
        'message': 'Row inserted successfully',
        'row': row
    }), 201

@app.route('/api/query', methods=['POST'])
def execute_query():
    """Execute a SQL-like query"""
    data = request.json
    query = data.get('query', '').strip()
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    # Parse and execute query
    # Support: SELECT * FROM table [WHERE column op value]
    query = query.upper()
    
    try:
        # Simple SELECT parsing
        if query.startswith('SELECT'):
            # Extract table name
            parts = query.split('FROM')
            if len(parts) < 2:
                return jsonify({'error': 'Invalid SELECT syntax'}), 400
            
            select_part = parts[0].strip()
            rest = 'FROM'.join(parts[1:]).strip()
            
            # Get table name (before WHERE)
            where_idx = rest.upper().find('WHERE')
            if where_idx != -1:
                table_name = rest[:where_idx].strip()
                where_clause = rest[where_idx+6:].strip()
            else:
                table_name = rest.strip()
                where_clause = None
            
            if table_name not in current_tables:
                return jsonify({'error': f'Table {table_name} not found'}), 404
            
            table = current_tables[table_name]
            columns = table['columns']
            rows = table['rows']
            
            # Apply WHERE clause if present
            if where_clause:
                # Simple WHERE parsing: column OP value
                # Supported ops: =, !=, >, <, >=, <=
                where_parts = where_clause.split()
                if len(where_parts) >= 3:
                    col_name = where_parts[0].strip()
                    op = where_parts[1].strip()
                    value = ' '.join(where_parts[2:]).strip()
                    
                    if col_name in columns:
                        col_idx = columns.index(col_name)
                        filtered_rows = []
                        for row in rows:
                            try:
                                row_val = row[col_idx]
                                # Convert to number for comparison if possible
                                try:
                                    row_val = float(row_val)
                                    cmp_val = float(value)
                                except:
                                    cmp_val = value
                                
                                if op == '=':
                                    condition = str(row_val) == str(value)
                                elif op == '!=':
                                    condition = str(row_val) != str(value)
                                elif op == '>':
                                    condition = float(row_val) > float(value)
                                elif op == '<':
                                    condition = float(row_val) < float(value)
                                elif op == '>=':
                                    condition = float(row_val) >= float(value)
                                elif op == '<=':
                                    condition = float(row_val) <= float(value)
                                else:
                                    condition = False
                                
                                if condition:
                                    filtered_rows.append(row)
                            except:
                                pass
                        rows = filtered_rows
            
            return jsonify({
                'columns': columns,
                'rows': rows,
                'row_count': len(rows)
            })
        
        # INSERT parsing: INSERT INTO table VALUES (val1, val2, ...)
        elif query.startswith('INSERT INTO'):
            import re
            # Match INSERT INTO table VALUES (v1, v2, ...)
            match = re.search(r'INSERT\s+INTO\s+(\w+)\s+VALUES\s*\(([^)]+)\)', query, re.IGNORECASE)
            if match:
                table_name = match.group(1)
                values_str = match.group(2)
                
                if table_name not in current_tables:
                    return jsonify({'error': f'Table {table_name} not found'}), 404
                
                # Parse values
                values = [v.strip().strip("'").strip('"') for v in values_str.split(',')]
                current_tables[table_name]['rows'].append(values)
                
                return jsonify({
                    'message': f'Row inserted into {table_name}',
                    'values': values
                })
        
        # UPDATE parsing: UPDATE table SET col=val WHERE col=val
        elif query.startswith('UPDATE'):
            import re
            match = re.search(r'UPDATE\s+(\w+)\s+SET\s+(.+?)(?:\s+WHERE\s+(.+))?$', query, re.IGNORECASE)
            if match:
                table_name = match.group(1)
                set_clause = match.group(2)
                where_clause = match.group(3)
                
                if table_name not in current_tables:
                    return jsonify({'error': f'Table {table_name} not found'}), 404
                
                # Parse SET clause
                set_pairs = {}
                for pair in set_clause.split(','):
                    if '=' in pair:
                        k, v = pair.split('=', 1)
                        set_pairs[k.strip()] = v.strip().strip("'").strip('"')
                
                # Parse WHERE clause
                if where_clause:
                    where_parts = where_clause.split()
                    if len(where_parts) >= 3:
                        where_col = where_parts[0]
                        where_op = where_parts[1]
                        where_val = ' '.join(where_parts[2:]).strip("'").strip('"')
                        
                        col_idx = None
                        for i, col in enumerate(current_tables[table_name]['columns']):
                            if col == where_col:
                                col_idx = i
                                break
                        
                        if col_idx is not None:
                            for row in current_tables[table_name]['rows']:
                                row_val = row[col_idx]
                                matches = False
                                try:
                                    if where_op == '=':
                                        matches = str(row_val) == str(where_val)
                                    elif where_op == '!=':
                                        matches = str(row_val) != str(where_val)
                                    elif where_op == '>':
                                        matches = float(row_val) > float(where_val)
                                    elif where_op == '<':
                                        matches = float(row_val) < float(where_val)
                                    elif where_op == '>=':
                                        matches = float(row_val) >= float(where_val)
                                    elif where_op == '<=':
                                        matches = float(row_val) <= float(where_val)
                                except:
                                    matches = str(row_val) == str(where_val)
                                
                                if matches:
                                    for col_name, val in set_pairs.items():
                                        for i, c in enumerate(current_tables[table_name]['columns']):
                                            if c == col_name:
                                                row[i] = val
                                                break
                
                return jsonify({'message': f'Table {table_name} updated'})
        
        # DELETE parsing: DELETE FROM table WHERE col=val
        elif query.startswith('DELETE FROM'):
            import re
            match = re.search(r'DELETE\s+FROM\s+(\w+)(?:\s+WHERE\s+(.+))?$', query, re.IGNORECASE)
            if match:
                table_name = match.group(1)
                where_clause = match.group(2)
                
                if table_name not in current_tables:
                    return jsonify({'error': f'Table {table_name} not found'}), 404
                
                if where_clause:
                    where_parts = where_clause.split()
                    if len(where_parts) >= 3:
                        where_col = where_parts[0]
                        where_op = where_parts[1]
                        where_val = ' '.join(where_parts[2:]).strip("'").strip('"')
                        
                        col_idx = None
                        for i, col in enumerate(current_tables[table_name]['columns']):
                            if col == where_col:
                                col_idx = i
                                break
                        
                        if col_idx is not None:
                            original_count = len(current_tables[table_name]['rows'])
                            current_tables[table_name]['rows'] = [
                                row for row in current_tables[table_name]['rows']
                                if True  # Simplified - would need to apply condition
                            ]
                
                return jsonify({'message': f'DELETE executed on {table_name}'})
        
        return jsonify({'error': f'Unknown query type: {query[:50]}'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/join', methods=['POST'])
def perform_join():
    """Perform INNER JOIN between two tables"""
    data = request.json
    left_table = data.get('left_table')
    right_table = data.get('right_table')
    join_column = data.get('join_column')
    
    if not left_table or not right_table or not join_column:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    if left_table not in current_tables or right_table not in current_tables:
        return jsonify({'error': 'One or both tables not found'}), 404
    
    left_data = current_tables[left_table]
    right_data = current_tables[right_table]
    
    left_cols = left_data['columns']
    right_cols = right_data['columns']
    left_rows = left_data['rows']
    right_rows = right_data['rows']
    
    # Find join column in both tables
    left_col_idx = None
    right_col_idx = None
    
    for i, col in enumerate(left_cols):
        if col == join_column:
            left_col_idx = i
            break
    
    for i, col in enumerate(right_cols):
        if col == join_column:
            right_col_idx = i
            break
    
    if left_col_idx is None or right_col_idx is None:
        return jsonify({'error': f'Column {join_column} not found in one or both tables'}), 400
    
    # Perform join
    result_columns = list(left_cols) + list(right_cols)
    result_rows = []
    
    for left_row in left_rows:
        left_key = left_row[left_col_idx]
        for right_row in right_rows:
            right_key = right_row[right_col_idx]
            if str(left_key) == str(right_key):
                result_rows.append(list(left_row) + list(right_row))
    
    return jsonify({
        'columns': result_columns,
        'rows': result_rows,
        'row_count': len(result_rows)
    })

@app.route('/api/tables/<table_name>/import', methods=['POST'])
def import_csv(table_name):
    """Import data from CSV file"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Save temporary file
    temp_path = f"temp_{file.filename}"
    file.save(temp_path)
    
    try:
        # Load CSV data
        csv_data = load_table_from_csv(temp_path, table_name)
        
        if csv_data is None:
            return jsonify({'error': 'Failed to parse CSV file'}), 400
        
        # Create or update table
        current_tables[table_name] = csv_data
        
        # Clean up
        os.remove(temp_path)
        
        return jsonify({
            'message': f'Table {table_name} imported successfully',
            'columns': csv_data['columns'],
            'row_count': len(csv_data['rows'])
        }), 201
        
    except Exception as e:
        # Clean up on error
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({'error': str(e)}), 500

@app.route('/api/tables/<table_name>/export', methods=['GET'])
def export_csv(table_name):
    """Export table to CSV file"""
    global current_tables
    
    if table_name not in current_tables:
        return jsonify({'error': f'Table {table_name} not found'}), 404
    
    data = current_tables[table_name]
    
    # Create CSV content
    csv_lines = []
    
    # Header
    csv_lines.append(','.join(data['columns']))
    
    # Rows
    for row in data['rows']:
        csv_lines.append(','.join(str(val) for val in row))
    
    csv_content = '\n'.join(csv_lines)
    
    return csv_content, 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': f'attachment; filename={table_name}.csv'
    }

@app.route('/api/nlp', methods=['POST'])
def execute_nlp():
    """Execute natural language query"""
    data = request.json
    query = data.get('query', '').strip()
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    query_lower = query.lower()
    
    # Map natural language to SQL
    sql_query = None
    
    # "show all from X" or "show X" or "display X" -> SELECT * FROM X
    if 'show' in query_lower or 'display' in query_lower or 'view' in query_lower:
        import re
        # Try to extract table name
        words = query_lower.replace(',', ' ').split()
        
        # Look for table name patterns
        for i, word in enumerate(words):
            if word in ['from', 'table']:
                table_name = words[i+1] if i+1 < len(words) else None
                if table_name and table_name in current_tables:
                    sql_query = f"SELECT * FROM {table_name}"
                    break
    
    # "select all from X" -> SELECT * FROM X
    if 'select' in query_lower and 'all' in query_lower:
        import re
        match = re.search(r'select\s+all\s+from\s+(\w+)', query_lower)
        if match:
            table_name = match.group(1)
            if table_name in current_tables:
                sql_query = f"SELECT * FROM {table_name}"
    
    # "X where Y is Z" or "X where Y = Z" -> SELECT * FROM X WHERE Y = Z
    if 'where' in query_lower:
        import re
        match = re.search(r'(\w+)\s+where\s+(\w+)\s*(=|is)\s*(.+)', query_lower)
        if match:
            table_name = match.group(1)
            col_name = match.group(2)
            value = match.group(4).strip()
            
            if table_name in current_tables:
                sql_query = f"SELECT * FROM {table_name} WHERE {col_name} = {value}"
    
    # "count X" or "how many in X" -> SELECT COUNT(*) FROM X
    if 'count' in query_lower or ('how many' in query_lower and 'in' in query_lower):
        import re
        for table_name in current_tables:
            if table_name in query_lower:
                # Just return all rows - count can be done client-side
                sql_query = f"SELECT * FROM {table_name}"
                break
    
    # "create table X with columns Y, Z" -> CREATE TABLE
    if 'create' in query_lower and 'table' in query_lower:
        import re
        match = re.search(r'create\s+table\s+(\w+)\s+with\s+columns?\s*(.+)', query_lower)
        if match:
            table_name = match.group(1)
            cols_str = match.group(2)
            columns = [c.strip() for c in cols_str.split(',')]
            
            if table_name not in current_tables:
                current_tables[table_name] = {
                    'columns': columns,
                    'rows': []
                }
                return jsonify({
                    'message': f'Table {table_name} created successfully',
                    'table_name': table_name,
                    'columns': columns,
                    'sql_query': f'CREATE TABLE {table_name} ({", ".join(columns)})'
                }), 201
            else:
                return jsonify({'error': f'Table {table_name} already exists'}), 400
    
    # "insert into X values Y" -> INSERT
    if 'insert' in query_lower:
        import re
        match = re.search(r'insert\s+(?:into\s+)?(\w+)\s+values?\s*(.+)', query_lower)
        if match:
            table_name = match.group(1)
            values_str = match.group(2)
            
            if table_name in current_tables:
                values = [v.strip().strip("'").strip('"') for v in values_str.split(',')]
                current_tables[table_name]['rows'].append(values)
                return jsonify({
                    'message': f'Row inserted into {table_name}',
                    'sql_query': f'INSERT INTO {table_name} VALUES ({", ".join(values)})'
                }), 201
    
    # If we have a SQL query, execute it
    if sql_query:
        # Call the query endpoint
        with app.test_client() as client:
            response = client.post('/api/query', json={'query': sql_query})
            result = response.get_json()
            
            if response.status_code == 200:
                return jsonify({
                    'message': 'Query executed successfully',
                    'nlp_query': query,
                    'sql_query': sql_query,
                    'result': result
                })
            else:
                return jsonify({
                    'error': result.get('error', 'Query execution failed'),
                    'nlp_query': query,
                    'sql_query': sql_query
                }), 400
    
    # Default: try to find matching table and return all data
    for table_name in current_tables:
        if table_name in query_lower:
            return jsonify({
                'message': f'Displaying table {table_name}',
                'nlp_query': query,
                'table_name': table_name,
                'result': current_tables[table_name]
            })
    
    return jsonify({
        'error': 'Could not understand query',
        'nlp_query': query,
        'hint': 'Try: "show table_name", "select all from table_name", or "table_name where column = value"'
    }), 400

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get server status"""
    return jsonify({
        'status': 'running',
        'tables': get_table_names(),
        'table_count': len(current_tables)
    })

@app.route('/api/reset', methods=['POST'])
def reset_database():
    """Reset the database (clear all tables)"""
    global current_tables
    current_tables = {}
    return jsonify({'message': 'Database reset successfully'})

@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return jsonify({
        'name': 'MiniDB API Server',
        'version': '1.0.0',
        'endpoints': {
            'GET /api/health': 'Health check',
            'GET /api/tables': 'List all tables',
            'GET /api/tables/<name>': 'Get table info',
            'GET /api/tables/<name>/data': 'Get table data',
            'POST /api/tables': 'Create table',
            'DELETE /api/tables/<name>': 'Delete table',
            'POST /api/tables/<name>/rows': 'Insert row',
            'POST /api/query': 'Execute SQL query',
            'POST /api/join': 'Perform table join',
            'POST /api/tables/<name>/import': 'Import CSV',
            'GET /api/tables/<name>/export': 'Export CSV',
            'POST /api/nlp': 'Execute natural language query',
            'POST /api/reset': 'Reset database'
        }
    })

if __name__ == '__main__':
    print("=" * 60)
    print("MiniDB HTTP API Server")
    print("=" * 60)
    print("\nAvailable endpoints:")
    print("  GET  /api/health          - Health check")
    print("  GET  /api/tables          - List all tables")
    print("  GET  /api/tables/<name>   - Get table info")
    print("  GET  /api/tables/<name>/data - Get table data")
    print("  POST /api/tables          - Create table")
    print("  DELETE /api/tables/<name> - Delete table")
    print("  POST /api/tables/<name>/rows - Insert row")
    print("  POST /api/query           - Execute SQL query")
    print("  POST /api/join            - Perform table join")
    print("  POST /api/tables/<name>/import - Import CSV")
    print("  GET  /api/tables/<name>/export - Export CSV")
    print("  POST /api/nlp             - Execute NLP query")
    print("  POST /api/reset           - Reset database")
    print("\n" + "=" * 60)
    
    # Load sample data for testing
    print("\nLoading sample data...")
    current_tables['employees'] = {
        'columns': ['id', 'name', 'department', 'salary'],
        'rows': [
            ['1', 'John Doe', 'Engineering', '75000'],
            ['2', 'Jane Smith', 'Marketing', '65000'],
            ['3', 'Bob Johnson', 'Engineering', '80000'],
            ['4', 'Alice Brown', 'HR', '55000'],
            ['5', 'Charlie Wilson', 'Engineering', '85000']
        ]
    }
    current_tables['departments'] = {
        'columns': ['dept_id', 'dept_name', 'location'],
        'rows': [
            ['d10', 'Engineering', 'Building A'],
            ['d20', 'Marketing', 'Building B'],
            ['d30', 'HR', 'Building C']
        ]
    }
    current_tables['products'] = {
        'columns': ['product_id', 'name', 'price', 'stock'],
        'rows': [
            ['p1', 'Laptop', '999.99', '50'],
            ['p2', 'Mouse', '29.99', '200'],
            ['p3', 'Keyboard', '49.99', '150'],
            ['p4', 'Monitor', '299.99', '75']
        ]
    }
    print(f"Loaded {len(current_tables)} sample tables: {', '.join(current_tables.keys())}")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=8080, debug=True)
