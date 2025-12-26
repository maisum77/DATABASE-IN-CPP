import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import json
from typing import List, Dict, Any

API_BASE = "http://localhost:8080"

# ============= MODERN COLOR SYSTEM =============
COLORS = {
    'bg_primary': "#0f172a",      # Deep slate
    'bg_secondary': "#1e293b",    # Slate-800
    'bg_card': "#334155",         # Slate-700
    'accent': "#0ea5e9",          # Sky-500 (professional blue)
    'accent_hover': "#0284c7",    # Sky-600
    'success': "#10b981",         # Emerald
    'warning': "#f59e0b",         # Amber
    'error': "#ef4444",           # Red
    'text_primary': "#f1f5f9",    # Slate-100
    'text_secondary': "#cbd5e1",  # Slate-300
    'border': "#475569",          # Slate-600
    'row_hover': "#1e40af",       # Indigo accent for rows
}

# ============= TYPOGRAPHY =============
FONTS = {
    'title': ("Segoe UI", 24, "bold"),
    'subtitle': ("Segoe UI", 11),
    'header': ("Segoe UI", 12, "bold"),
    'body': ("Segoe UI", 10),
    'monospace': ("JetBrains Mono", 10),  # Better for data
}

class ModernDatabaseGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DataSphere Pro")
        self.root.geometry("1600x900")
        self.root.configure(bg=COLORS['bg_primary'])
        
        # Center window
        self.root.eval('tk::PlaceWindow . center')
        
        # Variables
        self.selected_table = None
        self.tables = []
        self.table_data = None
        
        # Configure styles
        self.setup_styles()
        
        # Layout
        self.create_header()
        self.create_main_layout()
        
        # Load data
        self.refresh_tables()
    
    def setup_styles(self):
        """Centralized styling with modern design system"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame styles
        style.configure("Card.TFrame", 
                       background=COLORS['bg_card'], 
                       relief="flat")
        style.configure("Sidebar.TFrame", 
                       background=COLORS['bg_secondary'])
        
        # Button styles
        style.configure("Primary.TButton",
                       background=COLORS['accent'],
                       foreground=COLORS['text_primary'],
                       borderwidth=0,
                       focuscolor="none",
                       padding=(16, 10),
                       font=FONTS['body'])
        style.map("Primary.TButton",
                 background=[("active", COLORS['accent_hover'])],
                 foreground=[("active", "white")])
        
        style.configure("Secondary.TButton",
                       background=COLORS['bg_secondary'],
                       foreground=COLORS['text_secondary'],
                       borderwidth=1,
                       bordercolor=COLORS['border'],
                       focuscolor="none",
                       padding=(12, 8),
                       font=FONTS['body'])
        style.map("Secondary.TButton",
                 background=[("active", COLORS['bg_card'])])
        
        # Label styles
        style.configure("Title.TLabel",
                       background=COLORS['bg_primary'],
                       foreground=COLORS['text_primary'],
                       font=FONTS['title'])
        style.configure("Subtitle.TLabel",
                       background=COLORS['bg_primary'],
                       foreground=COLORS['text_secondary'],
                       font=FONTS['subtitle'])
        style.configure("Header.TLabel",
                       background=COLORS['bg_card'],
                       foreground=COLORS['text_primary'],
                       font=FONTS['header'])
        style.configure("Normal.TLabel",
                       background=COLORS['bg_card'],
                       foreground=COLORS['text_secondary'],
                       font=FONTS['body'])
        
        # Form controls
        style.configure("TEntry",
                       fieldbackground=COLORS['bg_secondary'],
                       foreground=COLORS['text_primary'],
                       borderwidth=1,
                       bordercolor=COLORS['border'],
                       insertcolor=COLORS['accent'],
                       padding=6)
        
        style.configure("TCombobox",
                       fieldbackground=COLORS['bg_secondary'],
                       background=COLORS['bg_secondary'],
                       foreground=COLORS['text_primary'],
                       arrowcolor=COLORS['accent'],
                       padding=6)
        
        # Notebook (Tabs)
        style.configure("TNotebook",
                       background=COLORS['bg_primary'],
                       borderwidth=0,
                       tabmargins=(0, 0, 0, 0))
        style.configure("TNotebook.Tab",
                       background=COLORS['bg_secondary'],
                       foreground=COLORS['text_secondary'],
                       padding=[24, 12],
                       font=FONTS['body'])
        style.map("TNotebook.Tab",
                 background=[("selected", COLORS['accent'])],
                 foreground=[("selected", COLORS['text_primary'])])
        
        # Treeview (Data grid)
        style.configure("Treeview",
                       background=COLORS['bg_card'],
                       foreground=COLORS['text_primary'],
                       fieldbackground=COLORS['bg_card'],
                       borderwidth=0,
                       rowheight=28,
                       font=FONTS['body'])
        style.configure("Treeview.Heading",
                       background=COLORS['bg_secondary'],
                       foreground=COLORS['text_primary'],
                       borderwidth=0,
                       font=FONTS['header'])
        style.map('Treeview', 
                 background=[('selected', COLORS['row_hover'])],
                 foreground=[('selected', COLORS['text_primary'])])
        
        # Progress bar (for future use)
        style.configure("TProgressbar",
                       thickness=4,
                       background=COLORS['accent'],
                       troughcolor=COLORS['bg_secondary'])
    
    def create_header(self):
        """Professional header with balanced spacing"""
        header = tk.Frame(self.root, bg=COLORS['bg_primary'], height=80)
        header.pack(fill=tk.X, padx=30, pady=(25, 15))
        header.pack_propagate(False)
        
        # Title block
        title_frame = tk.Frame(header, bg=COLORS['bg_primary'])
        title_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        title_label = ttk.Label(title_frame, text="DataSphere Pro", style="Title.TLabel")
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(title_frame, text="Enterprise Database Management", 
                                   style="Subtitle.TLabel")
        subtitle_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Action buttons
        action_frame = tk.Frame(header, bg=COLORS['bg_primary'])
        action_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        new_table_btn = ttk.Button(action_frame, text="+ New Table",
                                   style="Primary.TButton",
                                   command=self.show_create_table_dialog)
        new_table_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        refresh_btn = ttk.Button(action_frame, text="⟳ Refresh",
                                style="Secondary.TButton",
                                command=self.refresh_tables)
        refresh_btn.pack(side=tk.LEFT)
    
    def create_main_layout(self):
        """Main layout with proper proportions"""
        main_container = tk.Frame(self.root, bg=COLORS['bg_primary'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 25))
        
        # Sidebar (25% width)
        self.create_sidebar(main_container)
        
        # Content area (75% width)
        self.create_content_area(main_container)
    
    def create_sidebar(self, parent):
        """Enhanced sidebar with better spacing"""
        sidebar = ttk.Frame(parent, style="Sidebar.TFrame", width=350)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        # Tables header with count
        header_frame = tk.Frame(sidebar, bg=COLORS['bg_secondary'])
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 15))
        
        ttk.Label(header_frame, text="Tables", style="Header.TLabel").pack(side=tk.LEFT)
        self.table_count_label = ttk.Label(header_frame, text="(0)", style="Normal.TLabel")
        self.table_count_label.pack(side=tk.LEFT, padx=(8, 0))
        
        # Tables listbox
        self.tables_listbox = tk.Listbox(sidebar,
                                         bg=COLORS['bg_card'],
                                         fg=COLORS['text_primary'],
                                         selectbackground=COLORS['accent'],
                                         selectforeground=COLORS['text_primary'],
                                         font=FONTS['body'],
                                         borderwidth=0,
                                         highlightthickness=0,
                                         activestyle='none',
                                         relief=tk.FLAT)
        self.tables_listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        self.tables_listbox.bind('<<ListboxSelect>>', self.on_table_select)
        
        # Action buttons
        actions_frame = tk.Frame(sidebar, bg=COLORS['bg_secondary'])
        actions_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Use grid for equal button heights
        actions_frame.columnconfigure(0, weight=1)
        actions_frame.columnconfigure(1, weight=1)
        
        export_btn = ttk.Button(actions_frame, text="⬇ Export CSV",
                               style="Secondary.TButton",
                               command=self.export_selected_table)
        export_btn.grid(row=0, column=0, sticky=tk.EW, padx=(0, 5), pady=5)
        
        join_btn = ttk.Button(actions_frame, text="⋈ Join Tables",
                             style="Secondary.TButton",
                             command=self.show_join_dialog)
        join_btn.grid(row=0, column=1, sticky=tk.EW, padx=(5, 0), pady=5)
    
    def create_content_area(self, parent):
        """Content area with modern card design"""
        content_frame = ttk.Frame(parent, style="Card.TFrame")
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0))
        
        # Notebook with tabs
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        # Schema Tab
        self.schema_tab = self.create_schema_tab()
        self.notebook.add(self.schema_tab, text="📋 Schema")
        
        # Query Tab
        self.query_tab = self.create_query_tab()
        self.notebook.add(self.query_tab, text="🔎 Query")
        
        # Data Tab
        self.data_tab = self.create_data_tab()
        self.notebook.add(self.data_tab, text="📊 Data")
    
    def create_schema_tab(self):
        """Schema tab with better scroll handling"""
        tab = tk.Frame(self.notebook, bg=COLORS['bg_card'])
        
        # Header
        ttk.Label(tab, text="Table Structure Visualization", style="Header.TLabel").pack(fill=tk.X, padx=25, pady=(25, 15))
        
        # Improved scrollable canvas
        container = tk.Frame(tab, bg=COLORS['bg_card'])
        container.pack(fill=tk.BOTH, expand=True, padx=25, pady=10)
        
        scrollbar = ttk.Scrollbar(container, orient="vertical")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.schema_canvas = tk.Canvas(container,
                                       bg=COLORS['bg_card'],
                                       highlightthickness=0,
                                       relief=tk.FLAT)
        self.schema_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.schema_canvas.yview)
        self.schema_canvas.config(yscrollcommand=scrollbar.set)
        
        # Bind mousewheel
        self.schema_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        self.schema_frame = tk.Frame(self.schema_canvas, bg=COLORS['bg_card'])
        self.schema_canvas.create_window((0, 0), window=self.schema_frame, anchor=tk.NW, width=700)
        
        return tab
    
    def create_query_tab(self):
        """Query tab with improved mode toggle"""
        tab = tk.Frame(self.notebook, bg=COLORS['bg_card'])
        
        # Query mode selector (modern toggle)
        mode_frame = tk.Frame(tab, bg=COLORS['bg_card'])
        mode_frame.pack(fill=tk.X, padx=25, pady=(25, 15))
        
        self.query_mode = tk.StringVar(value="standard")
        
        # Custom styled radio buttons
        modes = [
            ("standard", "Standard SQL", "🔍"),
            ("nlp", "Natural Language", "✨")
        ]
        
        for idx, (value, text, icon) in enumerate(modes):
            btn = ttk.Radiobutton(mode_frame,
                                 text=f"{icon} {text}",
                                 variable=self.query_mode,
                                 value=value,
                                 command=self.toggle_query_mode,
                                 style="TRadiobutton")
            btn.pack(side=tk.LEFT, padx=(0 if idx == 0 else 25))
        
        # Standard Query Frame
        self.standard_query_frame = tk.Frame(tab, bg=COLORS['bg_card'])
        
        # Clean grid layout
        query_grid = tk.Frame(self.standard_query_frame, bg=COLORS['bg_card'])
        query_grid.pack(fill=tk.X, pady=20)
        
        # Configure grid columns
        for i in range(4):
            query_grid.columnconfigure(i, weight=1)
        
        # Table
        ttk.Label(query_grid, text="Table", style="Normal.TLabel").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=10)
        self.query_table = ttk.Combobox(query_grid, state="readonly", width=25)
        self.query_table.grid(row=0, column=1, sticky=tk.EW, padx=(0, 20), pady=10)
        
        # Column
        ttk.Label(query_grid, text="Column", style="Normal.TLabel").grid(row=0, column=2, sticky=tk.W, padx=(0, 10), pady=10)
        self.query_column = ttk.Entry(query_grid, width=25)
        self.query_column.grid(row=0, column=3, sticky=tk.EW, pady=10)
        
        # Operator
        ttk.Label(query_grid, text="Operator", style="Normal.TLabel").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=10)
        self.query_operator = ttk.Combobox(query_grid, state="readonly", values=["=", ">", "<", ">=", "<=", "!="], width=25)
        self.query_operator.current(0)
        self.query_operator.grid(row=1, column=1, sticky=tk.EW, padx=(0, 20), pady=10)
        
        # Value
        ttk.Label(query_grid, text="Value", style="Normal.TLabel").grid(row=1, column=2, sticky=tk.W, padx=(0, 10), pady=10)
        self.query_value = ttk.Entry(query_grid, width=25)
        self.query_value.grid(row=1, column=3, sticky=tk.EW, pady=10)
        
        # Execute button
        btn_container = tk.Frame(self.standard_query_frame, bg=COLORS['bg_card'])
        btn_container.pack(fill=tk.X, pady=20)
        
        execute_btn = ttk.Button(btn_container, text="▶ Execute Query",
                                style="Primary.TButton",
                                command=self.execute_standard_query)
        execute_btn.pack()
        
        # NLP Query Frame
        self.nlp_query_frame = tk.Frame(tab, bg=COLORS['bg_card'])
        
        nlp_container = tk.Frame(self.nlp_query_frame, bg=COLORS['bg_card'])
        nlp_container.pack(fill=tk.X, pady=20)
        
        ttk.Label(nlp_container, text="Describe your query in plain English:", 
                 style="Normal.TLabel").pack(anchor=tk.W, pady=(0, 10))
        
        self.nlp_text = scrolledtext.ScrolledText(nlp_container,
                                                  height=4,
                                                  bg=COLORS['bg_secondary'],
                                                  fg=COLORS['text_primary'],
                                                  font=FONTS['body'],
                                                  insertbackground=COLORS['accent'],
                                                  relief=tk.FLAT,
                                                  padx=10,
                                                  pady=10)
        self.nlp_text.pack(fill=tk.X, pady=(0, 20))
        self.nlp_text.insert("1.0", "Example: Find employees in department 1 with salary > 50000")
        self.nlp_text.bind("<FocusIn>", lambda e: self._clear_placeholder())
        
        nlp_btn = ttk.Button(nlp_container, text="✨ Execute Natural Query",
                            style="Primary.TButton",
                            command=self.execute_nlp_query)
        nlp_btn.pack()
        
        # Results area
        results_container = tk.Frame(tab, bg=COLORS['bg_card'])
        results_container.pack(fill=tk.BOTH, expand=True, padx=25, pady=(20, 25))
        
        ttk.Label(results_container, text="Query Results", style="Header.TLabel").pack(anchor=tk.W, pady=(0, 10))
        
        self.query_results_tree = self.create_treeview(results_container)
        
        return tab
    
    def create_data_tab(self):
        """Data tab with improved spacing"""
        tab = tk.Frame(self.notebook, bg=COLORS['bg_card'])
        
        header_frame = tk.Frame(tab, bg=COLORS['bg_card'])
        header_frame.pack(fill=tk.X, padx=25, pady=(25, 15))
        
        ttk.Label(header_frame, text="Table Data Viewer", style="Header.TLabel").pack(side=tk.LEFT)
        
        data_container = tk.Frame(tab, bg=COLORS['bg_card'])
        data_container.pack(fill=tk.BOTH, expand=True, padx=25, pady=(0, 25))
        
        self.data_tree = self.create_treeview(data_container)
        
        return tab
    
    def create_treeview(self, parent):
        """Modern treeview with proper scrollbars"""
        container = tk.Frame(parent, bg=COLORS['bg_card'])
        container.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        vsb = ttk.Scrollbar(container, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        hsb = ttk.Scrollbar(container, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        tree = ttk.Treeview(container,
                           yscrollcommand=vsb.set,
                           xscrollcommand=hsb.set,
                           selectmode="browse")
        tree.pack(fill=tk.BOTH, expand=True)
        
        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)
        
        return tree
    
    # ========== UTILITY METHODS ==========
    def _on_mousewheel(self, event):
        """Smooth mousewheel scrolling"""
        self.schema_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def _clear_placeholder(self):
        """Clear NLP placeholder text"""
        if "Example:" in self.nlp_text.get("1.0", tk.END):
            self.nlp_text.delete("1.0", tk.END)
            self.nlp_text.config(fg=COLORS['text_primary'])
    
    # ========== EXISTING LOGIC (UNCHANGED) ==========
    def toggle_query_mode(self):
        if self.query_mode.get() == "standard":
            self.nlp_query_frame.pack_forget()
            self.standard_query_frame.pack(fill=tk.X, padx=25, pady=(0, 20))
        else:
            self.standard_query_frame.pack_forget()
            self.nlp_query_frame.pack(fill=tk.X, padx=25, pady=(0, 20))
    
    def refresh_tables(self):
        try:
            response = requests.get(f"{API_BASE}/tables", timeout=5)
            if response.status_code == 200:
                self.tables = response.json()
                self.tables_listbox.delete(0, tk.END)
                for table in self.tables:
                    self.tables_listbox.insert(tk.END, f"  {table}")
                
                self.query_table['values'] = self.tables
                if self.tables:
                    self.query_table.current(0)
                
                # Update count
                self.table_count_label.config(text=f"({len(self.tables)})")
            else:
                messagebox.showerror("Error", "Failed to fetch tables")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot connect to server:\n{str(e)}")
    
    def on_table_select(self, event):
        selection = self.tables_listbox.curselection()
        if selection:
            table_name = self.tables_listbox.get(selection[0]).strip()
            self.selected_table = table_name
            self.load_table_data(table_name)
            self.display_schema(table_name)
    
    def load_table_data(self, table_name):
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
        for widget in self.schema_frame.winfo_children():
            widget.destroy()
        
        if not self.table_data or len(self.table_data) == 0:
            return
        
        # Table name
        tk.Label(self.schema_frame,
                text=f"📊 {table_name}",
                bg=COLORS['bg_card'],
                fg=COLORS['text_primary'],
                font=("Segoe UI", 18, "bold"),
                anchor=tk.W).pack(fill=tk.X, padx=20, pady=(20, 25))
        
        # Columns
        columns = self.table_data[0]
        for idx, col in enumerate(columns):
            is_pk = 'id' in col.lower() and idx == 0
            is_fk = 'deptid' in col.lower() or 'dept_id' in col.lower()
            
            # Column card
            col_frame = tk.Frame(self.schema_frame, 
                               bg=COLORS['bg_secondary'], 
                               relief=tk.FLAT,
                               highlightthickness=1,
                               highlightbackground=COLORS['border'])
            col_frame.pack(fill=tk.X, padx=20, pady=6)
            
            # Icon and name
            icon = "🔑" if is_pk else ("🔗" if is_fk else "🗄️")
            col_label = tk.Label(col_frame,
                               text=f"  {icon}  {col}",
                               bg=COLORS['bg_secondary'],
                               fg=COLORS['text_primary'],
                               font=FONTS['header'],
                               anchor=tk.W)
            col_label.pack(side=tk.LEFT, padx=15, pady=12)
            
            # Badge
            if is_pk:
                badge_text = "PRIMARY KEY"
                badge_bg = COLORS['warning']
            elif is_fk:
                badge_text = "FOREIGN KEY"
                badge_bg = COLORS['accent']
            else:
                badge_text = None
            
            if badge_text:
                badge = tk.Label(col_frame,
                               text=badge_text,
                               bg=badge_bg,
                               fg=COLORS['bg_primary'],
                               font=("Segoe UI", 9, "bold"),
                               padx=10,
                               pady=4,
                               relief=tk.FLAT)
                badge.pack(side=tk.RIGHT, padx=15)
        
        self.schema_frame.update_idletasks()
        self.schema_canvas.config(scrollregion=self.schema_canvas.bbox("all"))
    
    def display_table_data(self, tree, data):
        tree.delete(*tree.get_children())
        
        if not data or len(data) == 0:
            return
        
        columns = data[0]
        tree['columns'] = columns
        tree['show'] = 'headings'
        
        for col in columns:
            tree.heading(col, text=col.upper(), anchor=tk.W)
            tree.column(col, width=140, anchor=tk.W, minwidth=100)
        
        for row in data[1:]:
            tree.insert('', tk.END, values=row)
    
    def execute_standard_query(self):
        table = self.query_table.get()
        column = self.query_column.get()
        operator = self.query_operator.get()
        value = self.query_value.get()
        
        if not all([table, column, value]):
            messagebox.showwarning("Missing Parameters", "Please complete all query fields")
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
                self.notebook.select(1)
                messagebox.showinfo("Query Success", f"Returned {len(result)-1 if result else 0} rows")
            else:
                messagebox.showerror("Query Failed", "Invalid query parameters")
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
    
    def execute_nlp_query(self):
        query_text = self.nlp_text.get("1.0", tk.END).strip().lower()
        
        params = {"table": "", "column": "", "operator": "=", "value": ""}
        
        # Table detection
        for table in self.tables:
            if table.lower() in query_text:
                params["table"] = table
                break
        
        # Operator detection
        if "greater than" in query_text or ">" in query_text:
            params["operator"] = ">"
        elif "less than" in query_text or "<" in query_text:
            params["operator"] = "<"
        elif "not" in query_text and ("equal" in query_text or "!=" in query_text):
            params["operator"] = "!="
        
        # Value detection
        import re
        numbers = re.findall(r'\d+', query_text)
        if numbers:
            params["value"] = numbers[0]
        
        # Column detection
        columns = ['empid', 'deptid', 'name', 'salary', 'department']
        for col in columns:
            if col in query_text.replace(" ", ""):
                params["column"] = col
                break
        
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
                                 "Could not understand query. Try:\n'Show employees with salary greater than 50000'")
    
    def export_selected_table(self):
        if not self.selected_table:
            messagebox.showwarning("No Selection", "Please select a table to export")
            return
        
        try:
            response = requests.post(f"{API_BASE}/table/{self.selected_table}/export",
                                    json={},
                                    timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                filename = result.get('file', f"{self.selected_table}.csv")
                messagebox.showinfo("Export Complete", f"Table saved to: {filename}")
            else:
                messagebox.showerror("Export Failed", "Could not export table")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def show_join_dialog(self):
        if len(self.tables) < 2:
            messagebox.showwarning("Insufficient Tables", "At least 2 tables required for join")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Table Join Wizard")
        dialog.geometry("500x300")
        dialog.configure(bg=COLORS['bg_primary'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Form
        form_frame = tk.Frame(dialog, bg=COLORS['bg_primary'])
        form_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        ttk.Label(form_frame, text="Select tables to join:", style="Header.TLabel").pack(pady=(0, 20))
        
        # Left table
        ttk.Label(form_frame, text="Left Table", style="Normal.TLabel").pack(anchor=tk.W)
        left_combo = ttk.Combobox(form_frame, values=self.tables, state="readonly", width=40)
        left_combo.current(0)
        left_combo.pack(fill=tk.X, pady=(5, 15))
        
        # Right table
        ttk.Label(form_frame, text="Right Table", style="Normal.TLabel").pack(anchor=tk.W)
        right_combo = ttk.Combobox(form_frame, values=self.tables, state="readonly", width=40)
        if len(self.tables) > 1:
            right_combo.current(1)
        right_combo.pack(fill=tk.X, pady=(5, 20))
        
        # Execute
        execute_btn = ttk.Button(form_frame, text="Execute INNER JOIN", 
                                style="Primary.TButton",
                                command=lambda: self._execute_join(dialog, left_combo.get(), right_combo.get()))
        execute_btn.pack()
    
    def _execute_join(self, dialog, left, right):
        try:
            response = requests.post(f"{API_BASE}/join",
                                    json={"left_table": left, "right_table": right},
                                    timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                self.display_table_data(self.query_results_tree, result)
                self.notebook.select(1)
                messagebox.showinfo("Join Success", f"Returned {len(result)-1 if result else 0} rows")
                dialog.destroy()
            else:
                messagebox.showerror("Join Failed", "Could not join tables")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def show_create_table_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Create New Table")
        dialog.geometry("600x700")
        dialog.configure(bg=COLORS['bg_primary'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Scrollable form
        canvas = tk.Canvas(dialog, bg=COLORS['bg_primary'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        form_frame = tk.Frame(canvas, bg=COLORS['bg_primary'])
        
        form_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=form_frame, anchor="nw", width=560)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=30, pady=30)
        scrollbar.pack(side="right", fill="y")
        
        # Form
        ttk.Label(form_frame, text="Create New Table", style="Title.TLabel").pack(pady=(0, 25))
        
        ttk.Label(form_frame, text="Table Name", style="Header.TLabel").pack(anchor=tk.W)
        name_entry = ttk.Entry(form_frame, width=50)
        name_entry.pack(fill=tk.X, pady=(5, 20))
        
        ttk.Label(form_frame, text="Columns (one per line)", style="Header.TLabel").pack(anchor=tk.W)
        columns_text = scrolledtext.ScrolledText(form_frame, height=10, width=50,
                                               bg=COLORS['bg_secondary'],
                                               fg=COLORS['text_primary'],
                                               font=FONTS['monospace'],
                                               insertbackground=COLORS['accent'],
                                               relief=tk.FLAT,
                                               padx=8,
                                               pady=8)
        columns_text.pack(fill=tk.X, pady=(5, 20))
        
        ttk.Label(form_frame, text="Primary Key Column", style="Header.TLabel").pack(anchor=tk.W)
        pk_entry = ttk.Entry(form_frame, width=50)
        pk_entry.pack(fill=tk.X, pady=(5, 20))
        
        ttk.Label(form_frame, text="Foreign Key Column (optional)", style="Header.TLabel").pack(anchor=tk.W)
        fk_entry = ttk.Entry(form_frame, width=50)
        fk_entry.pack(fill=tk.X, pady=(5, 30))
        
        # Buttons
        btn_frame = tk.Frame(form_frame, bg=COLORS['bg_primary'])
        btn_frame.pack(pady=(0, 20))
        
        create_btn = ttk.Button(btn_frame, text="Create Table", 
                               style="Primary.TButton",
                               command=lambda: self._create_table(dialog, name_entry, columns_text, pk_entry, fk_entry))
        create_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(btn_frame, text="Cancel", 
                               style="Secondary.TButton",
                               command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
    def _create_table(self, dialog, name_entry, columns_text, pk_entry, fk_entry):
        name = name_entry.get().strip()
        columns = [c.strip() for c in columns_text.get("1.0", tk.END).strip().split('\n') if c.strip()]
        pk = pk_entry.get().strip()
        fk = fk_entry.get().strip()
        
        if not name or not columns:
            messagebox.showwarning("Incomplete", "Table name and at least one column required")
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
                messagebox.showinfo("Success", f"Table '{name}' created")
                self.refresh_tables()
                dialog.destroy()
            else:
                messagebox.showerror("Creation Failed", "Could not create table")
        except Exception as e:
            messagebox.showerror("Error", str(e))


def main():
    root = tk.Tk()
    app = ModernDatabaseGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()