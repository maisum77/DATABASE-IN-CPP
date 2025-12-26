import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import json
from typing import List, Dict, Any

API_BASE = "http://localhost:8080"

class DatabaseGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Database Management System")
        self.root.geometry("1400x900")
        self.root.configure(bg="#1e1b4b")
        
        # Variables
        self.selected_table = None
        self.tables = []
        self.table_data = None
        
        # Style configuration
        self.setup_styles()
        
        # Create main layout
        self.create_header()
        self.create_main_layout()
        
        # Load initial data
        self.refresh_tables()
    
    def setup_styles(self):
        """Configure ttk styles for modern look"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        bg_dark = "#1e1b4b"
        bg_medium = "#312e81"
        bg_light = "#4c1d95"
        purple = "#7c3aed"
        purple_hover = "#6d28d9"
        text_color = "#e0e7ff"
        
        # Frame styles
        style.configure("Card.TFrame", background=bg_medium, relief="flat")
        style.configure("Sidebar.TFrame", background=bg_medium)
        
        # Button styles
        style.configure("Primary.TButton",
                       background=purple,
                       foreground="white",
                       borderwidth=0,
                       focuscolor="none",
                       padding=10)
        style.map("Primary.TButton",
                 background=[("active", purple_hover)])
        
        style.configure("Secondary.TButton",
                       background=bg_light,
                       foreground=text_color,
                       borderwidth=0,
                       focuscolor="none",
                       padding=8)
        
        # Label styles
        style.configure("Title.TLabel",
                       background=bg_dark,
                       foreground="white",
                       font=("Arial", 24, "bold"))
        style.configure("Subtitle.TLabel",
                       background=bg_dark,
                       foreground=text_color,
                       font=("Arial", 10))
        style.configure("Header.TLabel",
                       background=bg_medium,
                       foreground=text_color,
                       font=("Arial", 12, "bold"))
        style.configure("Normal.TLabel",
                       background=bg_medium,
                       foreground=text_color,
                       font=("Arial", 10))
        
        # Entry styles
        style.configure("TEntry",
                       fieldbackground=bg_light,
                       foreground="white",
                       borderwidth=1,
                       insertcolor="white")
        
        # Combobox styles
        style.configure("TCombobox",
                       fieldbackground=bg_light,
                       background=bg_light,
                       foreground="white",
                       arrowcolor="white")
        
        # Notebook (Tab) styles
        style.configure("TNotebook",
                       background=bg_dark,
                       borderwidth=0)
        style.configure("TNotebook.Tab",
                       background=bg_medium,
                       foreground=text_color,
                       padding=[20, 10])
        style.map("TNotebook.Tab",
                 background=[("selected", purple)],
                 foreground=[("selected", "white")])
    
    def create_header(self):
        """Create top header with title and actions"""
        header = tk.Frame(self.root, bg="#1e1b4b", height=80)
        header.pack(fill=tk.X, padx=20, pady=(20, 10))
        header.pack_propagate(False)
        
        # Left side - Title
        left_frame = tk.Frame(header, bg="#1e1b4b")
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        title_label = ttk.Label(left_frame, text="🗄️ Database Manager", style="Title.TLabel")
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(left_frame, text="Professional Data Management System", 
                                   style="Subtitle.TLabel")
        subtitle_label.pack(anchor=tk.W)
        
        # Right side - Actions
        right_frame = tk.Frame(header, bg="#1e1b4b")
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        new_table_btn = ttk.Button(right_frame, text="➕ New Table",
                                   style="Primary.TButton",
                                   command=self.show_create_table_dialog)
        new_table_btn.pack(side=tk.RIGHT, padx=5)
        
        refresh_btn = ttk.Button(right_frame, text="🔄 Refresh",
                                style="Secondary.TButton",
                                command=self.refresh_tables)
        refresh_btn.pack(side=tk.RIGHT, padx=5)
    
    def create_main_layout(self):
        """Create main content area with sidebar and content"""
        main_container = tk.Frame(self.root, bg="#1e1b4b")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Sidebar
        self.create_sidebar(main_container)
        
        # Content area
        self.create_content_area(main_container)
    
    def create_sidebar(self, parent):
        """Create left sidebar with table list"""
        sidebar = ttk.Frame(parent, style="Sidebar.TFrame", width=250)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        sidebar.pack_propagate(False)
        
        # Tables header
        tables_header = ttk.Label(sidebar, text="📊 TABLES", style="Header.TLabel")
        tables_header.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        # Tables listbox
        self.tables_listbox = tk.Listbox(sidebar,
                                         bg="#4c1d95",
                                         fg="white",
                                         selectbackground="#7c3aed",
                                         selectforeground="white",
                                         font=("Arial", 11),
                                         borderwidth=0,
                                         highlightthickness=0)
        self.tables_listbox.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        self.tables_listbox.bind('<<ListboxSelect>>', self.on_table_select)
        
        # Quick actions frame
        actions_frame = tk.Frame(sidebar, bg="#312e81")
        actions_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        export_btn = ttk.Button(actions_frame, text="💾 Export Table",
                               style="Secondary.TButton",
                               command=self.export_selected_table)
        export_btn.pack(fill=tk.X, pady=2)
        
        join_btn = ttk.Button(actions_frame, text="🔗 Quick Join",
                             style="Secondary.TButton",
                             command=self.show_join_dialog)
        join_btn.pack(fill=tk.X, pady=2)
    
    def create_content_area(self, parent):
        """Create main content area with tabs"""
        content_frame = ttk.Frame(parent, style="Card.TFrame")
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Schema Tab
        self.schema_tab = self.create_schema_tab()
        self.notebook.add(self.schema_tab, text="Schema")
        
        # Query Tab
        self.query_tab = self.create_query_tab()
        self.notebook.add(self.query_tab, text="Query")
        
        # Data Tab
        self.data_tab = self.create_data_tab()
        self.notebook.add(self.data_tab, text="Data")
    
    def create_schema_tab(self):
        """Create schema visualization tab"""
        tab = tk.Frame(self.notebook, bg="#312e81")
        
        # Header
        header = ttk.Label(tab, text="Table Structure", style="Header.TLabel")
        header.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        # Schema container with scrollbar
        schema_container = tk.Frame(tab, bg="#312e81")
        schema_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scrollbar = tk.Scrollbar(schema_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.schema_canvas = tk.Canvas(schema_container,
                                       bg="#312e81",
                                       highlightthickness=0)
        self.schema_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.schema_canvas.yview)
        self.schema_canvas.config(yscrollcommand=scrollbar.set)
        
        self.schema_frame = tk.Frame(self.schema_canvas, bg="#312e81")
        self.schema_canvas.create_window((0, 0), window=self.schema_frame, anchor=tk.NW)
        
        return tab
    
    def create_query_tab(self):
        """Create query interface tab"""
        tab = tk.Frame(self.notebook, bg="#312e81")
        
        # Query mode selector
        mode_frame = tk.Frame(tab, bg="#312e81")
        mode_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        self.query_mode = tk.StringVar(value="standard")
        
        standard_radio = tk.Radiobutton(mode_frame,
                                       text="🔍 Standard Query",
                                       variable=self.query_mode,
                                       value="standard",
                                       bg="#312e81",
                                       fg="white",
                                       selectcolor="#7c3aed",
                                       font=("Arial", 11, "bold"),
                                       command=self.toggle_query_mode)
        standard_radio.pack(side=tk.LEFT, padx=10)
        
        nlp_radio = tk.Radiobutton(mode_frame,
                                  text="⚡ Natural Language",
                                  variable=self.query_mode,
                                  value="nlp",
                                  bg="#312e81",
                                  fg="white",
                                  selectcolor="#7c3aed",
                                  font=("Arial", 11, "bold"),
                                  command=self.toggle_query_mode)
        nlp_radio.pack(side=tk.LEFT, padx=10)
        
        # Standard query frame
        self.standard_query_frame = tk.Frame(tab, bg="#1e1b4b")
        self.standard_query_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Query builder
        query_grid = tk.Frame(self.standard_query_frame, bg="#1e1b4b")
        query_grid.pack(fill=tk.X, pady=10)
        
        # Table selection
        ttk.Label(query_grid, text="Table:", style="Normal.TLabel").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.query_table = ttk.Combobox(query_grid, width=20, state="readonly")
        self.query_table.grid(row=0, column=1, padx=5, pady=5)
        
        # Column
        ttk.Label(query_grid, text="Column:", style="Normal.TLabel").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.query_column = ttk.Entry(query_grid, width=20)
        self.query_column.grid(row=0, column=3, padx=5, pady=5)
        
        # Operator
        ttk.Label(query_grid, text="Operator:", style="Normal.TLabel").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.query_operator = ttk.Combobox(query_grid, width=20, state="readonly",
                                          values=["=", ">", "<", ">=", "<=", "!="])
        self.query_operator.current(0)
        self.query_operator.grid(row=1, column=1, padx=5, pady=5)
        
        # Value
        ttk.Label(query_grid, text="Value:", style="Normal.TLabel").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.query_value = ttk.Entry(query_grid, width=20)
        self.query_value.grid(row=1, column=3, padx=5, pady=5)
        
        # Execute button
        execute_btn = ttk.Button(self.standard_query_frame, text="▶️ Execute Query",
                                style="Primary.TButton",
                                command=self.execute_standard_query)
        execute_btn.pack(pady=10)
        
        # NLP query frame
        self.nlp_query_frame = tk.Frame(tab, bg="#1e1b4b")
        
        ttk.Label(self.nlp_query_frame, text="Natural Language Query:", 
                 style="Normal.TLabel").pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        self.nlp_text = scrolledtext.ScrolledText(self.nlp_query_frame,
                                                  height=4,
                                                  bg="#4c1d95",
                                                  fg="white",
                                                  font=("Arial", 11),
                                                  insertbackground="white")
        self.nlp_text.pack(fill=tk.X, padx=10, pady=5)
        self.nlp_text.insert("1.0", "Try: Show employees where empID = 1")
        
        nlp_execute_btn = ttk.Button(self.nlp_query_frame, text="⚡ Execute Natural Language Query",
                                    style="Primary.TButton",
                                    command=self.execute_nlp_query)
        nlp_execute_btn.pack(pady=10)
        
        # Results area
        results_label = ttk.Label(tab, text="Query Results:", style="Header.TLabel")
        results_label.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        results_container = tk.Frame(tab, bg="#312e81")
        results_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.query_results_tree = self.create_treeview(results_container)
        
        return tab
    
    def create_data_tab(self):
        """Create data view tab"""
        tab = tk.Frame(self.notebook, bg="#312e81")
        
        header = ttk.Label(tab, text="Table Data", style="Header.TLabel")
        header.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        data_container = tk.Frame(tab, bg="#312e81")
        data_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.data_tree = self.create_treeview(data_container)
        
        return tab
    
    def create_treeview(self, parent):
        """Create a styled treeview widget"""
        tree_frame = tk.Frame(parent, bg="#312e81")
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        vsb = tk.Scrollbar(tree_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        hsb = tk.Scrollbar(tree_frame, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        tree = ttk.Treeview(tree_frame,
                           yscrollcommand=vsb.set,
                           xscrollcommand=hsb.set)
        tree.pack(fill=tk.BOTH, expand=True)
        
        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)
        
        # Style
        style = ttk.Style()
        style.configure("Treeview",
                       background="#4c1d95",
                       foreground="white",
                       fieldbackground="#4c1d95",
                       borderwidth=0)
        style.configure("Treeview.Heading",
                       background="#7c3aed",
                       foreground="white",
                       borderwidth=0)
        style.map('Treeview', background=[('selected', '#6d28d9')])
        
        return tree
    
    def toggle_query_mode(self):
        """Toggle between standard and NLP query modes"""
        if self.query_mode.get() == "standard":
            self.nlp_query_frame.pack_forget()
            self.standard_query_frame.pack(fill=tk.X, padx=20, pady=10)
        else:
            self.standard_query_frame.pack_forget()
            self.nlp_query_frame.pack(fill=tk.X, padx=20, pady=10)
    
    def refresh_tables(self):
        """Fetch and display list of tables"""
        try:
            response = requests.get(f"{API_BASE}/tables", timeout=5)
            if response.status_code == 200:
                self.tables = response.json()
                self.tables_listbox.delete(0, tk.END)
                for table in self.tables:
                    self.tables_listbox.insert(tk.END, f"  {table}")
                
                # Update query table dropdown
                self.query_table['values'] = self.tables
                if self.tables:
                    self.query_table.current(0)
            else:
                messagebox.showerror("Error", "Failed to fetch tables")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot connect to server:\n{str(e)}")
    
    def on_table_select(self, event):
        """Handle table selection from sidebar"""
        selection = self.tables_listbox.curselection()
        if selection:
            table_name = self.tables_listbox.get(selection[0]).strip()
            self.selected_table = table_name
            self.load_table_data(table_name)
            self.display_schema(table_name)
    
    def load_table_data(self, table_name):
        """Load table data and display in data tab"""
        try:
            response = requests.get(f"{API_BASE}/table/{table_name}", timeout=5)
            if response.status_code == 200:
                self.table_data = response.json()
                self.display_table_data(self.data_tree, self.table_data)
            else:
                messagebox.showerror("Error", f"Failed to load table: {table_name}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def display_schema(self, table_name):
        """Display table schema in schema tab"""
        # Clear existing schema
        for widget in self.schema_frame.winfo_children():
            widget.destroy()
        
        if not self.table_data or len(self.table_data) == 0:
            return
        
        # Table name header
        table_label = tk.Label(self.schema_frame,
                              text=f"Table: {table_name}",
                              bg="#312e81",
                              fg="white",
                              font=("Arial", 16, "bold"))
        table_label.pack(fill=tk.X, padx=10, pady=(10, 20))
        
        # Display columns
        columns = self.table_data[0]
        for idx, col in enumerate(columns):
            # Determine key type
            is_pk = 'id' in col.lower() and idx == 0
            is_fk = 'deptid' in col.lower() or 'dept_id' in col.lower()
            
            # Column frame
            col_frame = tk.Frame(self.schema_frame, bg="#4c1d95", relief=tk.RAISED, borderwidth=1)
            col_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Icon and name
            icon = "🔑" if is_pk else ("🔗" if is_fk else "📋")
            col_label = tk.Label(col_frame,
                               text=f"{icon}  {col}",
                               bg="#4c1d95",
                               fg="white",
                               font=("Arial", 12, "bold"),
                               anchor=tk.W)
            col_label.pack(side=tk.LEFT, padx=15, pady=10)
            
            # Key type badge
            if is_pk:
                badge = tk.Label(col_frame,
                               text="PRIMARY KEY",
                               bg="#fbbf24",
                               fg="#1e1b4b",
                               font=("Arial", 9, "bold"),
                               padx=8,
                               pady=2)
                badge.pack(side=tk.RIGHT, padx=15, pady=10)
            elif is_fk:
                badge = tk.Label(col_frame,
                               text="FOREIGN KEY",
                               bg="#60a5fa",
                               fg="#1e1b4b",
                               font=("Arial", 9, "bold"),
                               padx=8,
                               pady=2)
                badge.pack(side=tk.RIGHT, padx=15, pady=10)
        
        # Update scroll region
        self.schema_frame.update_idletasks()
        self.schema_canvas.config(scrollregion=self.schema_canvas.bbox("all"))
    
    def display_table_data(self, tree, data):
        """Display data in treeview"""
        # Clear existing data
        tree.delete(*tree.get_children())
        
        if not data or len(data) == 0:
            return
        
        # Configure columns
        columns = data[0]
        tree['columns'] = columns
        tree['show'] = 'headings'
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor=tk.W)
        
        # Insert data
        for row in data[1:]:
            tree.insert('', tk.END, values=row)
    
    def execute_standard_query(self):
        """Execute standard SQL-like query"""
        table = self.query_table.get()
        column = self.query_column.get()
        operator = self.query_operator.get()
        value = self.query_value.get()
        
        if not all([table, column, value]):
            messagebox.showwarning("Warning", "Please fill all query fields")
            return
        
        try:
            response = requests.post(f"{API_BASE}/query",
                                    json={
                                        "table": table,
                                        "column": column,
                                        "operator": operator,
                                        "value": value
                                    },
                                    timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                self.display_table_data(self.query_results_tree, result)
                messagebox.showinfo("Success", f"Query returned {len(result)-1 if result else 0} rows")
            else:
                messagebox.showerror("Error", "Query failed")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def execute_nlp_query(self):
        """Execute natural language query"""
        query_text = self.nlp_text.get("1.0", tk.END).strip().lower()
        
        # Simple NLP parsing
        params = {"table": "", "column": "", "operator": "=", "value": ""}
        
        # Find table
        for table in self.tables:
            if table.lower() in query_text:
                params["table"] = table
                break
        
        # Find operator
        if "greater than" in query_text or ">" in query_text:
            params["operator"] = ">"
        elif "less than" in query_text or "<" in query_text:
            params["operator"] = "<"
        elif "not equal" in query_text or "!=" in query_text:
            params["operator"] = "!="
        
        # Find value (numbers)
        import re
        numbers = re.findall(r'\d+', query_text)
        if numbers:
            params["value"] = numbers[0]
        
        # Find column (common patterns)
        columns = ['empid', 'deptid', 'name', 'salary', 'department']
        for col in columns:
            if col in query_text:
                params["column"] = col
                break
        
        # Execute if we have enough info
        if params["table"] and params["column"] and params["value"]:
            self.query_table.set(params["table"])
            self.query_column.delete(0, tk.END)
            self.query_column.insert(0, params["column"])
            self.query_operator.set(params["operator"])
            self.query_value.delete(0, tk.END)
            self.query_value.insert(0, params["value"])
            
            self.execute_standard_query()
        else:
            messagebox.showwarning("Parse Error",
                                 "Could not parse query. Try:\n'Show employees where empID = 1'")
    
    def export_selected_table(self):
        """Export selected table to CSV"""
        if not self.selected_table:
            messagebox.showwarning("Warning", "Please select a table first")
            return
        
        try:
            response = requests.post(f"{API_BASE}/table/{self.selected_table}/export",
                                    json={},
                                    timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                filename = result.get('file', f"{self.selected_table}.csv")
                messagebox.showinfo("Success", f"Table exported to {filename}")
            else:
                messagebox.showerror("Error", "Export failed")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def show_join_dialog(self):
        """Show dialog for joining tables"""
        if len(self.tables) < 2:
            messagebox.showwarning("Warning", "Need at least 2 tables to join")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Join Tables")
        dialog.geometry("400x250")
        dialog.configure(bg="#1e1b4b")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Content
        ttk.Label(dialog, text="Select tables to join:", style="Normal.TLabel").pack(pady=20)
        
        ttk.Label(dialog, text="Left Table:", style="Normal.TLabel").pack(pady=5)
        left_combo = ttk.Combobox(dialog, values=self.tables, state="readonly", width=30)
        left_combo.current(0)
        left_combo.pack(pady=5)
        
        ttk.Label(dialog, text="Right Table:", style="Normal.TLabel").pack(pady=5)
        right_combo = ttk.Combobox(dialog, values=self.tables, state="readonly", width=30)
        if len(self.tables) > 1:
            right_combo.current(1)
        right_combo.pack(pady=5)
        
        def execute_join():
            left = left_combo.get()
            right = right_combo.get()
            
            try:
                response = requests.post(f"{API_BASE}/join",
                                        json={"left_table": left, "right_table": right},
                                        timeout=5)
                
                if response.status_code == 200:
                    result = response.json()
                    self.display_table_data(self.query_results_tree, result)
                    self.notebook.select(1)  # Switch to query tab
                    messagebox.showinfo("Success", f"Join returned {len(result)-1 if result else 0} rows")
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Join failed")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        join_btn = ttk.Button(dialog, text="Execute Join", style="Primary.TButton", command=execute_join)
        join_btn.pack(pady=20)
    
    def show_create_table_dialog(self):
        """Show dialog for creating new table"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Create New Table")
        dialog.geometry("500x600")
        dialog.configure(bg="#1e1b4b")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Scrollable content
        canvas = tk.Canvas(dialog, bg="#1e1b4b", highlightthickness=0)
        scrollbar = tk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#1e1b4b")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y")
        
        # Form fields
        ttk.Label(scrollable_frame, text="Table Name:", style="Normal.TLabel").pack(pady=(10, 5))
        name_entry = ttk.Entry(scrollable_frame, width=40)
        name_entry.pack(pady=5)
        
        ttk.Label(scrollable_frame, text="Columns (one per line):", style="Normal.TLabel").pack(pady=(10, 5))
        columns_text = scrolledtext.ScrolledText(scrollable_frame, height=8, width=40,
                                                bg="#4c1d95",
                                                fg="white",
                                                insertbackground="white")
        columns_text.pack(pady=5)
        
        ttk.Label(scrollable_frame, text="Primary Key:", style="Normal.TLabel").pack(pady=(10, 5))
        pk_entry = ttk.Entry(scrollable_frame, width=40)
        pk_entry.pack(pady=5)
        
        ttk.Label(scrollable_frame, text="Foreign Key (optional):", style="Normal.TLabel").pack(pady=(10, 5))
        fk_entry = ttk.Entry(scrollable_frame, width=40)
        fk_entry.pack(pady=5)
        
        def create_table():
            name = name_entry.get().strip()
            columns = [c.strip() for c in columns_text.get("1.0", tk.END).strip().split('\n') if c.strip()]
            pk = pk_entry.get().strip()
            fk = fk_entry.get().strip()
            
            if not name or not columns:
                messagebox.showwarning("Warning", "Please provide table name and at least one column")
                return
            
            try:
                payload = {
                    "name": name,
                    "columns": columns,
                    "primary_key": pk,
                    "foreign_key": fk
                }
                
                response = requests.post(f"{API_BASE}/table",
                                        json=payload,
                                        timeout=5)
                
                if response.status_code == 200:
                    messagebox.showinfo("Success", f"Table '{name}' created successfully")
                    self.refresh_tables()
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Failed to create table")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        # Buttons
        btn_frame = tk.Frame(scrollable_frame, bg="#1e1b4b")
        btn_frame.pack(pady=20)
        
        create_btn = ttk.Button(btn_frame, text="Create Table", style="Primary.TButton", command=create_table)
        create_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(btn_frame, text="Cancel", style="Secondary.TButton", command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)


def main():
    root = tk.Tk()
    app = DatabaseGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()