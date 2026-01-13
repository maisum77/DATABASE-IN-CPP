# MiniDB - C++ Database Engine with Python Interface

## Complete Documentation

MiniDB is a lightweight, high-performance in-memory database system implemented in C++, featuring a modern Python GUI and REST API interface. This comprehensive documentation covers all aspects of the system, from installation and architecture to advanced usage scenarios and API references.

---

## 1. Project Overview

### 1.1 Introduction to MiniDB

MiniDB represents a sophisticated implementation of a relational database management system entirely in C++, providing users with the foundational capabilities expected from a database engine while maintaining simplicity for educational purposes and rapid prototyping. The system operates entirely in memory, delivering exceptional performance for read-heavy workloads and interactive data manipulation tasks. Unlike traditional databases that require complex installation procedures and configuration, MiniDB runs out-of-the-box with minimal dependencies, making it an ideal choice for developers, students, and researchers who need a quick and reliable data storage solution.

The architecture of MiniDB consists of three distinct layers that work together seamlessly. The foundation layer is the C++ database engine, which handles all core database operations including table management, indexing, query processing, and join operations. This engine is implemented using modern C++ features and the Standard Template Library, ensuring type safety and efficient memory usage. The middle layer is a Python-based HTTP server built with Flask, which exposes the database functionality through a comprehensive REST API. This abstraction allows the database to be accessed from various clients, including the included graphical user interface, web applications, or any other system capable of making HTTP requests. The top layer is the Python GUI application, which provides an intuitive and visually appealing interface for interacting with the database without requiring knowledge of SQL or programming.

MiniDB distinguishes itself from other database solutions through several key characteristics. The zero-configuration nature means that users can begin working with the database immediately after installation, without the need to set up database servers, configure connection strings, or manage background services. The in-memory architecture provides lightning-fast data access speeds, as all operations occur directly in RAM without the overhead of disk I/O. The comprehensive feature set includes support for creating and managing tables, inserting and updating records, executing SQL-like queries with various comparison operators, performing inner joins between related tables, and importing or exporting data in CSV format. Additionally, the system includes natural language processing capabilities that allow users to query their data using plain English sentences rather than strict SQL syntax.

### 1.2 Project Structure and Organization

The MiniDB repository is organized into several directories, each serving a specific purpose within the overall system architecture. Understanding this structure is essential for developers who wish to extend the system or understand how the components interact with one another.

The root directory contains essential project files including the LICENSE file specifying the terms of use, the requirements.txt file listing Python dependencies, and the main README documentation. This directory also serves as the entry point for understanding the project's purpose and basic usage instructions.

The `GUI` directory contains all components related to the graphical user interface and the HTTP server. Within this directory, the `server.py` file implements a Flask-based HTTP server that provides a REST API for database operations. This server acts as an intermediary between the GUI client and the underlying data structures, handling request parsing, data transformation, and response formatting. The `gui.py` file contains the complete implementation of the Tkinter-based desktop application, including all UI components, event handlers, and API communication logic. The GUI features a modern dark-themed design with intuitive navigation, real-time data visualization, and comprehensive table management capabilities.

The `NLP` directory houses natural language processing utilities that enable users to interact with the database using conversational queries. This component translates natural language sentences into executable SQL queries, making the database accessible to users without technical database knowledge. The files in this directory include the SQL translator, database client and server implementations for the NLP system, and various test files demonstrating different query patterns.

The `build` directory contains CMake configuration files and build outputs for users who prefer to compile the C++ components using CMake. This directory includes the CMakeLists.txt file defining the build configuration, generated Makefiles, and the compiled database executable. The presence of sample CSV files in this directory allows for testing the build process with real data.

The `src` directory contains the core C++ source files for the database engine. The `main.cpp` file contains the complete implementation of the table class, query processing logic, join algorithms, and the interactive command-line interface. Additional CSV data files in this directory provide sample datasets for testing and demonstration purposes.

The `data_insight` directory contains advanced data analysis and visualization components, including utilities for fetching data, generating insights, and creating visual representations of database contents. These components extend the basic database functionality with analytical capabilities useful for data exploration and reporting.

The `web` directory contains web interface components for users who prefer to access MiniDB through a browser-based interface. The HTML and JavaScript files in this directory implement a responsive web client that communicates with the backend server.

The `doc` directory contains supplementary documentation, including this comprehensive guide and any additional reference materials that describe specific aspects of the system in greater detail.

### 1.3 Key Features and Capabilities

MiniDB provides a comprehensive set of database management features that address the most common data manipulation scenarios while maintaining simplicity and ease of use. The following sections describe the major capabilities of the system in detail.

The table management capabilities allow users to create, view, and delete database tables through both the command-line interface and the graphical user interface. Each table consists of a schema defining column names and a collection of data rows containing values for each column. The system supports arbitrary column configurations, allowing users to define tables that match their specific data requirements. Tables can be populated with data through direct insertion, CSV import, or programmatically through the API.

The query processing system supports a SQL-like syntax for retrieving and filtering data from tables. Users can specify which columns to retrieve, which table to query from, and what conditions must be met for rows to be included in the results. The supported comparison operators include equality, inequality, greater than, less than, greater than or equal to, and less than or equal to. The query parser automatically optimizes equality comparisons by leveraging hash-based indexes when available, resulting in significantly faster query execution for matching queries.

The indexing system uses hash-based data structures to accelerate query execution for equality conditions. When a column is frequently used in equality comparisons, the system can build a hash index that maps column values to the row indices where those values appear. This optimization reduces query complexity from linear search O(n) to constant-time hash lookup O(1) plus iteration over matching rows, providing substantial performance improvements for selective queries on large tables.

The join operation implements inner join functionality between two tables based on primary key and foreign key relationships. This capability allows users to combine related data stored in separate tables, demonstrating fundamental relational database concepts. The join algorithm efficiently matches rows by leveraging hash indexes on primary key columns, producing combined results that show data from both source tables in a single view.

The CSV import and export functionality enables data exchange between MiniDB and external systems. Importing CSV files allows existing datasets to be loaded into the database for analysis and manipulation, while exporting tables to CSV format preserves data for use in spreadsheet applications or other programs. This feature is particularly valuable for data migration scenarios and for integrating MiniDB with existing data pipelines.

The natural language query system provides an alternative interface for retrieving data using conversational English sentences rather than formal SQL syntax. This capability makes the database accessible to users without technical database knowledge, allowing them to ask questions about their data in plain language. The NLP system parses natural language queries, identifies the relevant tables and columns, and generates equivalent SQL queries that are executed against the database.

---

## 2. Installation and Setup

### 2.1 Prerequisites and System Requirements

Before installing and running MiniDB, ensure that your development environment meets the following requirements. These prerequisites are essential for compiling the C++ components and running the Python-based server and GUI interface.

The system requires a C++ compiler supporting the C++11 standard or newer. The GNU Compiler Collection (GCC) with g++ version 4.8 or higher, Clang version 3.3 or higher, and Microsoft Visual C++ 2015 or higher all satisfy this requirement. The compiler is necessary for building the C++ database engine components if you choose to compile them separately. Most modern development environments include a compatible C++ compiler by default.

Python version 3.6 or higher is required to run the server and GUI components. The system has been tested with Python 3.8, 3.9, 3.10, and 3.11, and should work with newer versions as well. Python is available for all major operating systems and can be downloaded from the official Python website or installed through package managers such as Homebrew, apt, or winget.

The Python package manager pip is required to install the dependencies listed in the requirements.txt file. Pip is typically included with standard Python installations, but can be installed separately if needed. The command `pip --version` can be used to verify that pip is available on your system.

For the graphical user interface, a display environment capable of running Tkinter applications is required. Tkinter is included with most Python installations, but some minimal Linux installations may require installing the tk package through the system package manager.

### 2.2 Obtaining the Source Code

The MiniDB source code is hosted on GitHub at the repository location specified in the project description. You can obtain a copy of the codebase by either downloading a ZIP archive or cloning the repository using Git. Cloning the repository provides additional benefits including easy updates from the upstream project and the ability to track your own modifications separately.

To clone the repository using Git, open a terminal or command prompt and execute the following command:

```bash
git clone https://github.com/maisum77/DATABASE-IN-CPP.git
cd DATABASE-IN-CPP
```

This command creates a new directory named `DATABASE-IN-CPP` containing all project files. The clone operation preserves the full Git history, allowing you to examine previous versions, create branches for your own development, and easily integrate updates from the original repository.

After cloning, explore the repository structure to familiarize yourself with the organization. The main C++ source code is located in the `src` directory, the Python server and GUI components are in the `GUI` directory, and sample data files are distributed throughout the project to facilitate testing and demonstration.

### 2.3 Installing Python Dependencies

The Python components of MiniDB depend on several third-party packages that must be installed before running the server or GUI. These dependencies are listed in the `requirements.txt` file located in the root directory of the repository.

The Flask framework is required for the HTTP server component. Flask provides the routing, request handling, and response formatting capabilities needed to expose the database functionality through a REST API. The framework is lightweight and easy to use, making it ideal for the MiniDB server implementation.

The Requests library is required by the GUI component to communicate with the backend server. Requests simplifies HTTP client operations, providing intuitive methods for sending GET and POST requests and handling responses. The GUI uses this library to interact with the Flask server, sending queries and receiving results for display.

To install these dependencies, navigate to the repository root directory and execute the following command:

```bash
pip install -r requirements.txt
```

This command reads the requirements.txt file and installs all listed packages along with their dependencies. The installation process may take a few moments as pip downloads and compiles the required packages. After installation completes, you can verify that the dependencies are available by importing them in a Python shell.

### 2.4 Directory Structure for Data Files

MiniDB expects certain data files to be present in the appropriate directories for the demonstration data to load automatically when the server starts. The sample data files include employee records and department information that demonstrate the system's capabilities.

The `employees.csv` file in the `src` directory contains 20,000 employee records, each with an employee ID, name, age, and department ID. This large dataset is useful for testing query performance and demonstrating the system's ability to handle substantial data volumes. The file follows standard CSV format with a header row defining column names and subsequent rows containing data values.

The `departments.csv` file in the `src` directory contains department information including department ID, name, and location. This data demonstrates relationships between tables through the department ID field that appears in both the employees and departments tables.

When the server starts, it automatically loads these CSV files into in-memory tables if they are present in the working directory. This automatic loading provides immediate access to example data for exploration and testing without requiring manual table creation or data entry.

---

## 3. Running the Application

### 3.1 Starting the Server

The MiniDB system consists of two main components that must be started in sequence: the HTTP server and the graphical user interface. The server must be running before the GUI can connect to it, as the GUI depends on the server's REST API to perform all database operations.

To start the server, navigate to the `GUI` directory within the repository and execute the server.py script using Python:

```bash
cd GUI
python server.py
```

When the server starts successfully, it displays a banner showing the available API endpoints and loads the sample data files. The server runs on port 8080 by default and listens for incoming connections from any network interface. The output confirms that the server is running and ready to accept requests.

The server maintains all database state in memory during execution. When sample data files are present in the working directory, they are automatically loaded into tables named `employees` and `departments`. The server also creates additional sample tables including `products` that demonstrate various data types and structures.

The Flask server provides a comprehensive REST API with endpoints for all major database operations. The API supports table listing and retrieval, table creation and deletion, row insertion, SQL query execution, table joins, CSV import and export, natural language query processing, and database reset operations. Each endpoint accepts and returns JSON-formatted data, making it easy to integrate with other systems or test using command-line tools.

While the server is running, it logs all incoming requests to the console, showing the HTTP method, endpoint URL, request data, and response status. This logging is useful for debugging and for understanding how the GUI communicates with the backend. The server continues running until it is explicitly stopped by pressing `Ctrl+C` or by killing the process.

### 3.2 Starting the Graphical User Interface

After the server is running, open a new terminal window and start the GUI application. The GUI connects to the server on localhost port 8080 and provides an intuitive interface for all database operations.

To start the GUI, navigate to the `GUI` directory and execute the gui.py script:

```bash
cd GUI
python gui.py
```

Upon starting, the GUI displays a welcome screen with information about the database system. The application attempts to connect to the server automatically, and a connection status indicator shows whether the connection was successful. If the connection fails, the GUI provides detailed troubleshooting instructions including checking that the server is running and verifying the correct port number.

The GUI interface features a modern dark theme with a sidebar navigation panel and a main content area that changes based on the selected operation. The navigation panel provides access to all major features including the home dashboard, connection testing, table management, SQL query execution, natural language queries, table creation, CSV import and export, table joins, settings, and about information.

When connected to a running server, the GUI loads the list of available tables and displays statistics about the current database state. The status bar at the bottom of the window shows the connection status, current time, and table count. The interface supports keyboard shortcuts for common operations and provides contextual help through tooltips and information dialogs.

### 3.3 Verifying the Installation

After starting both the server and GUI, verify that the system is functioning correctly by performing a few basic operations. Navigate to the Tables section of the GUI to see the list of automatically loaded tables. The `employees` table should appear with approximately 20,000 records, the `departments` table with department information, and the `products` table with sample product data.

Click on the `employees` table to view its contents. The table viewer displays column headers and rows of data in a scrollable grid. You can sort the data by clicking on column headers and filter rows using the search functionality. Verify that the data matches the expected structure with columns for employee ID, name, age, and department ID.

Execute a simple SQL query to test the query processing system. Navigate to the SQL Query section and enter a query such as `SELECT * FROM employees WHERE age > 50`. The query results should display all employees older than 50, demonstrating the system's ability to filter data based on conditions. The results include a count of matching rows and display the data in a formatted table.

Test the natural language query interface by entering a conversational query such as "Show me all employees from Engineering". The NLP system should translate this query into SQL and return matching results. This feature demonstrates how users can interact with the database without learning SQL syntax.

Perform a table join operation to verify that the relational capabilities are working correctly. Navigate to the Join section, select `employees` as the left table, `departments` as the right table, and specify `deptID` as the join column. The join results should display combined data from both tables, showing employee information alongside their department details.

---

## 4. Architecture and Design

### 4.1 System Architecture Overview

MiniDB implements a three-tier architecture that separates concerns and enables flexible system configuration. Understanding this architecture is valuable for developers who wish to extend the system or integrate it with other applications.

The first tier is the C++ Database Engine, which provides the core data management functionality. This tier is implemented entirely in C++ using the Standard Template Library for container and algorithm support. The engine handles table storage using nested vectors, maintains hash indexes for query optimization, implements the query parser and execution engine, and provides join algorithms for combining data from multiple tables. All data resides in memory during execution, providing fast access times but requiring that data be exported to persistent storage before the program terminates.

The second tier is the HTTP API Server, implemented in Python using the Flask framework. This tier acts as an intermediary between the C++ engine and client applications, exposing database functionality through a RESTful interface. The server receives HTTP requests from clients, parses request data, performs any necessary data transformation, executes operations against the in-memory data structures, and formats results as JSON responses. The server also manages the sample data loading process and provides API endpoints for all supported operations.

The third tier is the Client Application, which in the case of MiniDB includes the graphical user interface implemented in Python using Tkinter. Clients connect to the server over HTTP, send requests for database operations, and display results to users. The GUI implements a modern dark-themed interface with intuitive navigation, real-time data visualization, and comprehensive table management capabilities. The client tier is completely separate from the server tier, allowing multiple clients to connect simultaneously and enabling integration with other applications through the API.

### 4.2 Core Data Structures

The fundamental storage mechanism in MiniDB relies on nested vectors to represent tabular data in an efficient and intuitive manner. Each table contains a `vector<vector<string>>` member variable that stores both the table schema and all data rows. The outer vector represents the collection of rows, while each inner vector represents a single row containing values for all columns in order. The first row in the vector contains column headers, and subsequent rows contain data values.

This row-major storage approach aligns with how users typically conceptualize tables, making the code easy to understand and modify. Accessing a specific row requires only a single vector indexing operation, and accessing a cell requires two indexing operations. The structure naturally supports variable-length rows and can accommodate tables with different schemas without requiring schema changes.

The table class also maintains metadata that enables efficient operations and enforces data relationships. Primary key and foreign key designations are tracked as strings containing column names, with corresponding indices stored for fast access during query processing. The hash indexing structure, described in detail below, provides accelerated access paths for common query patterns without requiring changes to the underlying data storage.

Beyond the table storage structure, MiniDB employs a linked-list structure for representing join results. The `JoinNode` class contains indices for the left and right rows that participated in the join, along with a pointer to the next node in the chain. This design allows join results to be traversed sequentially without requiring additional memory allocation for result storage. The linked-list approach trades random access convenience for simpler memory management and the ability to stream results as they are computed.

### 4.3 Hash-Based Indexing System

One of MiniDB's performance optimizations comes from its hash-based indexing implementation. For columns that are frequently queried using equality conditions, the system maintains an index that maps column values to the row indices where those values appear. This index structure is implemented as `unordered_map<string, unordered_map<string, vector<int>>>`, where the outer map keys are column names, the inner map keys are actual column values, and the vectors contain the row indices where each value occurs.

When a query specifies a condition of the form `WHERE column = value`, MiniDB consults the hash index to immediately retrieve all matching row indices rather than scanning every row in the table. This optimization reduces query complexity from O(n) linear search to O(1) hash lookup plus O(k) iteration over the matching rows, where k represents the number of matching records. For tables with many rows and selective queries that match only a small fraction of total rows, the performance improvement can be substantial.

The indexing system operates automatically for equality comparisons on columns that have been previously indexed. During row insertion, the database updates the appropriate index entries to reflect the new data. The index is consulted whenever the query parser encounters an equality condition, providing transparent performance benefits without requiring manual intervention from the user. Developers can extend the indexing system to support additional columns by calling the build index method when needed.

It is important to understand the limitations of the hash indexing approach. The index only accelerates equality comparisons; range queries using greater than, less than, or similar operators must still perform linear scans of candidate rows. Additionally, the hash index stores row indices rather than pointers to row data, meaning that index maintenance must track row positions as rows are inserted or modified.

### 4.4 Query Processing Pipeline

When a user submits a SQL-like query to MiniDB, the query passes through several processing stages before results are returned. Understanding this pipeline provides insight into how the system interprets and executes database operations.

The pipeline begins with lexical analysis, where the query string is tokenized into meaningful components. The parser identifies keywords such as SELECT, FROM, and WHERE, extracts identifiers representing table and column names, recognizes operators including equals, greater than, and less than, and parses literal values including strings and numbers. This tokenization process normalizes the query by converting it to lowercase and removing extra whitespace.

The parser then analyzes the token sequence to construct a structured representation of the query. For simple SELECT queries following the pattern `SELECT * FROM table WHERE column operator value`, the parser extracts the target table name, the condition column, the comparison operator, and the target value. More complex queries involving multiple conditions require additional parsing logic to combine predicates correctly using logical operators.

After parsing, the query execution engine determines the most efficient approach to retrieve matching rows. If the query contains an indexed equality condition, the engine consults the appropriate hash index to obtain candidate row identifiers. If no index is available or the condition involves range comparisons, the engine falls back to linear scanning of the table. The execution engine then filters the candidate rows according to any additional conditions and formats the results for presentation.

The results are returned as a structured object containing column headers and matching rows. For the GUI client, this data is rendered in a table view with sorting and filtering capabilities. For API clients, the data is serialized as JSON for easy parsing and integration with other systems.

### 4.5 Join Algorithm Implementation

MiniDB's INNER JOIN implementation uses a custom linked-list approach to combine rows from two tables based on primary key and foreign key relationships. This implementation demonstrates fundamental relational algebra concepts while remaining simple enough to study and understand.

The join algorithm operates by first identifying the foreign key column in the left table and the primary key column in the right table. For each row in the left table, the algorithm looks up the matching rows in the right table using the foreign key value. When a match is found, a new JoinNode is created containing the left row index, the right row index, and a pointer to the next node in the chain.

The matching process leverages the hash index on the primary key column of the right table for efficient lookups. This optimization ensures that the join operation scales efficiently even for large tables, as the complexity is roughly O(n log n) for the left table size n rather than O(n*m) for a naive nested loop join.

The linked-list structure allows the join to accumulate results incrementally without knowing the final result size in advance. Each new match extends the list by appending a new node, and the entire result can be traversed by following next pointers from the head node. This approach avoids the memory overhead of materializing complete join results in a two-dimensional structure, instead allowing results to be streamed as they are discovered.

After processing all left rows, the linked list contains all joined records. The print join function traverses this list and displays combined rows containing columns from both source tables. The output shows all columns from the left table followed by all columns from the right table, with rows ordered by the sequence of matches found during join execution.

---

## 5. Using the Graphical User Interface

### 5.1 Navigation and Layout

The MiniDB GUI features a modern dark-themed interface designed for efficient database management tasks. Understanding the layout and navigation conventions helps users work more effectively with the application.

The sidebar navigation panel occupies the left side of the window and provides access to all major features. Each navigation item consists of an icon and label, with the currently selected item highlighted to indicate the active view. The sidebar includes a logo and application title at the top, a connection status indicator, navigation buttons for all major features, a table count display, and version information at the bottom.

The main content area occupies the center and right portions of the window, displaying different views based on the selected navigation item. The header section at the top of the content area shows the current page title and optional breadcrumb navigation. The content area itself adapts to show relevant controls, data displays, and action buttons for each feature.

The status bar at the bottom of the window provides real-time information about the application state. The left section shows status messages indicating the current operation or state. The right section displays the current time, table count, and connection status icon. The status bar updates automatically as operations complete and state changes occur.

Navigation through the application is accomplished by clicking on sidebar items or using keyboard shortcuts for frequently accessed features. The interface supports contextual operations that appear based on the current view, such as action buttons that only appear when a table is selected. The refresh button in the header allows users to reload data from the server, useful after performing modifications that change the database state.

### 5.2 Connecting to the Database

The GUI must establish a connection to the server before it can perform database operations. The connection process is largely automated but can be understood and configured when needed.

Upon starting, the GUI attempts to connect to the server at the configured backend URL, which defaults to `http://localhost:8080`. The connection status indicator in the sidebar shows the current connection state, changing from red (disconnected) to green (connected) when a successful connection is established. If the initial connection fails, the GUI provides detailed troubleshooting guidance.

The connection test page allows users to verify connectivity and diagnose connection problems. This page shows the current configuration, provides a way to change the backend URL, and includes a button to run connection tests. The tests attempt to access several API endpoints and report which ones respond successfully. Failed tests indicate potential server problems, network issues, or incorrect configuration.

If the server is not running, the GUI cannot connect. The troubleshooting guidance explains how to start the server and verify that it is listening on the correct port. For users on Linux or macOS, the command `lsof -i :8080` can verify that a process is listening on port 8080. For Windows users, the command `netstat -ano | findstr :8080` serves the same purpose.

### 5.3 Managing Tables

The table management features allow users to view, create, and delete tables through an intuitive interface. Understanding these features enables effective organization of database contents.

The Tables view displays a list of all tables currently in the database. Each table appears as a card showing the table name, row count, and column count. A search bar at the top allows filtering the displayed tables by name. When no tables exist, the view shows an empty state with guidance on creating the first table.

Viewing a table displays its contents in a scrollable grid. Column headers appear at the top of the grid, and data rows appear below. The grid supports sorting by clicking on column headers, with the sort direction toggling between ascending and descending. The view toolbar includes buttons for refreshing the data, adding new rows, exporting to CSV, and returning to the table list.

Creating a new table requires specifying a table name and a comma-separated list of column names. The form includes validation to ensure that required fields are filled and that the table name does not already exist. Upon successful creation, the new table appears in the tables list and can be populated with data.

Deleting a table removes it from the database along with all contained data. The operation requires confirmation before execution, as it cannot be undone. Deleted tables cannot be recovered except by re-creating them and re-importing any data.

### 5.4 Executing SQL Queries

The SQL query interface provides direct access to the query processing system, allowing users to retrieve and filter data using familiar SQL syntax. This feature is intended for users comfortable with database query languages.

The query editor consists of a text area where queries are entered, an example queries dropdown providing templates for common patterns, and an execute button that sends the query to the server. The editor supports keyboard shortcuts including Ctrl+Enter for quick execution. A line number display helps with positioning the cursor and identifying query lines.

Supported query syntax includes the basic pattern `SELECT * FROM table_name WHERE column operator value`. The asterisk indicates selection of all columns, though specific columns can be named instead. The FROM clause specifies the target table, and the WHERE clause is optional for queries without filtering conditions.

The supported comparison operators are equals (=), not equals (!=), greater than (>), less than (<), greater than or equal (>=), and less than or equal (<=). For equality queries on indexed columns, the system automatically uses the hash index for optimized execution. For range queries and other conditions, the system scans applicable rows and filters according to the specified conditions.

Query results appear below the editor in a formatted display showing column headers, data rows, and statistics about the result set. The statistics include the number of rows returned and the number of columns in each row. Results can be scrolled horizontally and vertically to view all data.

### 5.5 Natural Language Queries

The natural language query interface allows users to retrieve data using conversational English sentences rather than formal SQL syntax. This feature makes the database accessible to users without technical database knowledge.

The NLP input field accepts natural language queries in plain English. Users can ask questions such as "Show me all employees" or "Find products where price is less than 50". The system parses these sentences, identifies the relevant table and columns, determines any filtering conditions, and generates equivalent SQL queries that are executed against the database.

Example queries demonstrate the types of questions the system can understand. Display queries ask for all data from a table, such as "Show employees" or "Display all products". Filter queries request data matching specific conditions, such as "Show employees where salary > 70000" or "Find products where price < 50". Count queries request counts of matching records, such as "Count all employees" or "How many products are in stock". Create and insert queries demonstrate data manipulation through natural language, such as "Create table customers with columns id, name, email".

Results from NLP queries show the generated SQL translation alongside the data results. This transparency helps users learn SQL syntax by seeing how natural language maps to formal queries. The results display column headers, data rows, and statistics similar to the SQL query interface.

### 5.6 Importing and Exporting CSV Data

The CSV import and export features enable data exchange between MiniDB and external systems that use comma-separated values format. These features are essential for integrating MiniDB with data workflows and for preserving data between sessions.

Importing CSV data allows existing datasets to be loaded into the database. The import process opens a file selection dialog where users choose the CSV file to import. After selecting a file, users specify the table name that the data should be loaded into. The import process reads the file, parses each line into individual column values, and inserts the resulting rows into the specified table. The first row of the CSV file is expected to contain column headers, which become the table schema.

Exporting table data to CSV format preserves the table contents for use in other applications. Users select the table to export and specify a filename for the output file. The export process writes column headers followed by all data rows in comma-separated format. The resulting file can be opened in spreadsheet applications such as Microsoft Excel or Google Sheets, or processed by other programs that support CSV input.

The export feature also supports exporting query results, allowing users to save the results of filtered or transformed data for further analysis. After executing a query, the export option saves the result set to a CSV file in the same format as table exports.

### 5.7 Performing Table Joins

The table join interface enables relational operations that combine data from multiple tables based on key relationships. Understanding join operations is essential for working with normalized data models.

The join configuration requires selecting a left table, a right table, and a join column. The join column must exist in both tables and contain matching values that establish the relationship. For typical use cases, this column is a foreign key in the left table that references a primary key in the right table.

After configuring the join, clicking the perform join button sends the join request to the server. The server executes the join algorithm, combining rows where the join column values match. The results appear in a new window showing all columns from both tables side by side. Each row in the result represents a match between a left table row and a right table row.

The join results display includes a row count indicating how many matches were found. For tables with no matching rows based on the join column, the result set is empty. Users can verify that their data has proper relationships by checking for expected join results.

---

## 6. API Reference

### 6.1 API Overview

The MiniDB HTTP API provides programmatic access to all database functionality through RESTful endpoints. This API enables integration with other applications and allows developers to build custom clients beyond the included GUI.

All API endpoints are relative to the server base URL, which defaults to `http://localhost:8080`. Requests use standard HTTP methods including GET for data retrieval and POST for operations that modify data or execute queries. Responses are formatted as JSON objects with consistent structure across all endpoints.

The API implements authentication through the absence of authentication requirements for local access. In production deployments, additional authentication mechanisms such as API keys or OAuth should be implemented to secure the API. For development and testing, the API is open and accessible to any client that can reach the server.

### 6.2 Health and Status Endpoints

The health and status endpoints provide information about the server state and database status without performing any operations.

The health check endpoint at `GET /api/health` returns the server status and list of current tables. This endpoint is useful for verifying that the server is running and responsive. The response includes a status field set to "ok" for healthy servers, a message describing the server, and an array of table names currently in the database.

The status endpoint at `GET /api/status` provides detailed information about the database state. The response includes the server status, an array of table names, and the total table count. This endpoint is useful for applications that need to discover available tables before performing operations.

The root endpoint at `GET /` returns a list of all available API endpoints with descriptions. This endpoint serves as API documentation and discovery, allowing clients to understand what operations are available without consulting external documentation.

### 6.3 Table Management Endpoints

The table management endpoints provide operations for creating, reading, updating, and deleting tables.

The list tables endpoint at `GET /api/tables` returns an array containing the names of all tables currently in the database. This endpoint is useful for discovering available tables before performing operations on specific tables.

The get table info endpoint at `GET /api/tables/{table_name}` returns metadata about a specific table including column names and row count. The response includes the table name, an array of column names, and the number of rows in the table. Returns a 404 error if the table does not exist.

The get table data endpoint at `GET /api/tables/{table_name}/data` returns the complete contents of a table including column headers and all data rows. The response includes an array of column names and a two-dimensional array of row values. This endpoint is used by the GUI to display table contents.

The create table endpoint at `POST /api/tables` creates a new table with the specified name and columns. The request body must include a JSON object with `table_name` (string) and `columns` (array of strings) fields. Returns a 201 status code with confirmation message on success, or a 400 error if the table name is missing or already exists.

The delete table endpoint at `DELETE /api/tables/{table_name}` removes a table and all its data from the database. This operation cannot be undone. Returns a 200 status code with confirmation message on success, or a 404 error if the table does not exist.

### 6.4 Data Manipulation Endpoints

The data manipulation endpoints support inserting rows into tables and executing queries.

The insert row endpoint at `POST /api/tables/{table_name}/rows` adds a new row to the specified table. The request body must include a JSON object with a `values` object mapping column names to values. Returns a 201 status code with confirmation message on success, or a 404 error if the table does not exist.

The execute query endpoint at `POST /api/query` executes a SQL-like query against the database. The request body must include a JSON object with a `query` string containing the query to execute. The supported query syntax is `SELECT * FROM table_name WHERE column operator value` with operators including =, !=, >, <, >=, and <=. Returns query results including column headers and matching rows on success, or appropriate error messages for invalid queries or missing tables.

### 6.5 Advanced Operations Endpoints

The advanced operations endpoints provide join functionality, CSV import/export, and natural language query processing.

The perform join endpoint at `POST /api/join` executes an inner join between two tables. The request body must include JSON objects specifying the left table name, right table name, and join column name. Returns the combined results including columns from both tables and rows representing matched pairs. Returns a 400 error if required parameters are missing or a 404 error if either table does not exist.

The import CSV endpoint at `POST /api/tables/{table_name}/import` imports data from a CSV file into the specified table. The request must be a multipart form upload with a file field containing the CSV data. Returns a 201 status code with column and row count on success, or appropriate errors for invalid files or parsing failures.

The export CSV endpoint at `GET /api/tables/{table_name}/export` returns the contents of a table in CSV format. The response content type is text/csv with a content-disposition header suggesting a filename. Returns a 404 error if the table does not exist.

The natural language query endpoint at `POST /api/nlp` processes natural language queries and returns results. The request body must include a JSON object with a `query` string containing the natural language question. The system parses the query, generates SQL, executes it, and returns both the generated SQL and the results. Returns a 400 error if the query cannot be understood.

### 6.6 Administrative Endpoints

The administrative endpoints provide server management capabilities.

The reset database endpoint at `POST /api/reset` clears all tables and data from the database. This operation cannot be undone. Returns a confirmation message on success. This endpoint is useful for testing scenarios that require a clean database state.

---

## 7. Troubleshooting and Support

### 7.1 Common Issues and Solutions

This section addresses common problems that users may encounter when running MiniDB and provides solutions for resolving them.

The most common issue is failure to connect from the GUI to the server. This typically occurs when the server is not running or is running on a different port than expected. Verify that the server is running by checking for the server banner output and confirming that it shows the server is listening on port 8080. Check that the GUI is configured to connect to the correct URL by accessing the connection test page. Ensure that no firewall software is blocking connections to port 8080.

Another common issue is missing sample data when the server starts. This occurs when the CSV files are not in the working directory where the server is running. Verify that the employees.csv and departments.csv files exist in the GUI directory alongside server.py. The server displays a message indicating how many sample tables were loaded during startup.

Query execution errors may occur when using invalid SQL syntax or referencing non-existent tables or columns. Review the error message returned by the server for specific information about what went wrong. Ensure that table and column names are spelled correctly and that comparison operators are supported. Remember that all data is stored as strings, so numeric comparisons may behave unexpectedly for non-numeric values.

Memory issues may occur when working with very large datasets in the in-memory database. Since MiniDB stores all data in RAM, the available system memory limits the amount of data that can be loaded. If the system becomes slow or unresponsive, consider exporting data to CSV, restarting the server, and loading only the data needed for current operations.

### 7.2 Performance Considerations

Understanding performance characteristics helps users work effectively with MiniDB and avoid common pitfalls.

Query performance depends heavily on the use of indexes and the selectivity of conditions. Equality queries on indexed columns execute very quickly because the hash index provides O(1) lookup. Queries without indexes or with range conditions require scanning all rows, which is slower for large tables.

Table join performance depends on the size of the tables being joined and the availability of indexes on join columns. Joins between large tables benefit from indexed primary keys on the right table, reducing the complexity from nested loops to indexed lookups.

Memory usage grows with the amount of data stored in the database. Each row requires storage for all column values plus overhead for vector structures and indexes. For most educational and prototyping scenarios, MiniDB can comfortably handle tables with thousands to tens of thousands of rows.

The GUI may become slow when displaying very large result sets. Consider using WHERE clauses to limit results rather than retrieving all rows when working with large tables. The pagination or limiting features can be implemented by adding conditions to queries.

### 7.3 Getting Help and Contributing

Users who encounter issues not covered by this documentation can seek help through GitHub issues on the project repository. When reporting issues, provide details about the operating system, Python version, and steps to reproduce the problem.

Contributions to MiniDB are welcome and appreciated. The project includes VSCode configuration files in the .vscode directory providing recommended settings for working with the codebase. Contributions should follow existing code style conventions, compile without warnings, and include appropriate test coverage for new functionality.

---

## 8. Appendix: Sample Data Reference

### 8.1 Employees Table Schema

The employees table contains employee records with the following column structure. The first row of the CSV file defines these column names, and subsequent rows contain data values.

The `empID` column contains unique employee identification numbers. This column serves as the primary key for the employees table and is used as a foreign key in other tables that reference employees. Values are integers stored as strings, ranging from 1 to 20,000 in the sample dataset.

The `name` column contains employee names in the format "UserN" where N is the employee number. This naming convention provides easily distinguishable sample data while demonstrating text field handling.

The `age` column contains employee ages as integers stored as strings. Values range from 18 to 65 in the sample dataset, representing a typical working age range.

The `deptID` column contains department identification codes that reference the departments table. Values include d10, d20, d30, and d40, representing four different departments. This column serves as a foreign key enabling joins with the departments table.

### 8.2 Departments Table Schema

The departments table contains department information with the following column structure.

The `deptID` column contains unique department identification codes. This column serves as the primary key for the departments table and is referenced by the deptID foreign key in the employees table.

The `deptName` column contains descriptive department names such as Engineering, Marketing, and Human Resources. These names provide human-readable labels for the department codes.

The `location` column contains department location information including building names or numbers. This data demonstrates additional attribute storage and enables location-based queries.

### 8.3 Products Table Schema

The products table contains sample product data with the following column structure.

The `product_id` column contains unique product identification codes such as p1, p2, p3. This column serves as the primary key for the products table.

The `name` column contains product names such as Laptop, Mouse, and Keyboard. These names demonstrate text field handling and enable product identification.

The `price` column contains product prices as decimal values. This column demonstrates numeric data handling for currency values.

The `stock` column contains current inventory quantities as integers. This column demonstrates numeric data handling for inventory tracking.

---

*Documentation generated for MiniDB - A Lightweight C++ In-Memory Database Engine with Python Interface*
