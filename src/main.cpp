#include <iostream>
using namespace std;



class table
{
private:
    vector<vector<string>> form;

public:
    int index_of_attributes = 0;
    int index_for_values = 1;

    void add_attirbute(string name)
    {
        if (form.empty())
        {
            form.push_back({}); // create header
        }
        form[0].push_back(name);
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
};
int main()
{
    table tt;
    tt.add_attirbute("ID");
    tt.add_attirbute("name");
    tt.add_attirbute("dept");
    tt.add_value({"101", "maisum"});
    tt.add_value({"102", "AON", "BSCS"});
    tt.add_value({"103", "Umair"});
    tt.display_table();
    tt.update(2,"name","ALi");
    tt.update(1,"dept","cs");
    tt.display_table();
}