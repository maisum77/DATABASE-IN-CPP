#include <iostream>
#include <unordered_map>
#include <vector>
#include <fstream>
#include <sstream>
#include <cctype>
#include "httplib.h"
#include <nlohmann/json.hpp>

using namespace std;
using json = nlohmann::json;

struct JoinNode {
    int left_row;
    int right_row;
    JoinNode *next = nullptr;
    JoinNode(int l, int r) : left_row(l), right_row(r) {}
};

class table {
public:
    vector<vector<string>> form;
    unordered_map<string, unordered_map<string, vector<int>>> hash_indexes;
    string pk_col;
    string fk_col;
    int pk_idx = -1;
    int fk_idx = -1;

    void set_primary_key(const string &col) { pk_col = col; }
    void set_foreign_key(const string &col) { fk_col = col; }

    void add_attribute(string name) {
        if (form.empty()) form.push_back({});
        form[0].push_back(name);
        if (name == pk_col) pk_idx = form[0].size() - 1;
        if (name == fk_col) fk_idx = form[0].size() - 1;
    }

    void add_value(const vector<string> &values) {
        vector<string> row(form[0].size(), "null");
        for (int i = 0; i < values.size() && i < row.size(); ++i) {
            row[i] = values[i];
        }
        form.push_back(row);
    }

    void build_hash_index(const string &col) {
        int col_idx = -1;
        for (size_t i = 0; i < form[0].size(); ++i)
            if (form[0][i] == col) { col_idx = i; break; }
        if (col_idx == -1) return;
        
        auto &idx = hash_indexes[col];
        idx.clear();
        for (size_t r = 1; r < form.size(); ++r)
            idx[form[r][col_idx]].push_back(r);
    }

    bool import_csv(const string &file_name) {
        ifstream fin(file_name);
        if (!fin) return false;
        
        string line;
        bool first = true;
        while (getline(fin, line)) {
            if (line.empty()) continue;
            stringstream ss(line);
            string cell;
            vector<string> row;
            while (getline(ss, cell, ',')) row.push_back(cell);
            
            if (first) {
                form.clear();
                form.push_back(row);
                first = false;
                for (int i = 0; i < row.size(); ++i) {
                    if (row[i] == pk_col) pk_idx = i;
                    if (row[i] == fk_col) fk_idx = i;
                }
            } else {
                add_value(row);
            }
        }
        return true;
    }

    bool export_csv(const string &file_name) const {
        ofstream fout(file_name);
        if (!fout) return false;
        
        for (const auto &row : form) {
            for (size_t i = 0; i < row.size(); ++i) {
                fout << row[i];
                if (i + 1 != row.size()) fout << ',';
            }
            fout << '\n';
        }
        return true;
    }

    json to_json() const {
        json result = json::array();
        for (const auto &row : form) {
            result.push_back(row);
        }
        return result;
    }

    json select_where_json(const string &col_name, const string &op, const string &value) {
        json result = json::array();
        if (form.empty()) return result;
        
        int col_idx = -1;
        for (int i = 0; i < form[0].size(); ++i) {
            if (form[0][i] == col_name) { col_idx = i; break; }
        }
        if (col_idx == -1) return result;
        
        result.push_back(form[0]); // header
        
        for (int r = 1; r < form.size(); ++r) {
            string cell = form[r][col_idx];
            bool match = false;
            
            if (op == "=") match = (cell == value);
            else if (op == ">") match = (stoi(cell) > stoi(value));
            else if (op == "<") match = (stoi(cell) < stoi(value));
            else if (op == ">=") match = (stoi(cell) >= stoi(value));
            else if (op == "<=") match = (stoi(cell) <= stoi(value));
            else if (op == "!=") match = (cell != value);
            
            if (match) result.push_back(form[r]);
        }
        return result;
    }
};

unordered_map<string, table> database;

JoinNode* inner_join(const table &left, const table &right) {
    unordered_map<string, int> right_pk_map;
    for (int r = 1; r < right.form.size(); ++r) {
        if (right.pk_idx < right.form[r].size())
            right_pk_map[right.form[r][right.pk_idx]] = r;
    }
    
    JoinNode dummy(0, 0);
    JoinNode *tail = &dummy;
    
    for (int l = 1; l < left.form.size(); ++l) {
        if (left.fk_idx >= left.form[l].size()) continue;
        string fk_val = left.form[l][left.fk_idx];
        auto it = right_pk_map.find(fk_val);
        if (it != right_pk_map.end()) {
            tail->next = new JoinNode(l, it->second);
            tail = tail->next;
        }
    }
    return dummy.next;
}

json join_to_json(const table &left, const table &right, JoinNode *join_head) {
    json result = json::array();
    if (!join_head) return result;
    
    // Header
    vector<string> header;
    for (const string &h : left.form[0]) header.push_back(h);
    for (const string &h : right.form[0]) header.push_back(h);
    result.push_back(header);
    
    // Data rows
    for (JoinNode *node = join_head; node; node = node->next) {
        vector<string> row;
        for (const string &cell : left.form[node->left_row]) row.push_back(cell);
        for (const string &cell : right.form[node->right_row]) row.push_back(cell);
        result.push_back(row);
    }
    return result;
}

int main() {
    httplib::Server svr;
    
    // Load default tables
    table employees, departments;
    employees.set_primary_key("empID");
    employees.set_foreign_key("deptID");
    employees.import_csv("employees.csv");
    
    departments.set_primary_key("deptID");
    departments.import_csv("departments.csv");
    
    database["employees"] = employees;
    database["departments"] = departments;
    
    // Health check
    svr.Get("/health", [](const httplib::Request&, httplib::Response& res) {
        res.set_content("{\"status\":\"ok\"}", "application/json");
    });
    
    // List all tables
    svr.Get("/tables", [](const httplib::Request&, httplib::Response& res) {
        json result = json::array();
        for (const auto &pair : database) {
            result.push_back(pair.first);
        }
        res.set_content(result.dump(), "application/json");
    });
    
    // Get table data
    svr.Get("/table/:name", [](const httplib::Request& req, httplib::Response& res) {
        string name = req.path_params.at("name");
        auto it = database.find(name);
        if (it == database.end()) {
            res.status = 404;
            res.set_content("{\"error\":\"Table not found\"}", "application/json");
            return;
        }
        res.set_content(it->second.to_json().dump(), "application/json");
    });
    
    // Create table
    svr.Post("/table", [](const httplib::Request& req, httplib::Response& res) {
        json body = json::parse(req.body);
        string name = body["name"];
        
        if (database.count(name)) {
            res.status = 400;
            res.set_content("{\"error\":\"Table already exists\"}", "application/json");
            return;
        }
        
        table t;
        if (body.contains("primary_key")) t.set_primary_key(body["primary_key"]);
        if (body.contains("foreign_key")) t.set_foreign_key(body["foreign_key"]);
        
        for (const auto &col : body["columns"]) {
            t.add_attribute(col);
        }
        
        database[name] = t;
        res.set_content("{\"success\":true}", "application/json");
    });
    
    // Insert row
    svr.Post("/table/:name/insert", [](const httplib::Request& req, httplib::Response& res) {
        string name = req.path_params.at("name");
        auto it = database.find(name);
        if (it == database.end()) {
            res.status = 404;
            res.set_content("{\"error\":\"Table not found\"}", "application/json");
            return;
        }
        
        json body = json::parse(req.body);
        vector<string> values;
        for (const auto &val : body["values"]) {
            values.push_back(val);
        }
        
        it->second.add_value(values);
        res.set_content("{\"success\":true}", "application/json");
    });
    
    // Query with WHERE
    svr.Post("/query", [](const httplib::Request& req, httplib::Response& res) {
        json body = json::parse(req.body);
        string table_name = body["table"];
        string col = body["column"];
        string op = body["operator"];
        string val = body["value"];
        
        auto it = database.find(table_name);
        if (it == database.end()) {
            res.status = 404;
            res.set_content("{\"error\":\"Table not found\"}", "application/json");
            return;
        }
        
        json result = it->second.select_where_json(col, op, val);
        res.set_content(result.dump(), "application/json");
    });
    
    // Inner join
    svr.Post("/join", [](const httplib::Request& req, httplib::Response& res) {
        json body = json::parse(req.body);
        string left_name = body["left_table"];
        string right_name = body["right_table"];
        
        auto it1 = database.find(left_name);
        auto it2 = database.find(right_name);
        
        if (it1 == database.end() || it2 == database.end()) {
            res.status = 404;
            res.set_content("{\"error\":\"One or both tables not found\"}", "application/json");
            return;
        }
        
        JoinNode *j = inner_join(it1->second, it2->second);
        json result = join_to_json(it1->second, it2->second, j);
        res.set_content(result.dump(), "application/json");
    });
    
    // Export to CSV
    svr.Post("/table/:name/export", [](const httplib::Request& req, httplib::Response& res) {
        string name = req.path_params.at("name");
        auto it = database.find(name);
        if (it == database.end()) {
            res.status = 404;
            res.set_content("{\"error\":\"Table not found\"}", "application/json");
            return;
        }
        
        string filename = name + ".csv";
        if (it->second.export_csv(filename)) {
            res.set_content("{\"success\":true,\"file\":\"" + filename + "\"}", "application/json");
        } else {
            res.status = 500;
            res.set_content("{\"error\":\"Export failed\"}", "application/json");
        }
    });
    
    cout << "Server starting on http://localhost:8080" << endl;
    svr.listen("0.0.0.0", 8080);
    
    return 0;
}