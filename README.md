# MiniDB Documentation

## A Lightweight C++ In-Memory Database Engine

---

## Table of Contents

1. [Introduction and Overview](#1-introduction-and-overview)
2. [Installation and Setup](#2-installation-and-setup)
3. [Architecture and Design](#3-architecture-and-design)
4. [Features and Capabilities](#4-features-and-capabilities)
5. [Usage Guide](#5-usage-guide)
6. [API Reference](#6-api-reference)
7. [Contributing Guidelines](#7-contributing-guidelines)
8. [Frequently Asked Questions](#8-frequently-asked-questions)
9. [License](#9-license)

---

## 1. Introduction and Overview

MiniDB is a lightweight, interactive in-memory database system implemented entirely in modern C++. This project demonstrates the fundamental principles of database management systems while remaining accessible enough for educational purposes and practical prototyping. The entire database operates within the system's random-access memory (RAM), providing extremely fast data access and manipulation at the cost of data persistence across sessions.

The project serves multiple purposes within the software development ecosystem. For computer science students, MiniDB provides a hands-on understanding of how database engines function internally, covering essential concepts such as indexing strategies, query execution, and join algorithms. For developers building small-scale applications or prototypes, MiniDB offers a zero-dependency database solution that can be integrated directly into C++ projects without the overhead of installing and configuring external database systems like MySQL, PostgreSQL, or SQLite. The modular design also makes MiniDB an excellent foundation for developers who wish to extend or customize database functionality for specific use cases.

One of the distinguishing characteristics of MiniDB is its implementation approach. Rather than relying on external libraries or complex dependency chains, MiniDB builds entirely upon the C++ Standard Template Library (STL). This design decision significantly reduces the barrier to entry for developers who wish to study, modify, or extend the codebase. The hash-based indexing system provides fast lookup capabilities for equality comparisons, while the custom linked-list join structure demonstrates how relational operations can be implemented without resorting to conventional database algorithms.

### 1.1 Key Features Summary

MiniDB encompasses a comprehensive set of database management capabilities within its compact codebase. The interactive command-line interface provides users with direct access to all database operations through a menu-driven system. Table management operations include creating tables with user-defined schemas, inserting new rows, updating existing records, and displaying table contents in a formatted manner. The relational capabilities support primary key and foreign key constraints, enabling meaningful relationships between tables that can be exploited through the INNER JOIN operation.

Data import and export functionality bridges the gap between MiniDB's in-memory environment and external data sources. The CSV import capability allows existing datasets to be loaded into the database for analysis and manipulation, while CSV export ensures that valuable data can be persisted and transferred to other applications. The SQL-like query parser supports basic selection operations with various comparison operators, including equality, inequality, and numeric comparisons.

### 1.2 Use Cases and Applications

The primary use case for MiniDB centers on educational environments where students need to understand database internals without the complexity of production-grade systems. The codebase is small enough to be read and comprehended within a reasonable timeframe, yet it contains enough functionality to demonstrate real database concepts. Instructors can use MiniDB as a teaching tool to explain indexing, querying, and join operations through visible, traceable code.

For rapid prototyping, MiniDB offers a convenient solution when full database infrastructure is unnecessary. Developers building proof-of-concept applications can use MiniDB to store and manipulate data without deploying external database servers or configuring connection strings. The zero-configuration nature of MiniDB means that prototypes can be up and running immediately, with the flexibility to migrate to more robust solutions if the project outgrows MiniDB's capabilities.

Embedded systems and applications with limited dependencies can also benefit from MiniDB's lightweight architecture. Since the database consists entirely of C++ code with no external library requirements, it can be compiled and integrated into diverse environments including embedded Linux systems, IoT applications, and standalone utilities.

---

## 2. Installation and Setup

Setting up MiniDB requires minimal infrastructure due to the project's commitment to simplicity and standard C++ tooling. The following sections detail the prerequisites, installation process, and verification steps necessary to get MiniDB running on your system.

### 2.1 Prerequisites

Before compiling and running MiniDB, ensure that your development environment meets the following requirements. A C++ compiler supporting the C++11 standard or higher is essential, as MiniDB utilizes modern C++ features including containers, smart pointers, and range-based iteration. The GNU Compiler Collection (GCC) with g++, Clang, or Microsoft Visual C++ (MSVC) all satisfy this requirement. The C++ Standard Template Library must be available, which is included with all standard C++ compiler installations.

For building the project, you will need a terminal or command-line interface with the ability to execute compilation commands. No additional build tools such as CMake or Make are strictly required, as MiniDB can be compiled with a single g++ command. However, if you prefer using build automation tools, the repository includes CMake configuration files for those who wish to utilize them.

The system should have sufficient memory to hold your anticipated datasets. Since MiniDB operates entirely in RAM, the practical limits of data storage depend on your available system memory. For most educational and prototyping scenarios, the available RAM will far exceed the data volumes you need to store.

### 2.2 Obtaining the Source Code

The MiniDB source code is hosted on GitHub at the repository location specified in the project documentation. To obtain a copy of the codebase, you can either download the repository as a ZIP archive or clone it using Git. Cloning the repository provides the additional benefit of easy updates and the ability to track your own modifications separately from the upstream project.

To clone the repository using Git, execute the following command in your terminal:

```bash
git clone https://github.com/maisum77/DATABASE-IN-CPP.git
cd DATABASE-IN-CPP
```

After cloning, explore the repository structure to familiarize yourself with the organization. The main implementation resides in the root directory as `main.cpp`, while additional components and extensions are organized into subdirectories. Sample data files including `employees.csv` and `departments.csv` are provided for testing purposes and can be loaded automatically when present.

### 2.3 Compilation

Compiling MiniDB requires only the standard C++ compiler and the main source file. Navigate to the repository directory and execute the compilation command appropriate for your compiler. The following command demonstrates compilation using g++:

```bash
g++ main.cpp -o minidb -std=c++11
```

The `-std=c++11` flag ensures that the compiler uses the C++11 standard or newer, which is necessary for the language features employed in the codebase. If your compiler defaults to C++11 or higher, this flag may be omitted, but including it ensures consistent behavior across different compiler versions and configurations.

For users with Clang, the compilation command follows the same pattern:

```bash
clang++ main.cpp -o minidb -std=c++11
```

On Windows with MSVC, open a Developer Command Prompt and use:

```cmd
cl /EHsc main.cpp /Fe:minidb.exe
```

The compilation process should complete quickly, producing an executable file named `minidb` (or `minidb.exe` on Windows) in the current directory. If you encounter compilation errors, verify that your compiler supports C++11 and that you have copied all necessary source files from the repository.

### 2.4 Initial Execution and Verification

Once compilation is complete, you can verify that MiniDB is functioning correctly by executing the compiled program. Simply run the executable from your terminal:

```bash
./minidb
```

Upon successful launch, MiniDB will display an interactive menu presenting the available operations. If the sample data files `employees.csv` and `departments.csv` are present in the working directory, MiniDB will automatically load them, providing immediate access to example data for exploration and testing.

The initial screen should show the CLI menu with numbered options for various database operations. You can verify basic functionality by selecting the option to display a table, which will show any loaded data. If no tables appear initially, this is expected behavior when the sample CSV files are not present—you can create your own tables and data using the provided menu options.

---

## 3. Architecture and Design

Understanding MiniDB's internal architecture provides valuable insight into how database systems organize and manipulate data. This section examines the core data structures, indexing mechanisms, query processing pipeline, and join algorithm that together form the foundation of MiniDB's functionality.

### 3.1 Core Data Structures

The fundamental storage mechanism in MiniDB relies on nested vectors to represent tabular data. Each table contains a `vector<vector<string>>` member variable named `form` that stores both the table schema (column headers) and all data rows. This row-major storage approach aligns with how users typically think about tables, with each inner vector representing a complete row containing values for all columns in order.

The table structure also maintains additional metadata that enables efficient operations. Column names are stored separately for quick reference during query parsing and validation. Primary key and foreign key designations are tracked to enforce referential integrity and enable join operations. The hash indexing structure, discussed in detail below, provides accelerated access paths for common query patterns.

Beyond the table structure, MiniDB employs a linked-list structure for representing join results. The `JoinNode` class contains pointers to the left and right rows that participated in the join, along with a pointer to the next node in the chain. This design allows join results to be traversed sequentially without requiring additional memory allocation for result storage. The linked list approach trades the random access convenience of array-based storage for simpler memory management and the ability to stream results as they are computed.

### 3.2 Hash-Based Indexing System

One of MiniDB's performance optimizations comes from its hash-based indexing implementation. For columns that are frequently queried using equality conditions, MiniDB maintains an index that maps column values to the row identifiers where those values appear. This index structure is implemented as `unordered_map<string, unordered_map<string, vector<int>>>`, where the outer map keys are column names, the inner map keys are actual column values, and the vectors contain the row indices where each value occurs.

When a query specifies a condition of the form `WHERE column = value`, MiniDB can consult the hash index to immediately retrieve all matching row indices rather than scanning every row in the table. This optimization reduces query complexity from O(n) linear search to O(1) hash lookup plus O(k) iteration over the matching rows, where k represents the number of matching records. For tables with many rows and selective queries (those matching only a small fraction of total rows), the performance improvement can be substantial.

The indexing system operates automatically for equality comparisons on columns that have been indexed. During row insertion, the database updates the appropriate index entries to reflect the new data. The index is consulted whenever the query parser encounters an equality condition, providing transparent performance benefits without requiring manual intervention from the user.

It is important to understand the limitations of the hash indexing approach. The index only accelerates equality (`=`) comparisons; range queries using `>`, `<`, `>=`, or `<=` operators must still perform linear scans of candidate rows. Additionally, the hash index stores row indices rather than pointers to row data, meaning that index maintenance must track row positions as rows are inserted or modified.

### 3.3 Query Processing Pipeline

When a user submits a SQL-like query to MiniDB, the query passes through several processing stages before results are returned. The pipeline begins with lexical analysis, where the query string is tokenized into meaningful components: keywords (`SELECT`, `FROM`, `WHERE`), identifiers (table and column names), operators (`=`, `>`, `<`), and literal values.

The parser then analyzes the token sequence to construct a structured representation of the query. For simple `SELECT * FROM table WHERE column = value` queries, the parser extracts the target table name, the condition column, the comparison operator, and the target value. More complex queries involving multiple conditions or different comparison types require additional parsing logic to combine multiple predicates correctly.

After parsing, the query execution engine determines the most efficient approach to retrieve matching rows. If the query contains an indexed equality condition, the engine consults the appropriate hash index to obtain candidate row identifiers. If no index is available or the condition involves range comparisons, the engine falls back to linear scanning of the table. The execution engine then filters the candidate rows according to any additional conditions and formats the results for presentation to the user.

### 3.4 Join Algorithm Implementation

MiniDB's INNER JOIN implementation uses a custom linked-list approach to combine rows from two tables based on primary key and foreign key relationships. The join algorithm operates by first identifying the foreign key column in the left table and the primary key column in the right table. For each row in the left table, the algorithm looks up the matching rows in the right table using the foreign key value.

The matching process leverages the hash index on the primary key column of the right table for efficient lookups. When a match is found, a new `JoinNode` is created containing pointers to the left row, the right row, and the next node in the chain. This linked list structure allows the join to accumulate results incrementally without knowing the final result size in advance.

The join execution proceeds as follows: the algorithm iterates through all rows of the left table, performing indexed lookups against the right table's primary key. Each successful match creates a new node in the result chain. After processing all left rows, the linked list contains all joined records, which can then be traversed and displayed to the user.

This join implementation demonstrates the fundamental concept of relational algebra's theta join operation while remaining simple enough to study and understand. The linked-list approach avoids the memory overhead of materializing complete join results in a two-dimensional structure, instead allowing results to be streamed as they are discovered.

---

## 4. Features and Capabilities

MiniDB provides a comprehensive set of database management features within its compact implementation. This section details each major capability, explaining both how to use the feature and the underlying implementation approach.

### 4.1 Table Management

Creating tables in MiniDB involves defining the table name and the columns (attributes) that comprise the schema. The table creation process establishes the fundamental structure that will hold your data, including column names that serve as identifiers for subsequent operations. When creating a table, you specify whether each column serves as a primary key or may participate in foreign key relationships with other tables.

Row insertion adds new data to an existing table. Each inserted row must conform to the table's schema, providing a value for every column defined in the table structure. The insertion operation automatically updates any hash indexes associated with the table, ensuring that newly inserted rows become immediately discoverable through indexed queries. Primary key columns must contain unique values across all rows, as duplicates would violate the primary key constraint.

Table display functionality renders the current contents of a table in a human-readable format. The display routine formats column headers and rows with appropriate spacing and alignment, making it easy to visually verify the state of your data. This feature proves particularly valuable during development and debugging when you need to confirm that operations have produced the expected results.

### 4.2 Query Capabilities

The SQL-like query parser supports selection operations that retrieve rows matching specified conditions. The query syntax follows the familiar pattern `SELECT * FROM table WHERE column operator value`, where the asterisk indicates selection of all columns and the WHERE clause specifies filtering criteria. This syntax will be familiar to anyone who has worked with relational databases, reducing the learning curve for new users.

Supported comparison operators include equality (`=`), inequality (`!=`), greater than (`>`), less than (`<`), greater than or equal (`>=`), and less than or equal (`<=`). The equality operator receives special optimization treatment through hash indexing, while the comparison operators perform linear scans of candidate rows. The query parser handles operator precedence and combines multiple conditions when present in the query string.

Query results are returned as formatted output showing the matching rows. For indexed equality queries, the system leverages the hash index for efficient retrieval. For range queries and other conditions without index support, the system scans applicable rows and filters according to the specified conditions.

### 4.3 Data Import and Export

CSV import functionality allows existing datasets to be loaded into MiniDB for analysis and manipulation. The import process reads comma-separated values from a file, parses each line into individual column values, and inserts the resulting rows into the specified table. This capability bridges the gap between external data sources and MiniDB's in-memory environment, enabling analysis workflows that combine data from multiple origins.

The export functionality performs the inverse operation, writing table contents to a CSV file that can be opened in spreadsheet applications or consumed by other programs. Export proves essential for preserving valuable data across sessions, as MiniDB's in-memory nature means that all data is lost when the program terminates unless explicitly saved. The export routine writes column headers followed by all data rows in comma-separated format.

Sample data files including `employees.csv` and `departments.csv` demonstrate the expected CSV format and provide ready-made data for experimentation. These files are automatically loaded when present, giving new users immediate access to example data for exploring MiniDB's capabilities.

### 4.4 Relational Operations

Primary key and foreign key support enables meaningful relationships between tables, which can then be exploited through join operations. A primary key uniquely identifies each row in a table and serves as the target for foreign key references from other tables. A foreign key in one table references the primary key of another table, establishing a link between related data stored across multiple tables.

The INNER JOIN operation combines rows from two tables based on matching primary key and foreign key values. This operation is fundamental to relational database design, enabling queries that retrieve related information from multiple tables in a single operation. MiniDB's join implementation automatically identifies foreign key to primary key relationships and produces combined results showing data from both source tables.

---

## 5. Usage Guide

This section provides practical guidance for using MiniDB's features through common usage scenarios. Each scenario demonstrates a specific workflow, showing the menu selections and expected interactions.

### 5.1 Interactive CLI Overview

Upon launching MiniDB, you are presented with an interactive menu offering numbered options for various operations. The menu system provides an accessible interface to all database capabilities without requiring knowledge of command-line syntax. Each menu option corresponds to a specific operation, with sub-options available for detailed configuration when needed.

The main menu presents the following options:

```
1. Display table
2. Run SQL query
3. Export table to CSV
4. Inner join
5. Create new table
6. Insert into table
0. Exit
```

Navigation through the menu system involves entering the number corresponding to your desired operation. The system then prompts for any additional information required to complete the selected operation, such as table names, column specifications, or query strings.

### 5.2 Creating and Populating a Table

To create a new table, select option 5 from the main menu. The system will prompt you to enter the table name and the column definitions. Column definitions specify the names of each column in the table, which together form the table schema. For example, creating an employees table might involve specifying columns for employee ID, name, department, and salary.

After creating the table structure, you can add data by selecting option 6 (Insert into table) from the main menu. The insertion prompt asks for values corresponding to each column in the table's schema. Enter values in the order specified by the schema, using appropriate data types (all values are stored as strings internally). The insertion routine validates that all required columns receive values and that primary key columns do not receive duplicate entries.

### 5.3 Querying Data

To retrieve data from a table, select option 2 (Run SQL query) from the main menu. Enter your query using the supported syntax pattern. For basic queries retrieving all columns where a specific column equals a specified value, use the following format:

```sql
SELECT * FROM employees WHERE deptID = d10
```

This query retrieves all columns from the employees table for rows where the deptID column contains the value "d10". The system will display matching rows in a formatted layout showing all column values.

For more complex queries involving different comparison operators, modify the WHERE clause accordingly:

```sql
SELECT * FROM employees WHERE salary > 50000
SELECT * FROM departments WHERE name != Sales
```

### 5.4 Performing Joins

The inner join operation combines data from two related tables. Before performing a join, ensure that your tables have appropriate primary key and foreign key relationships established. Select option 4 (Inner join) from the main menu, then specify the two tables to join and the columns serving as the join keys.

The join operation matches rows where the foreign key value in one table equals the primary key value in the other table. Results display combined rows containing columns from both source tables, enabling you to view related information together.

### 5.5 Importing and Exporting Data

To import data from a CSV file, ensure the file exists in the working directory and follows the expected format. The import process reads the file and creates or populates the appropriate table. Sample files employees.csv and departments.csv demonstrate the expected format.

To export data, select option 3 (Export table to CSV) from the main menu and specify the table to export. The system writes the table contents to a CSV file named after the table, preserving column headers and all data rows.

---

## 6. API Reference

This section provides reference information for the internal API exposed by MiniDB's implementation. Understanding these interfaces proves valuable for developers who wish to extend or modify the codebase.

### 6.1 Table Class Methods

The Table class serves as the primary interface for data storage and manipulation. Key methods include the constructor, which initializes an empty table with the specified schema, and methods for inserting new rows, updating existing records, and retrieving data based on various criteria.

The `select_where` method implements conditional row retrieval, accepting a column name, comparison operator, and target value. The method first checks for available hash indexes to optimize equality comparisons, then falls back to linear scanning for other operators or when indexes are unavailable. The method returns a collection of matching row indices that can be used to retrieve or display the actual row data.

The `insert` method adds new rows to the table, accepting a vector of values corresponding to the table's columns. The method validates the input against the schema, checks primary key uniqueness, and updates any maintained indexes. Foreign key validation ensures that referenced values exist in the target tables before accepting the insertion.

### 6.2 JoinNode Structure

The JoinNode structure represents individual join results within the linked-list join implementation. Each JoinNode contains pointers to the left and right rows that participated in the join, along with a pointer to the next node in the chain. The structure supports sequential traversal through the result list, with the final node containing a null next pointer.

The inner join function constructs the linked list by iterating through the left table's rows, looking up matching right table rows via primary key index, and creating JoinNode instances for each match. The function returns the head of the resulting linked list, which can then be traversed to access all join results.

### 6.3 Index Management

Hash index management is handled through the `hash_indexes` member variable, which maps column names to value-to-row-indices mappings. Index maintenance occurs automatically during row insertion and updates, ensuring that the index remains consistent with the underlying data.

The indexing system supports efficient lookups through the `find` operation on the inner unordered_map, which returns a vector of row indices for the specified column value. This lookup operates in constant time on average, providing significant performance benefits for equality queries on indexed columns.

---

## 7. Contributing Guidelines

Contributions to MiniDB are welcome and appreciated. This section outlines the process for contributing improvements, bug fixes, or new features to the project.

### 7.1 Development Environment

The project includes VSCode configuration files in the `.vscode` directory, providing recommended settings and extensions for working with the codebase. These configuration files establish consistent formatting, linting, and debugging settings across development environments.

To set up your development environment, clone the repository and open it in your preferred code editor. The codebase follows standard C++ conventions, with header files for declarations and implementation files for definitions. All code should compile with a standards-compliant C++11 or newer compiler.

### 7.2 Code Style and Conventions

Contributions should adhere to the existing code style observed throughout the codebase. Variable names use descriptive identifiers in camelCase. Class names use PascalCase with meaningful names that indicate the component's purpose. Comments explain complex logic and document the purpose of non-obvious code sections.

Before submitting changes, ensure that your code compiles without warnings and that existing functionality continues to work correctly. Test your changes with the provided sample data and consider adding new test cases for any new functionality.

### 7.3 Submission Process

For significant changes, consider opening an issue first to discuss the proposed modifications. This discussion helps ensure that your contribution aligns with the project's direction and avoids duplicate work. When submitting changes, provide a clear description of what the modification accomplishes and any testing performed.

Pull requests should be submitted through GitHub's standard pull request mechanism. Include a summary of changes, explanation of the approach taken, and any relevant context for reviewers. The project maintainer will review the submission and provide feedback or merge the changes as appropriate.

---

## 8. Frequently Asked Questions

This section addresses common questions and concerns that arise when working with MiniDB.

**Does MiniDB persist data between sessions?**

No, MiniDB operates entirely in memory and does not automatically persist data when the program exits. All data is lost when MiniDB terminates unless you explicitly export tables to CSV files using the export functionality. To preserve data across sessions, export your tables before exiting and import the data when starting a new session.

**What is the performance characteristics of queries?**

For equality queries on indexed columns, MiniDB achieves O(1) hash lookup performance plus O(k) for retrieving k matching rows. For queries using comparison operators or on columns without indexes, MiniDB performs O(n) linear scans where n is the total number of rows in the table. The actual performance depends on your data size and query patterns.

**What SQL syntax is supported?**

MiniDB supports a simplified subset of SQL syntax focused on selection operations. The supported pattern is `SELECT * FROM table WHERE column operator value`, where operators include `=`, `!=`, `>`, `<`, `>=`, and `<=`. More complex SQL constructs including JOIN clauses in the query string, subqueries, and aggregations are not supported in the current implementation.

**Can I use MiniDB in my commercial project?**

MiniDB is licensed under the MIT License, which permits use in commercial projects with minimal restrictions. The license requires inclusion of the copyright notice and license text in copies of the software. See the LICENSE file for complete terms.

**How do I handle data type differences?**

All data in MiniDB is stored internally as strings. For numeric comparisons, the system converts string values to numeric types during evaluation. This approach provides flexibility but means that numeric formatting affects comparison results (e.g., "10" is less than "9" in string comparison but greater in numeric comparison).

**What are the memory limitations?**

MiniDB's memory usage scales with the size of your data. Each row requires storage for all column values plus overhead for vector and index structures. For most educational and prototyping scenarios, MiniDB can comfortably handle tables with thousands to tens of thousands of rows within typical system memory constraints.

---

## 9. License

MiniDB is licensed under the MIT License, a permissive open-source license that allows you to use, copy, modify, merge, publish, distribute, sublicense, and sell the software. The only requirements are that you include the original copyright notice and license text in any copies or substantial portions of the software.

The MIT License text is included in the LICENSE file distributed with the project. For commercial use, the primary obligation is to preserve the license notice in any distributed copies. Beyond this requirement, the license places minimal restrictions on how you use the software.

This licensing approach encourages both open-source and commercial adoption by removing barriers to use while ensuring proper attribution. Projects incorporating MiniDB should include the following notice in their documentation or about screens:

```
This software includes MiniDB, licensed under the MIT License.
Copyright (c) [Year] [Original Author]
```

---

## Appendix: Project Directory Structure

```
DATABASE-IN-CPP/
├── .vscode/                 # VSCode editor configuration
├── build/                   # Build output directory
├── data_insight/            # Data analysis and visualization components
├── doc/                     # Documentation files
├── minmax/                  # GUI components
├── NLP/                     # Natural language processing utilities
├── src/                     # Source code directory
├── web/                     # Web interface components
├── main.cpp                 # Main database implementation
├── employees.csv            # Sample employee data
├── departments.csv          # Sample department data
└── README.md                # Project README
```

---

*Documentation generated for MiniDB - A Lightweight C++ In-Memory Database Engine*
