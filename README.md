# 🗄️ MiniDB --- A Lightweight C++ In-Memory Database Engine

MiniDB is a simple, interactive in-memory database system implemented in
modern C++.\
It supports table creation, row insertion, CSV import/export, basic
SQL-like querying, and an inner join engine using custom linked-list
join nodes.

This project is ideal for learning how databases work internally,
including indexing, row storage, query execution, and joins.

## 📑 Table of Contents

-   [Features](#features)\
-   [Project Structure](#project-structure)\
-   [How It Works](#how-it-works)\
-   [Building](#building)\
-   [Running](#running)\
-   [CLI Menu](#cli-menu)\
-   [SQL Query Support](#sql-query-support)\
-   [CSV Import/Export](#csv-importexport)\
-   [Inner Join Engine](#inner-join-engine)\
-   [Example Session](#example-session)\
-   [Future Improvements](#future-improvements)\
-   [License](#license)

## ✨ Features

MiniDB provides:

-   **Interactive CLI** for manipulating tables\
-   **Create table** with user-defined attributes\
-   **Insert rows**\
-   **Primary & foreign key support**\
-   **Hash-based indexing** for fast `WHERE col = value` queries\
-   **CSV import & export**\
-   **Simple SQL-like query parser**\
-   **INNER JOIN implementation** using a linked list join structure\
-   **Display and update table rows**

## 📁 Project Structure

    main.cpp      → full implementation of table management and MiniDB CLI
    employees.csv → optional preloaded table (loaded at runtime)
    departments.csv → optional preloaded table (loaded at runtime)

## ⚙️ How It Works

### Table Class

Each table is represented using:

-   `vector<vector<string>> form` → stores header + rows\
-   `unordered_map<string, unordered_map<string, vector<int>>> hash_indexes`
    → column-based hash indexes\
-   Primary key and foreign key columns\
-   CSV import/export\
-   Query operations (`select_where`)\
-   Row insertion and updates

### Query Engine

A minimal SQL-like parser supports:

    SELECT * FROM table WHERE column = value
    SELECT * FROM table WHERE column > value
    SELECT * FROM table WHERE column < value
    ...

### Join Engine

The `inner_join()` function:

-   Matches `left.foreign_key` ↔ `right.primary_key`\
-   Builds a linked list of matches\
-   Prints join relationships during processing\
-   Outputs final merged rows

## 🏗️ Building

### Requirements

-   C++11 or higher\
-   Any standard compiler (g++, clang++, MSVC)

### Build Command

``` bash
g++ main.cpp -o minidb
```

## ▶️ Running the Application

``` bash
./minidb
```

If `employees.csv` and `departments.csv` are present, MiniDB loads them
automatically.

## 📟 CLI Menu

    1. Display table
    2. Run SQL query
    3. Export table to CSV
    4. Inner join
    5. Create new table
    6. Insert into table
    0. Exit

## 🔍 SQL Query Support

Supported operators:

  Operator   Meaning
  ---------- --------------------
  =          Equality (indexed)
  !=         Not equal
  \>, \<     Numeric comparison
  \>=, \<=   Numeric comparison

## 📤 CSV Import/Export

### Import

``` cpp
employees.import_csv("employees.csv");
```

### Export

Exports as `tablename.csv`.

## 🔗 Inner Join Engine

-   Matches PK ↔ FK\
-   Builds `JoinNode(lrow, rrow)` linked list\
-   Prints merged table

## 🧪 Example Session

    SQL: SELECT * FROM employees WHERE deptID = d10

## 🚀 Future Improvements

-   More SQL support\
-   Data types\
-   Storage engine\
-   More join types

## 📜 License

MIT Licensed
