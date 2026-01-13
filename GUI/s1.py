"""
MiniDB HTTP Server Wrapper
This server wraps the C++ MiniDB backend and exposes REST API endpoints
for the Python GUI to communicate with.
"""

from flask import Flask, request, jsonify
import json
import os
import csv
import threading

app = Flask(__name__)

# Global state to track database process and tables
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
        with open(filename, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            rows = list(reader)
            
            if not rows:
                print(f"CSV file is empty: {filename}")
                return None
            
            # First row is header (columns)
            columns = rows[0] if rows else []
            columns = [col.strip() for col in columns if col.strip()]
            
            if not columns:
                return None
            
            # Data rows (skip header)
            data_rows = rows[1:] if len(rows) > 1 else []
            cleaned_rows = []
            
            for row in data_rows:
                # Skip empty rows
                if not row or all(not cell.strip() for cell in row):
                    continue
                # Normalize row length
                if len(row) != len(columns):
                    while len(row) < len(columns):
                        row.append('')
                    row = row[:len(columns)]
                cleaned_rows.append(row)
            
            return {
                'columns': columns,
                'rows': cleaned_rows
            }
    except Exception as e:
        print(f"Error loading CSV {filename}: {e}")
        return None

# API Endpoints

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'message': 'MiniDB Server is running',
        'tables': get_table_names()
    })

@app.route('/api/tables', methods=['GET'])
def list_tables():
    return jsonify({'tables': get_table_names()})

@app.route('/api/tables/<table_name>', methods=['GET'])
def get_table_info(table_name):
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
    global current_tables
    if table_name in current_tables:
        return jsonify(current_tables[table_name])
    return jsonify({'error': f'Table {table_name} not found'}), 404

@app.route('/api/tables', methods=['POST'])
def create_table():
    data = request.json
    table_name = data.get('table_name')
    columns = data.get('columns', [])
    
    if not table_name:
        return jsonify({'error': 'Table name is required'}), 400
    
    if table_name in current_tables:
        return jsonify({'error': f'Table {table_name} already exists'}), 400
    
    current_tables[table_name] = {'columns': columns, 'rows': []}
    return jsonify({'message': f'Table {table_name} created successfully'}), 201

@app.route('/api/tables/<table_name>', methods=['DELETE'])
def delete_table(table_name):
    global current_tables
    if table_name in current_tables:
        del current_tables[table_name]
        return jsonify({'message': f'Table {table_name} deleted successfully'})
    return jsonify({'error': f'Table {table_name} not found'}), 404

# --- FIX: Added Import Route ---
@app.route('/api/tables/<table_name>/import', methods=['POST'])
def import_table(table_name):
    """Import a CSV file into a table"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file:
        filename = f"{table_name}_temp.csv"
        try:
            file.save(filename)
            data = load_table_from_csv(filename, table_name)
            
            if data:
                global current_tables
                current_tables[table_name] = data
                if os.path.exists(filename):
                    os.remove(filename)
                return jsonify({
                    'message': f'Table {table_name} imported successfully',
                    'columns': data['columns'],
                    'row_count': len(data['rows'])
                })
            else:
                if os.path.exists(filename):
                    os.remove(filename)
                return jsonify({'error': 'Failed to parse CSV file'}), 400
        except Exception as e:
            if os.path.exists(filename):
                os.remove(filename)
            return jsonify({'error': str(e)}), 500

@app.route('/api/query', methods=['POST'])
def execute_query():
    """Execute a SQL-like query"""
    data = request.json
    query = data.get('query', '').strip().upper()
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
        
    try:
        if query.startswith('SELECT'):
            parts = query.split('FROM')
            if len(parts) < 2:
                return jsonify({'error': 'Invalid SELECT syntax'}), 400
            
            # Simple parsing for FROM <table> WHERE <col> = <val>
            rest = parts[1].strip()
            where_idx = rest.find('WHERE')
            
            if where_idx != -1:
                table_name = rest[:where_idx].strip()
                # Basic WHERE logic would go here
            else:
                table_name = rest.strip()
                
            if table_name not in current_tables:
                return jsonify({'error': f'Table {table_name} not found'}), 404
                
            return jsonify(current_tables[table_name])
            
        return jsonify({'error': 'Only SELECT queries are supported in this demo'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Load some sample data
    current_tables['employees'] = {
        'columns': ['id', 'name', 'dept', 'salary'],
        'rows': [['1', 'John', 'IT', '5000'], ['2', 'Jane', 'HR', '4500']]
    }
    print("MiniDB HTTP API Server running on port 8080...")
    app.run(host='0.0.0.0', port=8080, debug=True)