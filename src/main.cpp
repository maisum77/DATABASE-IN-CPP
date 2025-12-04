#include <iostream>
#include <unordered_map>
#include <vector>
#include <fstream>
#include <sstream>
using namespace std;
struct JoinNode
{
    int left_row;  // index in left table
    int right_row; // index in right table
    JoinNode *next = nullptr;
    JoinNode(int l, int r) : left_row(l), right_row(r) {}
};

class table
{
public:
    vector<vector<string>> form;
    string pk_col; // primary-key column name
    string fk_col; // foreign-key column name
    int pk_idx = -1;
    int fk_idx = -1;

public:
    int index_of_attributes = 0;
    int index_for_values = 1;
    void set_primary_key(const string &col)
    {
        pk_col = col;
    }
    void set_foreign_key(const string &col)
    {
        fk_col = col;
    }

    void add_attribute(string name)
    {
        if (form.empty())
        {
            form.push_back({}); // create header
        }
        form[0].push_back(name);

        // Check if this is the primary or foreign key AFTER adding
        if (name == pk_col)
            pk_idx = form[0].size() - 1;
        if (name == fk_col)
            fk_idx = form[0].size() - 1;
    }

    void add_value(const vector<string> &values)
    {
        vector<string> row(form[0].size(), "null");
        for (int i = 0; i < values.size() && i < row.size(); ++i)
        {
            row[i] = values[i];
        }
        form.push_back(row);
    }
    void update(int row_index, const string &col_name, const string &new_value)
    {
        if (form.empty() || row_index < 1 || row_index >= form.size())
        {
            cout << "[Error] Invalid row index.\n";
            return;
        }

        int col_idx = -1;
        for (int i = 0; i < form[0].size(); ++i)
        {
            if (form[0][i] == col_name)
            {
                col_idx = i;
                break;
            }
        }

        if (col_idx == -1)
        {
            cout << "[Error] Column '" << col_name << "' not found.\n";
            return;
        }

        form[row_index][col_idx] = new_value;
    }

    void display_table()
    {
        for (const auto &row : form)
        {
            for (const string &cell : row)
            {
                cout << cell << "\t";
            }
            cout << endl;
        }
    }
    bool import_csv(const string &file_name)
    {
        ifstream fin(file_name);
        if (!fin)
            return false;

        string line;
        bool first = true;
        while (getline(fin, line))
        {
            if (line.empty())
                continue;
            stringstream ss(line);
            string cell;
            vector<string> row;
            while (getline(ss, cell, ','))
                row.push_back(cell);

            if (first)
            {                 // header line
                form.clear(); // wipe old content
                form.push_back(row);
                first = false;
                /* rebuild pk/fk indices if column names match */
                for (int i = 0; i < row.size(); ++i)
                {
                    if (row[i] == pk_col)
                        pk_idx = i;
                    if (row[i] == fk_col)
                        fk_idx = i;
                }
            }
            else
            {                   // data line
                add_value(row); // reuse existing null-padding logic
            }
        }
        return true;
    }

    bool export_csv(const string &file_name) const
    {
        ofstream fout(file_name);
        if (!fout)
            return false;

        for (const auto &row : form)
        {
            for (size_t i = 0; i < row.size(); ++i)
            {
                fout << row[i];
                if (i + 1 != row.size())
                    fout << ',';
            }
            fout << '\n';
        }
        return true;
    }
};
// Standalone function for inner join
JoinNode *inner_join(const table &left, const table &right)
{
    // right PK -> row index
    unordered_map<string, int> right_pk_map;
    for (int r = 1; r < right.form.size(); ++r)
    {
        if (right.pk_idx < right.form[r].size())
            right_pk_map[right.form[r][right.pk_idx]] = r;
    }

    JoinNode dummy(0, 0); // head sentinel
    JoinNode *tail = &dummy;

    // scan left
    for (int l = 1; l < left.form.size(); ++l)
    {
        if (left.fk_idx >= left.form[l].size())
            continue;
        string fk_val = left.form[l][left.fk_idx];
        auto it = right_pk_map.find(fk_val);
        if (it != right_pk_map.end())
        {
            tail->next = new JoinNode(l, it->second);
            tail = tail->next;
            // *** PRINT THE LINK IMMEDIATELY ***
            cout << "JOIN: left[" << l << "] (FK=" << fk_val
                 << ")  -->  right[" << it->second << "] (PK=" << fk_val << ")\n";
        }
    }
    return dummy.next;
}

// Standalone function to print join results
void print_join(const table &left, const table &right, JoinNode *head)
{
    // header
    for (const string &h : left.form[0])
        cout << h << '\t';
    cout << "|\t";
    for (const string &h : right.form[0])
        cout << h << '\t';
    cout << '\n';

    // data rows
    for (JoinNode *p = head; p; p = p->next)
    {
        for (const string &cell : left.form[p->left_row])
            cout << cell << '\t';
        cout << "|\t";
        for (const string &cell : right.form[p->right_row])
            cout << cell << '\t';
        cout << '\n';
    }
}

int main()
{
    table employees;
    employees.set_primary_key("empID");
    employees.set_foreign_key("deptID");
    employees.add_attribute("empID");
    employees.add_attribute("name");
    employees.add_attribute("deptID");
    employees.add_value({"101", "maisum", "d10"});
    employees.add_value({"102", "AON", "d20"});
    employees.add_value({"103", "Umair", "d10"});

    table departments;
    departments.set_primary_key("deptID");
    departments.add_attribute("deptID");
    departments.add_attribute("deptName");
    departments.add_value({"d10", "CS"});
    departments.add_value({"d20", "EE"});

    // cout << "\n=== EMPLOYEES TABLE ===\n";
    // employees.display_table();

    // cout << "\n=== DEPARTMENTS TABLE ===\n";
    // departments.display_table();

    // cout << "\n=== PERFORMING INNER JOIN ===\n";
    // JoinNode *joined = inner_join(employees, departments);

    // cout << "\n=== JOIN RESULT ===\n";
    // print_join(employees, departments, joined);

    employees.export_csv("employees.csv"); // write current table
    departments.export_csv("departments.csv");

    table temp;
    temp.import_csv("employees.csv"); // read it back
    temp.display_table();
}