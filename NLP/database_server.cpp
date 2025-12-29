#include <iostream>
#include <unordered_map>
#include <vector>
#include <fstream>
#include <sstream>
#include <cctype>
#include <map>
#include <string>
#include <cstring>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <unistd.h>

using namespace std;

// ============================================================================
// STRUCT: JoinNode
// Purpose: Represents a row pair from an inner join operation
// ============================================================================
struct JoinNode
{
    int left_row;      // Index of row in the left table
    int right_row;     // Index of row in the right table
    JoinNode* next;    // Pointer to next join node
    
    JoinNode(int l, int r) : left_row(l), right_row(r), next(nullptr) {}
};

// ============================================================================
// CLASS: Table
// Purpose: Represents a database table with rows, columns, and hash indexes
// ============================================================================
class Table
{
public:
    // Data storage: form[0] contains column headers, form[1+] contains data
    vector<vector<string>> data;
    
    // Hash indexes for fast lookups: column_name -> value -> list of row indices
    unordered_map<string, unordered_map<string, vector<int>>> hash_indexes;
    
    // Primary key and foreign key column names
    string pk_column;
    string fk_column;
    
    // Indices of primary key and foreign key columns in the header row
    int pk_index;
    int fk_index;

public:
    // Constructor initializes indices and clears data
    Table() : pk_index(-1), fk_index(-1) {}

    // Set the primary key column name
    void set_primary_key(const string& column_name)
    {
        pk_column = column_name;
    }

    // Set the foreign key column name
    void set_foreign_key(const string& column_name)
    {
        fk_column = column_name;
    }

    // Add a new column to the table
    void add_column(string column_name)
    {
        if (data.empty())
        {
            // Create the header row if it doesn't exist
            data.push_back({});
        }
        
        data[0].push_back(column_name);
        
        // Update primary key index if this is the primary key column
        if (column_name == pk_column)
        {
            pk_index = static_cast<int>(data[0].size()) - 1;
        }
        
        // Update foreign key index if this is the foreign key column
        if (column_name == fk_column)
        {
            fk_index = static_cast<int>(data[0].size()) - 1;
        }
    }

    // Add a new row of data to the table
    void add_row(const vector<string>& values)
    {
        // Create a row with null placeholders for missing columns
        vector<string> row(data[0].size(), "null");
        
        // Copy values into the row
        for (int i = 0; i < values.size() && i < row.size(); i++)
        {
            row[i] = values[i];
        }
        
        data.push_back(row);
    }

    // Update a specific cell in the table
    void update(int row_index, const string& column_name, const string& new_value)
    {
        // Validate row index
        if (data.empty() || row_index < 1 || row_index >= static_cast<int>(data.size()))
        {
            cout << "[Error] Invalid row index.\n";
            return;
        }

        // Find the column index
        int column_index = find_column_index(column_name);
        
        if (column_index == -1)
        {
            cout << "[Error] Column '" << column_name << "' not found.\n";
            return;
        }

        data[row_index][column_index] = new_value;
    }

    // Find the index of a column by name
    int find_column_index(const string& column_name) const
    {
        for (int i = 0; i < static_cast<int>(data[0].size()); i++)
        {
            if (data[0][i] == column_name)
            {
                return i;
            }
        }
        return -1;
    }

    // Display the entire table to console
    void display() const
    {
        for (const auto& row : data)
        {
            for (const string& cell : row)
            {
                cout << cell << "\t";
            }
            cout << endl;
        }
    }

    // Build a hash index for a column for fast lookups
    void build_hash_index(const string& column_name)
    {
        int column_index = find_column_index(column_name);
        
        if (column_index == -1)
        {
            return;  // Column not found
        }

        // Clear existing index and rebuild
        auto& index = hash_indexes[column_name];
        index.clear();
        
        // Build index by iterating through all data rows (skip header)
        for (size_t row = 1; row < data.size(); row++)
        {
            string value = data[row][column_index];
            index[value].push_back(static_cast<int>(row));
        }
    }

    // Print a single row
    void print_row(int row_index) const
    {
        for (const string& cell : data[row_index])
        {
            cout << cell << '\t';
        }
        cout << '\n';
    }

    // Import table data from a CSV file
    bool import_csv(const string& file_name)
    {
        ifstream file(file_name);
        
        if (!file.is_open())
        {
            return false;
        }

        string line;
        bool is_first_line = true;
        
        while (getline(file, line))
        {
            if (line.empty())
            {
                continue;
            }

            // Parse the CSV line
            stringstream ss(line);
            string cell;
            vector<string> row;
            
            while (getline(ss, cell, ','))
            {
                row.push_back(cell);
            }

            if (is_first_line)
            {
                // This is the header row
                data.clear();
                data.push_back(row);
                is_first_line = false;
                
                // Rebuild primary key and foreign key indices
                for (int i = 0; i < static_cast<int>(row.size()); i++)
                {
                    if (row[i] == pk_column)
                    {
                        pk_index = i;
                    }
                    if (row[i] == fk_column)
                    {
                        fk_index = i;
                    }
                }
            }
            else
            {
                // This is a data row
                add_row(row);
            }
        }

        file.close();
        return true;
    }

    // Export table data to a CSV file
    bool export_csv(const string& file_name) const
    {
        ofstream file(file_name);
        
        if (!file.is_open())
        {
            return false;
        }

        for (const auto& row : data)
        {
            for (size_t i = 0; i < row.size(); i++)
            {
                file << row[i];
                
                if (i + 1 != row.size())
                {
                    file << ',';
                }
            }
            file << '\n';
        }

        file.close();
        return true;
    }

    // Select rows matching a condition and return them as a formatted string
    string select_where(const string& column_name, const string& operation, const string& value)
    {
        string result;
        
        if (data.empty())
        {
            return "[Error] Table is empty.\n";
        }

        // Find the column index
        int column_index = find_column_index(column_name);
        
        if (column_index == -1)
        {
            return "[Error] Column '" + column_name + "' not found.\n";
        }

        // Build result string with header
        for (const string& header : data[0])
        {
            result += header + "\t";
        }
        result += "\n";

        // For equality operations, try to use hash index
        if (operation == "=")
        {
            // Build index if it doesn't exist
            if (hash_indexes.find(column_name) == hash_indexes.end())
            {
                build_hash_index(column_name);
            }
            
            const auto& index = hash_indexes[column_name];
            auto found = index.find(value);
            
            if (found != index.end())
            {
                // Found matches using hash index
                for (int row : found->second)
                {
                    for (const string& cell : data[row])
                    {
                        result += cell + "\t";
                    }
                    result += "\n";
                }
                return result;
            }
            
            // No matches found
            return result;
        }

        // For other operations, scan all rows
        for (int row = 1; row < static_cast<int>(data.size()); row++)
        {
            string cell_value = data[row][column_index];
            bool matches = false;

            if (operation == "=")
            {
                matches = (cell_value == value);
            }
            else if (operation == ">")
            {
                matches = (stoi(cell_value) > stoi(value));
            }
            else if (operation == "<")
            {
                matches = (stoi(cell_value) < stoi(value));
            }
            else if (operation == ">=")
            {
                matches = (stoi(cell_value) >= stoi(value));
            }
            else if (operation == "<=")
            {
                matches = (stoi(cell_value) <= stoi(value));
            }
            else if (operation == "!=")
            {
                matches = (cell_value != value);
            }
            else
            {
                return "[Error] Unsupported operator: " + operation + "\n";
            }

            if (matches)
            {
                for (const string& cell : data[row])
                {
                    result += cell + "\t";
                }
                result += "\n";
            }
        }

        return result;
    }

    // Get the entire table as a formatted string
    string get_all_data() const
    {
        string result;
        
        for (const auto& row : data)
        {
            for (const string& cell : row)
            {
                result += cell + "\t";
            }
            result += "\n";
        }
        
        return result;
    }
};

// ============================================================================
// GLOBAL: Database
// Purpose: Holds all tables in the database, indexed by table name
// ============================================================================
unordered_map<string, Table> database;

// ============================================================================
// FUNCTION: execute_query
// Purpose: Parse and execute a SQL query, return results as string
// ============================================================================
string execute_query(const string& query)
{
    // Create a lowercase version for parsing
    string lower_query = query;
    
    for (char& character : lower_query)
    {
        character = tolower(character);
    }

    // Find the FROM keyword
    size_t from_position = lower_query.find("from");
    
    if (from_position == string::npos)
    {
        return "[Error] No FROM clause found.\n";
    }

    // Extract table name
    size_t where_position = lower_query.find("where", from_position);
    size_t table_start = from_position + 5;  // Position after "from "
    size_t table_end = (where_position != string::npos) ? where_position : lower_query.size();
    
    string table_name = query.substr(table_start, table_end - table_start);
    
    // Trim whitespace from table name
    size_t first_char = table_name.find_first_not_of(" \t");
    size_t last_char = table_name.find_last_not_of(" \t");
    
    if (first_char == string::npos)
    {
        return "[Error] Invalid table name.\n";
    }
    
    table_name = table_name.substr(first_char, last_char - first_char + 1);

    // Check if table exists
    auto table_iterator = database.find(table_name);
    
    if (table_iterator == database.end())
    {
        return "[Error] Table '" + table_name + "' not found.\n";
    }

    Table& target_table = table_iterator->second;

    // If no WHERE clause, return all data
    if (where_position == string::npos)
    {
        return target_table.get_all_data();
    }

    // Parse WHERE clause
    string where_clause = query.substr(where_position + 6);  // Skip "where "
    stringstream parser(where_clause);
    
    string column_name;
    string operation;
    string value;
    
    parser >> column_name >> operation >> value;

    // Remove quotes from value if present
    if (!value.empty() && (value.front() == '\'' || value.front() == '"'))
    {
        value = value.substr(1, value.size() - 2);
    }

    return target_table.select_where(column_name, operation, value);
}

// ============================================================================
// FUNCTION: create_table
// Purpose: Create a new table with the given name and columns
// ============================================================================
string create_table(const string& table_name, const vector<string>& columns)
{
    // Check if table already exists
    if (database.find(table_name) != database.end())
    {
        return "[Error] Table '" + table_name + "' already exists.\n";
    }

    Table new_table;
    
    for (const string& column : columns)
    {
        new_table.add_column(column);
    }
    
    database[table_name] = new_table;
    
    return "[OK] Table '" + table_name + "' created with " + 
           to_string(columns.size()) + " columns.\n";
}

// ============================================================================
// FUNCTION: insert_into_table
// Purpose: Insert a new row into a table
// ============================================================================
string insert_into_table(const string& table_name, const vector<string>& values)
{
    auto table_iterator = database.find(table_name);
    
    if (table_iterator == database.end())
    {
        return "[Error] Table '" + table_name + "' not found.\n";
    }

    table_iterator->second.add_row(values);
    
    return "[OK] Row inserted into '" + table_name + "'.\n";
}

// ============================================================================
// FUNCTION: inner_join_tables
// Purpose: Perform an inner join between two tables
// ============================================================================
string inner_join_tables(const string& left_table_name, const string& right_table_name)
{
    auto left_iterator = database.find(left_table_name);
    auto right_iterator = database.find(right_table_name);
    
    if (left_iterator == database.end())
    {
        return "[Error] Left table '" + left_table_name + "' not found.\n";
    }
    
    if (right_iterator == database.end())
    {
        return "[Error] Right table '" + right_table_name + "' not found.\n";
    }

    Table& left_table = left_iterator->second;
    Table& right_table = right_iterator->second;

    // Build a map of primary key values to row indices for the right table
    unordered_map<string, int> right_pk_map;
    
    for (int row = 1; row < static_cast<int>(right_table.data.size()); row++)
    {
        if (right_table.pk_index < static_cast<int>(right_table.data[row].size()))
        {
            string pk_value = right_table.data[row][right_table.pk_index];
            right_pk_map[pk_value] = row;
        }
    }

    string result;
    
    // Print combined header
    for (const string& header : left_table.data[0])
    {
        result += header + "\t";
    }
    for (const string& header : right_table.data[0])
    {
        result += header + "\t";
    }
    result += "\n";

    // Scan left table and find matching rows in right table
    for (int left_row = 1; left_row < static_cast<int>(left_table.data.size()); left_row++)
    {
        if (left_table.fk_index >= static_cast<int>(left_table.data[left_row].size()))
        {
            continue;
        }
        
        string fk_value = left_table.data[left_row][left_table.fk_index];
        auto found = right_pk_map.find(fk_value);
        
        if (found != right_pk_map.end())
        {
            int right_row = found->second;
            
            // Print combined row
            for (const string& cell : left_table.data[left_row])
            {
                result += cell + "\t";
            }
            for (const string& cell : right_table.data[right_row])
            {
                result += cell + "\t";
            }
            result += "\n";
        }
    }

    return result;
}

// ============================================================================
// FUNCTION: handle_client_request
// Purpose: Process a single client request and return the response
// ============================================================================
string handle_client_request(const string& request)
{
    string lower_request = request;
    
    // Convert to lowercase for parsing
    for (char& character : lower_request)
    {
        character = tolower(character);
    }

    // Check for CREATE TABLE command
    if (lower_request.find("create table") != string::npos)
    {
        size_t table_pos = lower_request.find("create table") + 12;
        size_t paren_pos = request.find('(', table_pos);
        
        if (paren_pos == string::npos)
        {
            return "[Error] Invalid CREATE TABLE syntax.\n";
        }

        string table_name = request.substr(table_pos, paren_pos - table_pos);
        trim_string(table_name);
        
        string columns_str = request.substr(paren_pos + 1);
        size_t paren_end = columns_str.find(')');
        
        if (paren_end != string::npos)
        {
            columns_str = columns_str.substr(0, paren_end);
        }

        vector<string> columns;
        stringstream ss(columns_str);
        string column;
        
        while (getline(ss, column, ','))
        {
            trim_string(column);
            if (!column.empty())
            {
                columns.push_back(column);
            }
        }

        return create_table(table_name, columns);
    }

    // Check for INSERT command
    if (lower_request.find("insert into") != string::npos)
    {
        size_t into_pos = lower_request.find("insert into") + 12;
        size_t values_pos = request.find("values", into_pos);
        
        if (values_pos == string::npos)
        {
            return "[Error] Invalid INSERT syntax.\n";
        }

        string table_name = request.substr(into_pos, values_pos - into_pos);
        trim_string(table_name);
        
        string values_str = request.substr(values_pos + 6);
        
        // Parse values
        vector<string> values;
        stringstream ss(values_str);
        string value;
        
        while (getline(ss, value, ','))
        {
            trim_string(value);
            // Remove quotes if present
            if (!value.empty() && value.front() == '\'')
            {
                value = value.substr(1, value.size() - 2);
            }
            values.push_back(value);
        }

        return insert_into_table(table_name, values);
    }

    // Check for JOIN command
    if (lower_request.find("join") != string::npos)
    {
        size_t join_pos = lower_request.find("join");
        size_t and_pos = lower_request.find("and", join_pos + 4);
        
        if (and_pos == string::npos)
        {
            return "[Error] Invalid JOIN syntax. Use: JOIN table1 AND table2\n";
        }

        string left_table = request.substr(join_pos + 5, and_pos - join_pos - 5);
        trim_string(left_table);
        
        string right_table = request.substr(and_pos + 4);
        trim_string(right_table);
        
        return inner_join_tables(left_table, right_table);
    }

    // Otherwise, treat as SELECT query
    return execute_query(request);
}

// ============================================================================
// FUNCTION: trim_string
// Purpose: Remove leading and trailing whitespace from a string
// ============================================================================
void trim_string(string& str)
{
    size_t start = str.find_first_not_of(" \t");
    
    if (start == string::npos)
    {
        str = "";
        return;
    }
    
    size_t end = str.find_last_not_of(" \t");
    str = str.substr(start, end - start + 1);
}

// ============================================================================
// FUNCTION: run_server
// Purpose: Start the TCP server and handle incoming connections
// ============================================================================
void run_server(int port_number)
{
    // Create socket
    int server_socket = socket(AF_INET, SOCK_STREAM, 0);
    
    if (server_socket < 0)
    {
        cout << "[Error] Failed to create socket.\n";
        return;
    }

    // Set socket options to allow address reuse
    int option = 1;
    setsockopt(server_socket, SOL_SOCKET, SO_REUSEADDR, (const char*)&option, sizeof(option));

    // Configure server address
    struct sockaddr_in server_address;
    server_address.sin_family = AF_INET;
    server_address.sin_addr.s_addr = INADDR_ANY;
    server_address.sin_port = htons(port_number);

    // Bind socket to port
    int bind_result = ::bind(server_socket, (struct sockaddr*)&server_address, sizeof(server_address));
    if (bind_result == -1)
    {
        cout << "[Error] Failed to bind to port " << port_number << ".\n";
        close(server_socket);
        return;
    }

    // Listen for connections
    listen(server_socket, 5);
    
    cout << "===========================================\n";
    cout << "   C++ Database Server Started\n";
    cout << "   Listening on port " << port_number << "\n";
    cout << "===========================================\n";

    // Buffer for receiving data
    const int buffer_size = 4096;
    char buffer[buffer_size];

    // Main server loop
    while (true)
    {
        cout << "Waiting for client connection...\n";

        struct sockaddr_in client_address;
        socklen_t client_length = sizeof(client_address);
        
        int client_socket = accept(server_socket, 
                                   (struct sockaddr*)&client_address, 
                                   &client_length);
        
        if (client_socket < 0)
        {
            cout << "[Error] Failed to accept client connection.\n";
            continue;
        }

        cout << "Client connected!\n";

        // Handle client requests
        while (true)
        {
            // Clear buffer
            memset(buffer, 0, buffer_size);
            
            // Receive data from client
            int bytes_received = recv(client_socket, buffer, buffer_size - 1, 0);
            
            if (bytes_received <= 0)
            {
                cout << "Client disconnected.\n";
                break;
            }

            buffer[bytes_received] = '\0';
            string request(buffer);
            
            cout << "Received request: " << request << "\n";

            // Process the request
            string response = handle_client_request(request);
            
            // Send response back to client
            send(client_socket, response.c_str(), response.length(), 0);
        }

        // Close client socket
        close(client_socket);
    }

    // Close server socket (never reached in this example)
    close(server_socket);
}

// ============================================================================
// FUNCTION: initialize_database
// Purpose: Load sample tables from CSV files
// ============================================================================
void initialize_database()
{
    Table employees;
    employees.set_primary_key("empID");
    employees.set_foreign_key("deptID");
    employees.import_csv("employees.csv");

    Table departments;
    departments.set_primary_key("deptID");
    departments.import_csv("departments.csv");

    database["employees"] = employees;
    database["departments"] = departments;

    cout << "Database initialized with sample data.\n";
    cout << "Tables loaded: employees, departments\n";
}

// ============================================================================
// MAIN FUNCTION
// ============================================================================
int main()
{
    // Initialize the database with sample data
    initialize_database();

    // Server port number
    int port = 8080;

    // Run the server
    run_server(port);

    return 0;
}
