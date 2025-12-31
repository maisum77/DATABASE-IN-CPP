"""
MiniDB GUI - Professional Database Manager
A Python GUI client for the MiniDB C++ database backend
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import requests
import json
from datetime import datetime
import threading


class MiniDBGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MiniDB - Professional Database Manager")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 700)
        
        # Backend configuration
        self.backend_url = "http://localhost:8080"
        
        # Enhanced color scheme - modern professional palette
        self.colors = {
            'bg': '#1a1a2e',           # Dark navy background
            'sidebar': '#16213e',       # Slightly lighter sidebar
            'sidebar_hover': '#1f4068', # Hover state
            'accent': '#e94560',        # Coral accent
            'accent_hover': '#d63850',  # Darker accent
            'success': '#0f3460',       # Success green
            'success_light': '#4ecca3', # Light green
            'danger': '#e94560',        # Danger red
            'warning': '#f39c12',       # Warning orange
            'info': '#3498db',          # Info blue
            'text_dark': '#eaeaea',     # Light text
            'text_light': '#a0a0a0',    # Muted text
            'text_muted': '#6c6c6c',    # Very muted
            'card': '#16213e',          # Card background
            'card_hover': '#1f4068',    # Card hover
            'border': '#2a2a4a',        # Subtle borders
            'input_bg': '#0f3460',      # Input background
            'tree_bg': '#16213e',       # Treeview background
            'tree_alt': '#1a1a2e',      # Alternating row
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # Database connection status
        self.db_connected = False
        self.current_table = None
        self.tables = []
        self.current_table_data = None
        
        # UI state
        self.query_history = []
        self.history_index = -1
        
        # Setup styles
        self.setup_styles()
        
        # Build UI
        self.setup_ui()
        
        # Auto-connect option
        self.root.after(500, self.auto_connect)
    
    def setup_styles(self):
        """Configure custom ttk styles for better appearance"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure Treeview colors
        style.configure(
            "Treeview",
            background=self.colors['tree_bg'],
            foreground=self.colors['text_dark'],
            fieldbackground=self.colors['tree_bg'],
            font=('Consolas', 10),
            rowheight=28
        )
        style.configure(
            "Treeview.Heading",
            background=self.colors['input_bg'],
            foreground=self.colors['text_dark'],
            font=('Consolas', 10, 'bold'),
            relief='flat'
        )
        style.map(
            "Treeview",
            background=[('selected', self.colors['accent'])],
            foreground=[('selected', 'white')]
        )
        
        # Configure Combobox
        style.configure(
            "TCombobox",
            background=self.colors['input_bg'],
            fieldbackground=self.colors['input_bg'],
            foreground=self.colors['text_dark']
        )
        
        # Configure Scrollbar
        style.configure(
            "Vertical.TScrollbar",
            background=self.colors['sidebar'],
            troughcolor=self.colors['bg'],
            arrowcolor=self.colors['text_dark']
        )
        style.configure(
            "Horizontal.TScrollbar",
            background=self.colors['sidebar'],
            troughcolor=self.colors['bg'],
            arrowcolor=self.colors['text_dark']
        )
        
    def setup_ui(self):
        # Create main container
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar
        self.create_sidebar(main_container)
        
        # Main content area with tabs
        self.create_main_content(main_container)
        
        # Status bar at bottom
        self.create_status_bar()
    
    def create_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg=self.colors['sidebar'], width=260)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        # Logo/Title area with gradient effect (simulated)
        title_frame = tk.Frame(sidebar, bg=self.colors['sidebar'])
        title_frame.pack(pady=25, padx=15)
        
        # Logo icon
        logo_label = tk.Label(
            title_frame,
            text="🗄️",
            font=('Helvetica', 36),
            bg=self.colors['sidebar'],
            fg=self.colors['success_light']
        )
        logo_label.pack()
        
        title = tk.Label(
            title_frame,
            text="MiniDB",
            font=('Helvetica', 22, 'bold'),
            bg=self.colors['sidebar'],
            fg=self.colors['text_dark']
        )
        title.pack(pady=(5, 0))
        
        subtitle = tk.Label(
            title_frame,
            text="Database Manager",
            font=('Helvetica', 9),
            bg=self.colors['sidebar'],
            fg=self.colors['text_light']
        )
        subtitle.pack()
        
        # Connection status with animated indicator
        self.status_frame = tk.Frame(sidebar, bg=self.colors['sidebar'])
        self.status_frame.pack(pady=15, padx=15, fill=tk.X)
        
        # Status indicator
        self.status_indicator = tk.Label(
            self.status_frame,
            text="●",
            font=('Helvetica', 14),
            bg=self.colors['sidebar'],
            fg=self.colors['danger']
        )
        self.status_indicator.pack(pady=(0, 5))
        
        self.status_label = tk.Label(
            self.status_frame,
            text="Disconnected",
            font=('Helvetica', 10),
            bg=self.colors['sidebar'],
            fg=self.colors['text_light']
        )
        self.status_label.pack()
        
        # Separator with glow effect
        separator = tk.Frame(sidebar, bg=self.colors['border'], height=2)
        separator.pack(fill=tk.X, padx=15, pady=15)
        
        # Navigation section header
        nav_header = tk.Label(
            sidebar,
            text="NAVIGATION",
            font=('Helvetica', 8, 'bold'),
            bg=self.colors['sidebar'],
            fg=self.colors['text_muted'],
            padx=20
        )
        nav_header.pack(anchor='w', pady=(0, 5))
        
        # Navigation buttons with icons
        nav_buttons = [
            ("🏠", "Home", self.show_welcome),
            ("🔌", "Connect", self.show_connection_test),
            ("📊", "Tables", self.show_tables),
            ("🔍", "SQL Query", self.show_query),
            ("🤖", "NLP Query", self.show_nlp),
            ("➕", "Create Table", self.show_create_table),
            ("📥", "Import CSV", self.show_import_csv),
            ("📤", "Export CSV", self.show_export_csv),
            ("🔗", "Join Tables", self.show_join),
            ("⚙️", "Settings", self.show_settings),
            ("ℹ️", "About", self.show_about)
        ]
        
        for icon, text, command in nav_buttons:
            self.create_nav_button(sidebar, icon, text, command)
        
        # Bottom section with stats
        bottom_frame = tk.Frame(sidebar, bg=self.colors['sidebar'])
        bottom_frame.pack(side=tk.BOTTOM, pady=15, padx=15, fill=tk.X)
        
        # Quick stats
        self.table_count_label = tk.Label(
            bottom_frame,
            text="📋 0 Tables",
            font=('Helvetica', 10),
            bg=self.colors['sidebar'],
            fg=self.colors['text_light'],
            anchor='w'
        )
        self.table_count_label.pack(fill=tk.X, pady=2)
        
        version_label = tk.Label(
            bottom_frame,
            text="Version 1.0.0",
            font=('Helvetica', 8),
            bg=self.colors['sidebar'],
            fg=self.colors['text_muted']
        )
        version_label.pack(pady=(10, 0))
        
    def create_nav_button(self, parent, icon, text, command):
        """Create a navigation button with icon and text"""
        btn = tk.Frame(
            parent,
            bg=self.colors['sidebar'],
            cursor='hand2'
        )
        btn.pack(fill=tk.X, padx=10, pady=3)
        
        # Icon label
        icon_label = tk.Label(
            btn,
            text=icon,
            font=('Helvetica', 12),
            bg=self.colors['sidebar'],
            fg=self.colors['text_light'],
            width=3,
            anchor='e'
        )
        icon_label.pack(side=tk.LEFT)
        
        # Text label
        text_label = tk.Label(
            btn,
            text=text,
            font=('Helvetica', 11),
            bg=self.colors['sidebar'],
            fg=self.colors['text_light'],
            anchor='w'
        )
        text_label.pack(side=tk.LEFT, fill=tk.X, padx=5)
        
        # Make clickable
        for widget in [btn, icon_label, text_label]:
            widget.bind('<Button-1>', lambda e: command())
            widget.bind('<Enter>', self._on_nav_enter)
            widget.bind('<Leave>', self._on_nav_leave)
    
    def _on_nav_enter(self, event):
        """Handle hover enter for nav buttons"""
        event.widget.configure(bg=self.colors['sidebar_hover']) if hasattr(event.widget, 'configure') else None
        
    def _on_nav_leave(self, event):
        """Handle hover leave for nav buttons"""
        event.widget.configure(bg=self.colors['sidebar']) if hasattr(event.widget, 'configure') else None
        
    def create_main_content(self, parent):
        # Main content frame with header
        content_frame = tk.Frame(parent, bg=self.colors['bg'])
        content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Header with better styling
        header = tk.Frame(content_frame, bg=self.colors['card'], height=70)
        header.pack(fill=tk.X, padx=20, pady=(15, 10))
        header.pack_propagate(False)
        
        # Left side - Page title with breadcrumb
        title_frame = tk.Frame(header, bg=self.colors['card'])
        title_frame.pack(side=tk.LEFT, padx=20, fill=tk.BOTH, expand=True)
        
        self.page_title = tk.Label(
            title_frame,
            text="Welcome to MiniDB",
            font=('Helvetica', 20, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text_dark']
        )
        self.page_title.pack(side=tk.LEFT, pady=15)
        
        # Subtitle / breadcrumb
        self.breadcrumb = tk.Label(
            title_frame,
            text="",
            font=('Helvetica', 10),
            bg=self.colors['card'],
            fg=self.colors['text_muted']
        )
        self.breadcrumb.pack(side=tk.LEFT, padx=15, pady=15)
        
        # Right side - Action buttons
        button_frame = tk.Frame(header, bg=self.colors['card'])
        button_frame.pack(side=tk.RIGHT, padx=20)
        
        # Connect button
        self.connect_btn = self.create_header_button(
            button_frame,
            "⚡ Connect",
            self.connect_database,
            self.colors['accent']
        )
        self.connect_btn.pack(side=tk.RIGHT, padx=5)
        
        # Refresh button
        self.refresh_btn = self.create_header_button(
            button_frame,
            "🔄 Refresh",
            self.refresh_current_view,
            self.colors['input_bg']
        )
        self.refresh_btn.pack(side=tk.RIGHT, padx=5)
        
        # Content area (will change based on navigation)
        self.content_area = tk.Frame(content_frame, bg=self.colors['bg'])
        self.content_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))
        
        # Show welcome screen by default
        self.show_welcome()
    
    def create_header_button(self, parent, text, command, bg_color):
        """Create a styled header button"""
        btn = tk.Button(
            parent,
            text=text,
            font=('Helvetica', 10, 'bold'),
            bg=bg_color,
            fg='white',
            activebackground=self.colors['accent_hover'],
            activeforeground='white',
            cursor='hand2',
            bd=0,
            padx=15,
            pady=8,
            command=command,
            relief='flat'
        )
        return btn
    
    def create_status_bar(self):
        """Create enhanced status bar with more information"""
        status_bar = tk.Frame(self.root, bg=self.colors['sidebar'], height=35)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Left section - Status message
        status_frame = tk.Frame(status_bar, bg=self.colors['sidebar'])
        status_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.status_text = tk.Label(
            status_frame,
            text="Ready - Click 'Connect' to start",
            font=('Helvetica', 9),
            bg=self.colors['sidebar'],
            fg=self.colors['text_light'],
            anchor='w'
        )
        self.status_text.pack(side=tk.LEFT, padx=15, pady=8)
        
        # Right section - Info
        info_frame = tk.Frame(status_bar, bg=self.colors['sidebar'])
        info_frame.pack(side=tk.RIGHT)
        
        # Time
        self.time_label = tk.Label(
            info_frame,
            text=datetime.now().strftime("%H:%M:%S"),
            font=('Helvetica', 9),
            bg=self.colors['sidebar'],
            fg=self.colors['text_light']
        )
        self.time_label.pack(side=tk.RIGHT, padx=15, pady=8)
        
        # Separator
        sep1 = tk.Label(info_frame, text="|", bg=self.colors['sidebar'], fg=self.colors['text_muted'])
        sep1.pack(side=tk.RIGHT, pady=8)
        
        # Table count
        self.tables_status_label = tk.Label(
            info_frame,
            text="0 tables",
            font=('Helvetica', 9),
            bg=self.colors['sidebar'],
            fg=self.colors['text_light']
        )
        self.tables_status_label.pack(side=tk.RIGHT, padx=15, pady=8)
        
        # Separator
        sep2 = tk.Label(info_frame, text="|", bg=self.colors['sidebar'], fg=self.colors['text_muted'])
        sep2.pack(side=tk.RIGHT, pady=8)
        
        # Connection indicator
        self.conn_status_icon = tk.Label(
            info_frame,
            text="●",
            font=('Helvetica', 10),
            bg=self.colors['sidebar'],
            fg=self.colors['danger']
        )
        self.conn_status_icon.pack(side=tk.RIGHT, padx=(15, 5), pady=8)
        
        # Update time every second
        self.update_time()
    
    def update_time(self):
        """Update the time display"""
        self.time_label.config(text=datetime.now().strftime("%H:%M:%S"))
        self.root.after(1000, self.update_time)
    
    def clear_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()
            
    def update_status(self, message, color=None):
        """Update status bar message"""
        self.status_text.config(text=message)
        if color:
            self.status_text.config(fg=color)
    
    def update_connection_status(self, connected):
        """Update connection status indicators"""
        if connected:
            self.status_indicator.config(text="● Connected", fg=self.colors['success_light'])
            self.status_label.config(text="Connected")
            self.conn_status_icon.config(fg=self.colors['success_light'], text="✓")
            self.connect_btn.config(text="✓ Connected", state=tk.DISABLED, bg=self.colors['success_light'])
        else:
            self.status_indicator.config(text="● Disconnected", fg=self.colors['danger'])
            self.status_label.config(text="Disconnected")
            self.conn_status_icon.config(fg=self.colors['danger'], text="●")
            self.connect_btn.config(text="⚡ Connect", state=tk.NORMAL, bg=self.colors['accent'])
    
    def refresh_current_view(self):
        """Refresh the current view based on page title"""
        title = self.page_title.cget("text")
        
        if "Welcome" in title or "MiniDB" in title:
            self.show_welcome()
        elif "Tables" in title and "Table:" not in title:
            self.show_tables()
        elif "Table:" in title and self.current_table:
            self.view_table(self.current_table)
        elif "SQL Query" in title:
            self.show_query()
        elif "NLP Query" in title:
            self.show_nlp()
        elif "Create" in title:
            self.show_create_table()
        elif "Inner Join" in title:
            self.show_join()
        elif "Import" in title:
            self.show_import_csv()
        elif "Export" in title:
            self.show_export_csv()
        elif "Settings" in title:
            self.show_settings()
        elif "About" in title:
            self.show_about()
        elif "Connection" in title:
            self.show_connection_test()
    
    def auto_connect(self):
        """Try to connect automatically on startup"""
        # Don't auto-connect, just show ready state
        self.update_status("Ready - Click 'Connect' to start")
    
    # API Communication Methods
    def api_request(self, endpoint, method='GET', data=None, files=None, timeout=10):
        """Make API request to backend"""
        try:
            url = f"{self.backend_url}{endpoint}"
            
            print(f"\n{'='*60}")
            print(f"API Request: {method} {url}")
            if data:
                print(f"Data: {json.dumps(data, indent=2)}")
            print(f"{'='*60}\n")
            
            if method == 'GET':
                response = requests.get(url, timeout=timeout)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, timeout=30)
                else:
                    response = requests.post(url, json=data, timeout=timeout)
            elif method == 'PUT':
                response = requests.put(url, json=data, timeout=timeout)
            elif method == 'DELETE':
                response = requests.delete(url, timeout=timeout)
            
            print(f"Response Status: {response.status_code}")
            print(f"Response Content: {response.text[:1000]}")
            
            return response
            
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Connection Error: {str(e)}")
            messagebox.showerror("Connection Error", 
                               f"Cannot connect to backend server at {self.backend_url}\n\nError: {str(e)}\n\nPlease ensure:\n1. Your server is running (python server.py)\n2. Server is listening on port 8080\n3. No firewall blocking the connection")
            return None
        except requests.exceptions.Timeout:
            print(f"❌ Timeout Error")
            messagebox.showerror("Timeout Error", "Request timed out. Server may be busy or not responding.")
            return None
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            return None
    
    def connect_database(self):
        """Test connection to backend"""
        self.update_status("Connecting to backend...", self.colors['warning'])
        
        # Try multiple common endpoints
        endpoints_to_try = [
            '/api/health',
            '/health',
            '/api/status',
            '/status',
            '/',
            '/api/tables'
        ]
        
        connected = False
        working_endpoint = None
        
        for endpoint in endpoints_to_try:
            print(f"Trying endpoint: {self.backend_url}{endpoint}")
            response = self.api_request(endpoint, timeout=3)
            
            if response and response.status_code in [200, 404]:  # 404 means server is responding
                connected = True
                working_endpoint = endpoint
                print(f"✓ Server responded at: {endpoint}")
                break
        
        if connected:
            self.db_connected = True
            self.update_connection_status(True)
            self.update_status(f"Connected to MiniDB at {self.backend_url}", self.colors['success_light'])
            
            # Load tables from backend
            self.load_tables()
            
            messagebox.showinfo("Success", 
                              f"Successfully connected to MiniDB backend!\n\nServer is running at: {self.backend_url}\nResponding endpoint: {working_endpoint}")
        else:
            self.update_status("Failed to connect to backend", self.colors['danger'])
            
            # More detailed error message
            error_details = f"""Could not connect to backend at {self.backend_url}

Troubleshooting steps:

1. Start the server first:
   • Run: python server.py
   • Server should show "MiniDB HTTP API Server"

2. Verify the server is on port 8080
   • Run: lsof -i :8080 (Mac/Linux)
   • Run: netstat -ano | findstr :8080 (Windows)

3. Test server directly:
   • Open browser: {self.backend_url}
   • Or run: curl {self.backend_url}/api/health

4. Check for firewall/antivirus blocking

5. Server might be on different port - check your server.py configuration

Tried endpoints: {', '.join(endpoints_to_try)}"""
            
            messagebox.showerror("Connection Failed", error_details)
    
    def load_tables(self):
        """Load list of tables from backend"""
        response = self.api_request('/api/tables')
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                self.tables = data.get('tables', [])
                self.update_status(f"Loaded {len(self.tables)} tables")
                self.table_count_label.config(text=f"📋 {len(self.tables)} Tables")
                self.tables_status_label.config(text=f"{len(self.tables)} tables")
            except json.JSONDecodeError as e:
                print(f"Error parsing tables response: {e}")
                self.tables = []
        else:
            # If /api/tables fails, try getting status
            response = self.api_request('/api/status')
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    self.tables = data.get('tables', [])
                    self.update_status(f"Loaded {len(self.tables)} tables")
                    self.table_count_label.config(text=f"📋 {len(self.tables)} Tables")
                    self.tables_status_label.config(text=f"{len(self.tables)} tables")
                except:
                    self.tables = []
    
    def show_welcome(self):
        self.clear_content()
        self.page_title.config(text="Welcome to MiniDB")
        self.breadcrumb.config(text="")
        
        # Main container with centered content
        main_frame = tk.Frame(self.content_area, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, pady=30)
        
        # Hero section
        hero_frame = tk.Frame(main_frame, bg=self.colors['card'])
        hero_frame.pack(fill=tk.X, pady=(0, 30))
        
        # Icon and title
        icon_label = tk.Label(
            hero_frame,
            text="🗄️",
            font=('Helvetica', 48),
            bg=self.colors['card'],
            fg=self.colors['success_light']
        )
        icon_label.pack(pady=(40, 10))
        
        welcome_text = tk.Label(
            hero_frame,
            text="Professional Database Management System",
            font=('Helvetica', 22, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text_dark']
        )
        welcome_text.pack(pady=(0, 10))
        
        desc = tk.Label(
            hero_frame,
            text="Powerful in-memory database with C++ backend\nFeaturing SQL Queries • CSV Import/Export • Table Joins • NLP Queries",
            font=('Helvetica', 12),
            bg=self.colors['card'],
            fg=self.colors['text_muted'],
            justify=tk.CENTER
        )
        desc.pack(pady=(0, 30))
        
        # Backend status card
        backend_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        backend_frame.pack(fill=tk.X, pady=20)
        
        # Two column layout
        left_col = tk.Frame(backend_frame, bg=self.colors['bg'])
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        right_col = tk.Frame(backend_frame, bg=self.colors['bg'])
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Connection card
        conn_card = self.create_info_card(
            left_col,
            "🔌 Connection",
            f"Backend: {self.backend_url}",
            self.colors['success_light'] if self.db_connected else self.colors['text_muted'],
            "Connect now →" if not self.db_connected else "Connected ✓"
        )
        conn_card.pack(fill=tk.X)
        
        # Quick start card
        start_card = self.create_info_card(
            right_col,
            "🚀 Quick Start",
            "Get started in 4 easy steps",
            self.colors['accent'],
            "Learn more →"
        )
        start_card.pack(fill=tk.X)
        
        # Features section
        features_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        features_frame.pack(fill=tk.X, pady=30)
        
        tk.Label(
            features_frame,
            text="Features",
            font=('Helvetica', 16, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['text_dark']
        ).pack(anchor='w', pady=(0, 15))
        
        # Feature cards grid
        features_grid = tk.Frame(features_frame, bg=self.colors['bg'])
        features_grid.pack(fill=tk.X)
        
        features = [
            ("📊", "Tables", "Create and manage database tables"),
            ("🔍", "SQL Queries", "Execute powerful SQL queries"),
            ("🤖", "NLP Queries", "Natural language database queries"),
            ("📥", "CSV Import", "Import data from CSV files"),
            ("📤", "CSV Export", "Export data to CSV format"),
            ("🔗", "Table Joins", "Perform INNER JOIN operations"),
        ]
        
        for i, (icon, title, desc) in enumerate(features):
            card = self.create_feature_card(features_grid, icon, title, desc)
            row = i // 3
            col = i % 3
            card.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
            
        features_grid.grid_columnconfigure(0, weight=1)
        features_grid.grid_columnconfigure(1, weight=1)
        features_grid.grid_columnconfigure(2, weight=1)
        
    def create_info_card(self, parent, title, subtitle, accent_color, action_text):
        """Create an information card"""
        card = tk.Frame(parent, bg=self.colors['card'], padx=20, pady=20)
        card.pack(fill=tk.X)
        
        tk.Label(
            card,
            text=title,
            font=('Helvetica', 14, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text_dark']
        ).pack(anchor='w')
        
        tk.Label(
            card,
            text=subtitle,
            font=('Helvetica', 11),
            bg=self.colors['card'],
            fg=self.colors['text_muted']
        ).pack(anchor='w', pady=5)
        
        tk.Label(
            card,
            text=action_text,
            font=('Helvetica', 10, 'bold'),
            bg=self.colors['card'],
            fg=accent_color
        ).pack(anchor='w', pady=(5, 0))
        
        return card
    
    def create_feature_card(self, parent, icon, title, desc):
        """Create a feature card"""
        card = tk.Frame(parent, bg=self.colors['card'], padx=15, pady=15)
        
        icon_label = tk.Label(
            card,
            text=icon,
            font=('Helvetica', 24),
            bg=self.colors['card'],
            fg=self.colors['success_light']
        )
        icon_label.pack(pady=(0, 10))
        
        tk.Label(
            card,
            text=title,
            font=('Helvetica', 12, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text_dark']
        ).pack()
        
        tk.Label(
            card,
            text=desc,
            font=('Helvetica', 9),
            bg=self.colors['card'],
            fg=self.colors['text_muted'],
            wraplength=150,
            justify=tk.CENTER
        ).pack()
        
        return card
        
    def show_tables(self):
        if not self.db_connected:
            messagebox.showwarning("Not Connected", "Please connect to database first!")
            return
        
        self.clear_content()
        self.page_title.config(text="Tables")
        self.breadcrumb.config(text="")
        
        # Refresh tables from backend
        self.load_tables()
        
        # Update table count in status bar
        self.table_count_label.config(text=f"📋 {len(self.tables)} Tables")
        self.tables_status_label.config(text=f"{len(self.tables)} tables")
        
        if not self.tables:
            # Empty state
            empty_frame = tk.Frame(self.content_area, bg=self.colors['bg'])
            empty_frame.pack(fill=tk.BOTH, expand=True, pady=50)
            
            icon = tk.Label(
                empty_frame,
                text="📋",
                font=('Helvetica', 64),
                bg=self.colors['bg'],
                fg=self.colors['text_muted']
            )
            icon.pack(pady=20)
            
            tk.Label(
                empty_frame,
                text="No Tables Found",
                font=('Helvetica', 24, 'bold'),
                bg=self.colors['bg'],
                fg=self.colors['text_dark']
            ).pack()
            
            tk.Label(
                empty_frame,
                text="Create your first table or import from CSV to get started",
                font=('Helvetica', 12),
                bg=self.colors['bg'],
                fg=self.colors['text_muted']
            ).pack(pady=10)
            
            # Quick actions
            btn_frame = tk.Frame(empty_frame, bg=self.colors['bg'])
            btn_frame.pack(pady=30)
            
            self.create_card_button(btn_frame, "➕ Create Table", self.colors['success_light'], 
                                    self.show_create_table).pack(side=tk.LEFT, padx=10)
            self.create_card_button(btn_frame, "📥 Import CSV", self.colors['accent'], 
                                    self.show_import_csv).pack(side=tk.LEFT, padx=10)
            return
        
        # Tables list with cards
        tables_container = tk.Frame(self.content_area, bg=self.colors['bg'])
        tables_container.pack(fill=tk.BOTH, expand=True)
        
        # Header with actions
        header = tk.Frame(tables_container, bg=self.colors['bg'])
        header.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            header,
            text=f"All Tables ({len(self.tables)})",
            font=('Helvetica', 14, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['text_dark']
        ).pack(side=tk.LEFT)
        
        # Quick filter
        filter_frame = tk.Frame(header, bg=self.colors['bg'])
        filter_frame.pack(side=tk.RIGHT)
        
        self.table_search = tk.Entry(
            filter_frame,
            font=('Helvetica', 10),
            bg=self.colors['input_bg'],
            fg=self.colors['text_dark'],
            insertbackground=self.colors['text_dark'],
            width=20,
            bd=0,
            highlightthickness=1,
            highlightbackground=self.colors['border']
        )
        self.table_search.pack(side=tk.RIGHT, padx=(10, 0))
        self.table_search.insert(0, "🔍 Search tables...")
        self.table_search.bind('<FocusIn>', self._clear_search_placeholder)
        self.table_search.bind('<KeyRelease>', self._filter_tables)
        self.table_search.bind('<FocusOut>', self._restore_search_placeholder)
        self.search_placeholder_active = True
        
        # Scrollable frame for table cards
        canvas = tk.Canvas(tables_container, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(tables_container, orient="vertical", command=canvas.yview)
        
        self.tables_frame = tk.Frame(canvas, bg=self.colors['bg'])
        
        self.tables_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.tables_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create table cards
        self.table_cards = []
        for table in self.tables:
            card = self.create_table_card(self.tables_frame, table)
            card.pack(fill=tk.X, pady=8)
            self.table_cards.append((table, card))
        
        # Bind mousewheel
        canvas.bind_all('<MouseWheel>', self._on_mousewheel)
    
    def _clear_search_placeholder(self, event):
        if self.search_placeholder_active:
            self.table_search.delete(0, 'end')
            self.search_placeholder_active = False
    
    def _restore_search_placeholder(self, event):
        if not self.table_search.get():
            self.table_search.insert(0, "🔍 Search tables...")
            self.search_placeholder_active = True
    
    def _filter_tables(self, event=None):
        """Filter tables based on search"""
        search_term = self.table_search.get().lower()
        if self.search_placeholder_active:
            search_term = ""
        
        for table, card in self.table_cards:
            if search_term in table.lower():
                card.pack(fill=tk.X, pady=8)
            else:
                card.pack_forget()
    
    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        canvas = event.widget
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def create_table_card(self, parent, table):
        """Create a table card with actions"""
        card = tk.Frame(parent, bg=self.colors['card'], padx=20, pady=15)
        
        # Get table info from backend
        response = self.api_request(f'/api/tables/{table}')
        
        row_count = 0
        col_count = 0
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                row_count = data.get('row_count', 0)
                col_count = len(data.get('columns', []))
            except:
                pass
        
        # Left side - Table info
        info_frame = tk.Frame(card, bg=self.colors['card'])
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Table name with icon
        name_frame = tk.Frame(info_frame, bg=self.colors['card'])
        name_frame.pack(anchor='w')
        
        tk.Label(
            name_frame,
            text="📋",
            font=('Helvetica', 16),
            bg=self.colors['card'],
            fg=self.colors['success_light']
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(
            name_frame,
            text=table,
            font=('Helvetica', 16, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text_dark']
        ).pack(side=tk.LEFT)
        
        # Stats
        stats_frame = tk.Frame(info_frame, bg=self.colors['card'])
        stats_frame.pack(anchor='w', pady=(8, 0))
        
        tk.Label(
            stats_frame,
            text=f"📊 {row_count} rows",
            font=('Helvetica', 10),
            bg=self.colors['card'],
            fg=self.colors['text_muted']
        ).pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Label(
            stats_frame,
            text=f"📐 {col_count} columns",
            font=('Helvetica', 10),
            bg=self.colors['card'],
            fg=self.colors['text_muted']
        ).pack(side=tk.LEFT)
        
        # Right side - Action buttons
        btn_frame = tk.Frame(card, bg=self.colors['card'])
        btn_frame.pack(side=tk.RIGHT)
        
        self.create_table_action_btn(btn_frame, "👁️ View", self.colors['info'], 
                                      lambda t=table: self.view_table(t)).pack(side=tk.LEFT, padx=3)
        self.create_table_action_btn(btn_frame, "📤 Export", self.colors['success_light'], 
                                      lambda t=table: self.export_table(t)).pack(side=tk.LEFT, padx=3)
        self.create_table_action_btn(btn_frame, "🗑️ Delete", self.colors['danger'], 
                                      lambda t=table: self.delete_table(t)).pack(side=tk.LEFT, padx=3)
        
        # Hover effect
        card.bind('<Enter>', lambda e: card.config(bg=self.colors['card_hover']))
        card.bind('<Leave>', lambda e: card.config(bg=self.colors['card']))
        for child in card.winfo_children():
            child.bind('<Enter>', lambda e: card.config(bg=self.colors['card_hover']))
            child.bind('<Leave>', lambda e: card.config(bg=self.colors['card']))
        
        return card
    
    def create_table_action_btn(self, parent, text, color, command):
        """Create a table action button"""
        btn = tk.Button(
            parent,
            text=text,
            font=('Helvetica', 9, 'bold'),
            bg=color,
            fg='white',
            activebackground=color,
            activeforeground='white',
            cursor='hand2',
            bd=0,
            padx=12,
            pady=6,
            command=command,
            relief='flat'
        )
        return btn
    
    def create_card_button(self, parent, text, color, command):
        """Create a card button"""
        btn = tk.Button(
            parent,
            text=text,
            font=('Helvetica', 11, 'bold'),
            bg=color,
            fg='white',
            activebackground=color,
            activeforeground='white',
            cursor='hand2',
            bd=0,
            padx=20,
            pady=12,
            command=command,
            relief='flat'
        )
        return btn

    def view_table(self, table_name):
        """Fetch and display table data from backend"""
        self.current_table = table_name
        
        response = self.api_request(f'/api/tables/{table_name}/data')
        
        if not response or response.status_code != 200:
            messagebox.showerror("Error", f"Failed to load table: {table_name}")
            return
        
        try:
            data = response.json()
            columns = data.get('columns', [])
            rows = data.get('rows', [])
        except:
            messagebox.showerror("Error", "Invalid data format from server")
            return
        
        self.clear_content()
        self.page_title.config(text=f"Table: {table_name}")
        self.breadcrumb.config(text="Tables > " + table_name)
        
        # Table viewer with enhanced styling
        table_frame = tk.Frame(self.content_area, bg=self.colors['bg'])
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Toolbar with better layout
        toolbar = tk.Frame(table_frame, bg=self.colors['card'])
        toolbar.pack(fill=tk.X, padx=0, pady=0)
        
        # Left side - Table info
        info_frame = tk.Frame(toolbar, bg=self.colors['card'])
        info_frame.pack(side=tk.LEFT, padx=20, pady=15)
        
        tk.Label(
            info_frame,
            text=f"📋 {table_name}",
            font=('Helvetica', 14, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text_dark']
        ).pack(anchor='w')
        
        tk.Label(
            info_frame,
            text=f"{len(rows)} rows • {len(columns)} columns",
            font=('Helvetica', 10),
            bg=self.colors['card'],
            fg=self.colors['text_muted']
        ).pack(anchor='w')
        
        # Right side - Action buttons
        action_frame = tk.Frame(toolbar, bg=self.colors['card'])
        action_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        self.create_table_action_btn(action_frame, "🔄 Refresh", self.colors['input_bg'], 
                                      lambda: self.view_table(table_name)).pack(side=tk.LEFT, padx=3)
        self.create_table_action_btn(action_frame, "➕ Add Row", self.colors['success_light'], 
                                      lambda: self.show_insert_row(table_name, columns)).pack(side=tk.LEFT, padx=3)
        self.create_table_action_btn(action_frame, "📤 Export", self.colors['info'], 
                                      lambda: self.export_table(table_name)).pack(side=tk.LEFT, padx=3)
        self.create_table_action_btn(action_frame, "🔙 Back", self.colors['warning'], 
                                      self.show_tables).pack(side=tk.LEFT, padx=3)
        
        # Data table frame
        data_frame = tk.Frame(table_frame, bg=self.colors['card'])
        data_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=(0, 20))
        
        # Create treeview with custom styling
        tree_frame = tk.Frame(data_frame, bg=self.colors['card'], padx=15, pady=15)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            style="Custom.Treeview"
        )
        
        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)
        
        # Configure columns
        for col in columns:
            tree.heading(col, text=col, command=lambda c=col: self._sort_treeview(tree, c))
            tree.column(col, width=120, anchor='center', minwidth=80)
        
        # Insert data with alternating colors
        for i, row in enumerate(rows):
            tags = ('evenrow',) if i % 2 == 0 else ('oddrow',)
            tree.insert('', tk.END, values=row, tags=tags)
        
        # Configure alternating row colors
        tree.tag_configure('evenrow', background=self.colors['tree_bg'])
        tree.tag_configure('oddrow', background=self.colors['tree_alt'])
        
        # Pack tree and scrollbars
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Store tree reference for sorting
        self.current_tree = tree
        self.sort_reverse = False
    
    def _sort_treeview(self, tree, col):
        """Sort treeview by column"""
        data = [(tree.item(item)['values'], item) for item in tree.get_children('')]
        data.sort(key=lambda x: x[0][0] if x[0] else '', reverse=self.sort_reverse)
        
        for index, (values, item) in enumerate(data):
            tree.move(item, '', index)
        
        self.sort_reverse = not self.sort_reverse
        
    def show_query(self):
        if not self.db_connected:
            messagebox.showwarning("Not Connected", "Please connect to database first!")
            return
            
        self.clear_content()
        self.page_title.config(text="SQL Query")
        self.breadcrumb.config(text="")
        
        query_frame = tk.Frame(self.content_area, bg=self.colors['bg'])
        query_frame.pack(fill=tk.BOTH, expand=True)
        
        # Query input section with better styling
        input_card = tk.Frame(query_frame, bg=self.colors['card'])
        input_card.pack(fill=tk.X, pady=(0, 15))
        
        # Header
        input_header = tk.Frame(input_card, bg=self.colors['card'])
        input_header.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(
            input_header,
            text="🔍 SQL Query Editor",
            font=('Helvetica', 14, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text_dark']
        ).pack(side=tk.LEFT)
        
        # Example queries dropdown
        examples = [
            "Example Queries ▼",
            "SELECT * FROM table_name",
            "SELECT * FROM table_name WHERE column = value",
            "SELECT column1, column2 FROM table_name",
            "SELECT * FROM table_name ORDER BY column",
            "SELECT COUNT(*) FROM table_name"
        ]
        
        self.example_var = tk.StringVar(value=examples[0])
        example_combo = ttk.Combobox(
            input_header,
            textvariable=self.example_var,
            values=examples,
            state='readonly',
            font=('Helvetica', 10)
        )
        example_combo.pack(side=tk.RIGHT)
        example_combo.bind('<<ComboboxSelected>>', self._load_example_query)
        
        # Query text area with line numbers
        text_frame = tk.Frame(input_card, bg=self.colors['card'])
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))
        
        # Line numbers
        self.line_numbers = tk.Text(
            text_frame,
            width=4,
            font=('Consolas', 11),
            bg=self.colors['input_bg'],
            fg=self.colors['text_muted'],
            state=tk.DISABLED,
            bd=0
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        # Query input
        self.query_text = scrolledtext.ScrolledText(
            text_frame,
            height=10,
            font=('Consolas', 11),
            bg=self.colors['input_bg'],
            fg=self.colors['text_dark'],
            insertbackground=self.colors['accent'],
            relief=tk.FLAT,
            bd=0
        )
        self.query_text.pack(fill=tk.BOTH, expand=True)
        self.query_text.insert('1.0', '-- Enter your SQL query here\nSELECT * FROM employees WHERE salary > 70000')
        self.query_text.bind('<KeyRelease>', self._update_line_numbers)
        self.query_text.bind('<Control-Return>', lambda e: self.execute_query())
        self.query_text.bind('<Up>', self._navigate_history_up)
        self.query_text.bind('<Down>', self._navigate_history_down)
        
        self._update_line_numbers()
        
        # Buttons with better layout
        btn_frame = tk.Frame(input_card, bg=self.colors['card'])
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        self.create_table_action_btn(btn_frame, "▶ Execute (Ctrl+Enter)", self.colors['accent'], 
                                      self.execute_query).pack(side=tk.LEFT, padx=(0, 10))
        self.create_table_action_btn(btn_frame, "📋 Copy", self.colors['input_bg'], 
                                      self._copy_query).pack(side=tk.LEFT, padx=5)
        self.create_table_action_btn(btn_frame, "🗑️ Clear", self.colors['warning'], 
                                      self._clear_query).pack(side=tk.LEFT, padx=5)
        self.create_table_action_btn(btn_frame, "📜 History", self.colors['input_bg'], 
                                      self._show_query_history).pack(side=tk.LEFT, padx=5)
        
        # Results section
        results_card = tk.Frame(query_frame, bg=self.colors['card'])
        results_card.pack(fill=tk.BOTH, expand=True)
        
        results_header = tk.Frame(results_card, bg=self.colors['card'])
        results_header.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(
            results_header,
            text="📊 Query Results",
            font=('Helvetica', 14, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text_dark']
        ).pack(side=tk.LEFT)
        
        # Results stats
        self.results_stats = tk.Label(
            results_header,
            text="",
            font=('Helvetica', 10),
            bg=self.colors['card'],
            fg=self.colors['text_muted']
        )
        self.results_stats.pack(side=tk.RIGHT)
        
        self.results_text = scrolledtext.ScrolledText(
            results_card,
            height=12,
            font=('Consolas', 10),
            bg=self.colors['input_bg'],
            fg=self.colors['text_dark'],
            relief=tk.FLAT,
            bd=0,
            state=tk.DISABLED
        )
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))
    
    def _update_line_numbers(self, event=None):
        """Update line numbers"""
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete('1.0', tk.END)
        
        lines = self.query_text.index('end-1c').split('.')[0]
        line_nums = '\n'.join(str(i) for i in range(1, int(lines) + 1))
        self.line_numbers.insert('1.0', line_nums)
        
        self.line_numbers.config(state=tk.DISABLED)
    
    def _load_example_query(self, event):
        """Load selected example query"""
        query = self.example_var.get()
        if "▼" in query or query == "Example Queries ▼":
            return
        
        self.query_text.delete('1.0', tk.END)
        self.query_text.insert('1.0', query)
        self._update_line_numbers()
    
    def _copy_query(self):
        """Copy query to clipboard"""
        query = self.query_text.get('1.0', tk.END).strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(query)
        self.update_status("Query copied to clipboard", self.colors['success_light'])
    
    def _clear_query(self):
        """Clear query"""
        self.query_text.delete('1.0', tk.END)
        self._update_line_numbers()
    
    def _show_query_history(self):
        """Show query history dialog"""
        if not self.query_history:
            messagebox.showinfo("Query History", "No queries executed yet")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Query History")
        dialog.geometry("600x400")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(
            dialog,
            text="📜 Query History",
            font=('Helvetica', 16, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['text_dark']
        ).pack(pady=20)
        
        history_frame = tk.Frame(dialog, bg=self.colors['bg'])
        history_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        listbox = tk.Listbox(
            history_frame,
            font=('Consolas', 10),
            bg=self.colors['card'],
            fg=self.colors['text_dark'],
            selectbackground=self.colors['accent'],
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=self.colors['border']
        )
        listbox.pack(fill=tk.BOTH, expand=True)
        
        for i, query in enumerate(self.query_history):
            display = query[:60] + "..." if len(query) > 60 else query
            listbox.insert(tk.END, f"{i+1}. {display}")
        
        def use_query():
            selection = listbox.curselection()
            if selection:
                query = self.query_history[selection[0]]
                self.query_text.delete('1.0', tk.END)
                self.query_text.insert('1.0', query)
                self._update_line_numbers()
                dialog.destroy()
        
        btn_frame = tk.Frame(dialog, bg=self.colors['bg'])
        btn_frame.pack(pady=20)
        
        tk.Button(
            btn_frame,
            text="Use Selected",
            font=('Helvetica', 10, 'bold'),
            bg=self.colors['accent'],
            fg='white',
            bd=0,
            padx=20,
            pady=8,
            command=use_query
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Close",
            font=('Helvetica', 10),
            bg=self.colors['input_bg'],
            fg=self.colors['text_dark'],
            bd=0,
            padx=20,
            pady=8,
            command=dialog.destroy
        ).pack(side=tk.LEFT, padx=5)
    
    def _navigate_history_up(self, event):
        """Navigate query history up"""
        if self.history_index < len(self.query_history) - 1:
            self.history_index += 1
            query = self.query_history[-1 - self.history_index]
            self.query_text.delete('1.0', tk.END)
            self.query_text.insert('1.0', query)
        return 'break'
    
    def _navigate_history_down(self, event):
        """Navigate query history down"""
        if self.history_index > 0:
            self.history_index -= 1
            query = self.query_history[-1 - self.history_index]
            self.query_text.delete('1.0', tk.END)
            self.query_text.insert('1.0', query)
        elif self.history_index == 0:
            self.history_index = -1
            self.query_text.delete('1.0', tk.END)
        return 'break'
        
    def execute_query(self):
        """Send SQL query to backend"""
        query = self.query_text.get('1.0', tk.END).strip()
        
        if not query or query.startswith('--'):
            messagebox.showwarning("Empty Query", "Please enter a SQL query")
            return
        
        # Add to history
        if query not in self.query_history:
            self.query_history.append(query)
            if len(self.query_history) > 20:
                self.query_history.pop(0)
        self.history_index = -1
        
        self.update_status("Executing query...", self.colors['warning'])
        
        response = self.api_request('/api/query', method='POST', data={'query': query})
        
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete('1.0', tk.END)
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                
                result = f"✓ Query executed successfully\n"
                result += f"{'='*60}\n\n"
                result += f"Query: {query[:50]}...\n\n"
                
                if 'columns' in data and 'rows' in data:
                    columns = data['columns']
                    rows = data['rows']
                    
                    # Format header
                    header = " | ".join(str(col)[:18].ljust(18) for col in columns)
                    result += header + "\n"
                    result += "-" * len(header) + "\n"
                    
                    # Format rows
                    for row in rows:
                        row_str = " | ".join(str(val)[:18].ljust(18) for val in row)
                        result += row_str + "\n"
                    
                    result += f"\n{'='*60}\n"
                    result += f"✓ {len(rows)} row(s) returned\n"
                    
                    self.results_stats.config(text=f"✓ {len(rows)} rows | {len(columns)} columns")
                else:
                    result += data.get('message', 'Query executed successfully')
                    self.results_stats.config(text="✓ Completed")
                
                self.results_text.insert('1.0', result)
                self.update_status("Query executed successfully", self.colors['success_light'])
            except Exception as e:
                error_msg = f"Error parsing response: {str(e)}"
                self.results_text.insert('1.0', error_msg)
                self.results_stats.config(text="✗ Error")
                self.update_status("Query execution failed", self.colors['danger'])
        else:
            error_msg = f"Query failed\n\n"
            if response:
                try:
                    error_data = response.json()
                    error_msg += f"Error: {error_data.get('error', 'Unknown error')}"
                except:
                    error_msg += f"Response: {response.text}"
            
            self.results_text.insert('1.0', error_msg)
            self.results_stats.config(text="✗ Failed")
            self.update_status("Query execution failed", self.colors['danger'])
        
        self.results_text.config(state=tk.DISABLED)

    def show_nlp(self):
        """Show Natural Language Query interface"""
        if not self.db_connected:
            messagebox.showwarning("Not Connected", "Please connect to database first!")
            return
            
        self.clear_content()
        self.page_title.config(text="NLP Query")
        self.breadcrumb.config(text="")
        
        nlp_frame = tk.Frame(self.content_area, bg=self.colors['bg'])
        nlp_frame.pack(fill=tk.BOTH, expand=True)
        
        # Input section
        input_card = tk.Frame(nlp_frame, bg=self.colors['card'])
        input_card.pack(fill=tk.X, pady=(0, 15))
        
        # Header
        input_header = tk.Frame(input_card, bg=self.colors['card'])
        input_header.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(
            input_header,
            text="🤖 Natural Language Query",
            font=('Helvetica', 14, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text_dark']
        ).pack(side=tk.LEFT)
        
        # Help button
        self.create_table_action_btn(
            input_header,
            "💡 Examples",
            self.colors['info'],
            self._show_nlp_help
        ).pack(side=tk.RIGHT)
        
        # Description
        tk.Label(
            input_card,
            text="Ask questions about your data in plain English. The system will translate\nyour natural language into SQL queries automatically.",
            font=('Helvetica', 10),
            bg=self.colors['card'],
            fg=self.colors['text_muted'],
            justify=tk.LEFT
        ).pack(anchor='w', padx=20, pady=(0, 15))
        
        # Input field
        input_frame = tk.Frame(input_card, bg=self.colors['card'])
        input_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        tk.Label(
            input_frame,
            text="Your question:",
            font=('Helvetica', 11, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text_dark']
        ).pack(anchor='w', pady=(0, 5))
        
        self.nlp_input = tk.Entry(
            input_frame,
            font=('Helvetica', 12),
            bg=self.colors['input_bg'],
            fg=self.colors['text_dark'],
            insertbackground=self.colors['accent'],
            relief=tk.FLAT,
            bd=0,
            highlightthickness=1,
            highlightbackground=self.colors['border']
        )
        self.nlp_input.pack(fill=tk.X, pady=(0, 10))
        self.nlp_input.insert(0, "e.g., Show me all employees with salary over 70000")
        
        # Available tables info
        if self.tables:
            tables_info = f"Available tables: {', '.join(self.tables)}"
            tk.Label(
                input_card,
                text=tables_info,
                font=('Helvetica', 9),
                bg=self.colors['card'],
                fg=self.colors['text_muted']
            ).pack(anchor='w', padx=20, pady=(0, 10))
        
        # Execute button
        btn_frame = tk.Frame(input_card, bg=self.colors['card'])
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        self.create_table_action_btn(
            btn_frame,
            "▶ Execute Query",
            self.colors['accent'],
            self.execute_nlp_query
        ).pack(side=tk.LEFT)
        
        # Results section
        results_card = tk.Frame(nlp_frame, bg=self.colors['card'])
        results_card.pack(fill=tk.BOTH, expand=True)
        
        results_header = tk.Frame(results_card, bg=self.colors['card'])
        results_header.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(
            results_header,
            text="📊 Results",
            font=('Helvetica', 14, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text_dark']
        ).pack(side=tk.LEFT)
        
        # Results stats
        self.nlp_results_stats = tk.Label(
            results_header,
            text="",
            font=('Helvetica', 10),
            bg=self.colors['card'],
            fg=self.colors['text_muted']
        )
        self.nlp_results_stats.pack(side=tk.RIGHT)
        
        # NLP Results text area
        self.nlp_results_text = scrolledtext.ScrolledText(
            results_card,
            height=15,
            font=('Consolas', 10),
            bg=self.colors['input_bg'],
            fg=self.colors['text_dark'],
            relief=tk.FLAT,
            bd=0,
            state=tk.DISABLED
        )
        self.nlp_results_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))
    
    def _show_nlp_help(self):
        """Show NLP query examples"""
        help_text = """
Natural Language Query Examples:

📋 SHOW DATA:
  • "Show me all employees"
  • "Display the products table"
  • "View all data from departments"

🔍 FILTER DATA:
  • "Show employees where salary > 70000"
  • "Find products where price < 50"
  • "Display rows where department = Engineering"

📊 AGGREGATE:
  • "Count all employees"
  • "How many products are in stock"

✏️ CREATE DATA:
  • "Create table customers with columns id, name, email"
  • "Insert into employees values 6, Mike, Sales, 60000"

💡 Tips:
  • Use table names from your database
  • Specify column names for filtering
  • Use natural comparison operators (=, >, <, !=)
        """
        messagebox.showinfo("NLP Query Examples", help_text.strip())
    
    def execute_nlp_query(self):
        """Execute natural language query"""
        query = self.nlp_input.get().strip()
        
        if not query or query.startswith("e.g.,"):
            messagebox.showwarning("Empty Query", "Please enter a question")
            return
        
        self.update_status("Processing natural language query...", self.colors['warning'])
        
        response = self.api_request('/api/nlp', method='POST', data={'query': query})
        
        self.nlp_results_text.config(state=tk.NORMAL)
        self.nlp_results_text.delete('1.0', tk.END)
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                
                result = f"✓ Query processed successfully\n"
                result += f"{'='*60}\n\n"
                result += f"Original Query: {query}\n\n"
                
                # Show SQL translation if available
                if 'sql_query' in data:
                    result += f"Generated SQL: {data['sql_query']}\n\n"
                
                # Check for result data
                if 'result' in data:
                    result_data = data['result']
                    if 'columns' in result_data and 'rows' in result_data:
                        columns = result_data['columns']
                        rows = result_data['rows']
                        
                        # Format header
                        header = " | ".join(str(col)[:18].ljust(18) for col in columns)
                        result += header + "\n"
                        result += "-" * len(header) + "\n"
                        
                        # Format rows
                        for row in rows:
                            row_str = " | ".join(str(val)[:18].ljust(18) for val in row)
                            result += row_str + "\n"
                        
                        result += f"\n{'='*60}\n"
                        result += f"✓ {len(rows)} row(s) returned\n"
                        
                        self.nlp_results_stats.config(text=f"✓ {len(rows)} rows | {len(columns)} columns")
                    else:
                        result += result_data.get('message', 'Query executed')
                        self.nlp_results_stats.config(text="✓ Completed")
                else:
                    result += data.get('message', 'Query executed successfully')
                    self.nlp_results_stats.config(text="✓ Completed")
                
                self.nlp_results_text.insert('1.0', result)
                self.update_status("NLP query executed successfully", self.colors['success_light'])
                
            except Exception as e:
                error_msg = f"Error parsing response: {str(e)}"
                self.nlp_results_text.insert('1.0', error_msg)
                self.nlp_results_stats.config(text="✗ Error")
                self.update_status("NLP query execution failed", self.colors['danger'])
        else:
            error_msg = "NLP Query failed\n\n"
            if response:
                try:
                    error_data = response.json()
                    error_msg += f"Error: {error_data.get('error', 'Unknown error')}\n\n"
                    if 'hint' in error_data:
                        error_msg += f"Hint: {error_data['hint']}"
                except:
                    error_msg += f"Response: {response.text}"
            
            self.nlp_results_text.insert('1.0', error_msg)
            self.nlp_results_stats.config(text="✗ Failed")
            self.update_status("NLP query execution failed", self.colors['danger'])
        
        self.nlp_results_text.config(state=tk.DISABLED)
    
    def show_create_table(self):
        if not self.db_connected:
            messagebox.showwarning("Not Connected", "Please connect to database first!")
            return
            
        self.clear_content()
        self.page_title.config(text="Create New Table")
        
        form_frame = tk.Frame(self.content_area, bg=self.colors['card'])
        form_frame.pack(fill=tk.BOTH, padx=100, pady=50)
        
        # Table name
        tk.Label(
            form_frame,
            text="Table Name:",
            font=('Helvetica', 12, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text_dark']
        ).pack(anchor='w', padx=20, pady=(20, 5))
        
        self.table_name_entry = tk.Entry(
            form_frame,
            font=('Helvetica', 11),
            bg=self.colors['input_bg'],
            fg=self.colors['text_dark'],
            insertbackground=self.colors['text_dark'],
            relief=tk.FLAT,
            bd=0,
            highlightthickness=1,
            highlightbackground=self.colors['border']
        )
        self.table_name_entry.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Columns
        tk.Label(
            form_frame,
            text="Columns (comma-separated):",
            font=('Helvetica', 12, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text_dark']
        ).pack(anchor='w', padx=20, pady=(10, 5))
        
        tk.Label(
            form_frame,
            text="Enter column names separated by commas (e.g., id, name, email, salary)",
            font=('Helvetica', 9),
            bg=self.colors['card'],
            fg=self.colors['text_muted']
        ).pack(anchor='w', padx=20)
        
        self.columns_entry = tk.Entry(
            form_frame,
            font=('Helvetica', 11),
            bg=self.colors['input_bg'],
            fg=self.colors['text_dark'],
            insertbackground=self.colors['text_dark'],
            relief=tk.FLAT,
            bd=0,
            highlightthickness=1,
            highlightbackground=self.colors['border']
        )
        self.columns_entry.pack(fill=tk.X, padx=20, pady=(5, 30))
        
        # Create button
        create_btn = tk.Button(
            form_frame,
            text="Create Table",
            font=('Helvetica', 12, 'bold'),
            bg=self.colors['success_light'],
            fg='white',
            activebackground=self.colors['success'],
            cursor='hand2',
            bd=0,
            padx=30,
            pady=12,
            command=self.create_table,
            relief='flat'
        )
        create_btn.pack(pady=20)
    
    def create_table(self):
        """Send create table request to backend"""
        name = self.table_name_entry.get().strip()
        columns_str = self.columns_entry.get().strip()
        
        if not name or not columns_str:
            messagebox.showerror("Error", "Please fill all required fields!")
            return
        
        column_list = [col.strip() for col in columns_str.split(',')]
        
        data = {
            'table_name': name,
            'columns': column_list
        }
        
        response = self.api_request('/api/tables', method='POST', data=data)
        
        if response and response.status_code in [200, 201]:
            messagebox.showinfo("Success", f"Table '{name}' created successfully!")
            self.update_status(f"Table '{name}' created")
            self.load_tables()
            self.show_tables()
        else:
            error_msg = "Failed to create table"
            if response:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', error_msg)
                except:
                    error_msg = f"Server error: {response.status_code}"
            messagebox.showerror("Error", error_msg)
            
    def show_insert_row(self, table_name, columns):
        """Show dialog to insert new row"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Insert Row - {table_name}")
        dialog.geometry("500x600")
        dialog.configure(bg=self.colors['bg'])
        
        # Make dialog modal
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Title
        tk.Label(
            dialog,
            text=f"Insert New Row into {table_name}",
            font=('Helvetica', 16, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['text_dark']
        ).pack(pady=20)
        
        # Form frame
        form_frame = tk.Frame(dialog, bg=self.colors['card'])
        form_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        entries = {}
        
        # Create entry for each column
        for col in columns:
            col_frame = tk.Frame(form_frame, bg=self.colors['card'])
            col_frame.pack(fill=tk.X, padx=20, pady=10)
            
            tk.Label(
                col_frame,
                text=f"{col}:",
                font=('Helvetica', 11, 'bold'),
                bg=self.colors['card'],
                fg=self.colors['text_dark']
            ).pack(anchor='w')
            
            entry = tk.Entry(
                col_frame,
                font=('Helvetica', 11),
                bg=self.colors['input_bg'],
                fg=self.colors['text_dark'],
                insertbackground=self.colors['text_dark'],
                relief=tk.FLAT,
                bd=0,
                highlightthickness=1,
                highlightbackground=self.colors['border']
            )
            entry.pack(fill=tk.X, pady=5)
            entries[col] = entry
        
        # Buttons
        btn_frame = tk.Frame(dialog, bg=self.colors['bg'])
        btn_frame.pack(pady=20)
        
        def insert_data():
            values = {col: entry.get() for col, entry in entries.items()}
            
            response = self.api_request(
                f'/api/tables/{table_name}/rows',
                method='POST',
                data={'values': values}
            )
            
            if response and response.status_code in [200, 201]:
                messagebox.showinfo("Success", "Row inserted successfully!")
                dialog.destroy()
                self.view_table(table_name)
            else:
                error_msg = "Failed to insert row"
                if response:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get('error', error_msg)
                    except:
                        error_msg = f"Server error: {response.status_code}"
                messagebox.showerror("Error", error_msg)
        
        tk.Button(
            btn_frame,
            text="Insert",
            font=('Helvetica', 11, 'bold'),
            bg=self.colors['success_light'],
            fg='white',
            cursor='hand2',
            bd=0,
            padx=20,
            pady=10,
            command=insert_data,
            relief='flat'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Cancel",
            font=('Helvetica', 11, 'bold'),
            bg=self.colors['danger'],
            fg='white',
            cursor='hand2',
            bd=0,
            padx=20,
            pady=10,
            command=dialog.destroy,
            relief='flat'
        ).pack(side=tk.LEFT, padx=5)
        
    def delete_table(self, table_name):
        """Delete table from backend"""
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete table '{table_name}'?\n\nThis action cannot be undone."
        )
        
        if not confirm:
            return
        
        response = self.api_request(f'/api/tables/{table_name}', method='DELETE')
        
        if response and response.status_code == 200:
            messagebox.showinfo("Success", f"Table '{table_name}' deleted successfully!")
            self.update_status(f"Table '{table_name}' deleted")
            self.load_tables()
            self.show_tables()
        else:
            error_msg = "Failed to delete table"
            if response:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', error_msg)
                except:
                    error_msg = f"Server error: {response.status_code}"
            messagebox.showerror("Error", error_msg)
    
    def show_import_csv(self):
        if not self.db_connected:
            messagebox.showwarning("Not Connected", "Please connect to database first!")
            return
            
        filename = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        # Ask for table name
        table_name = tk.simpledialog.askstring(
            "Import CSV",
            "Enter table name for imported data:",
            parent=self.root
        )
        
        if not table_name:
            return
        
        self.update_status("Importing CSV...", self.colors['warning'])
        
        # Send file to backend
        try:
            with open(filename, 'rb') as f:
                files = {'file': (filename, f, 'text/csv')}
                response = self.api_request(
                    f'/api/tables/{table_name}/import',
                    method='POST',
                    files=files
                )
            
            if response and response.status_code in [200, 201]:
                messagebox.showinfo("Success", f"CSV imported successfully as table '{table_name}'!")
                self.update_status(f"Imported {filename}", self.colors['success'])
                self.load_tables()
                self.show_tables()
            else:
                error_msg = "Failed to import CSV"
                if response:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get('error', error_msg)
                    except:
                        error_msg = f"Server error: {response.status_code}"
                messagebox.showerror("Error", error_msg)
                self.update_status("Import failed", self.colors['danger'])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file: {str(e)}")
            self.update_status("Import failed", self.colors['danger'])
            
    def show_export_csv(self):
        if not self.db_connected:
            messagebox.showwarning("Not Connected", "Please connect to database first!")
            return
        
        if not self.tables:
            messagebox.showwarning("No Tables", "No tables available to export!")
            return
        
        # Show dialog to select table
        dialog = tk.Toplevel(self.root)
        dialog.title("Export Table to CSV")
        dialog.geometry("400x300")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(
            dialog,
            text="Select Table to Export",
            font=('Helvetica', 14, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['text_dark']
        ).pack(pady=20)
        
        listbox = tk.Listbox(
            dialog,
            font=('Helvetica', 11),
            bg=self.colors['card'],
            fg=self.colors['text_dark'],
            selectbackground=self.colors['accent'],
            selectmode=tk.SINGLE,
            height=8,
            bd=0,
            highlightthickness=1,
            highlightbackground=self.colors['border']
        )
        listbox.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        for table in self.tables:
            listbox.insert(tk.END, table)
        
        def do_export():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a table!")
                return
            
            table_name = listbox.get(selection[0])
            dialog.destroy()
            self.export_table(table_name)
        
        tk.Button(
            dialog,
            text="Export",
            font=('Helvetica', 11, 'bold'),
            bg=self.colors['success_light'],
            fg='white',
            cursor='hand2',
            bd=0,
            padx=20,
            pady=10,
            command=do_export,
            relief='flat'
        ).pack(pady=10)
            
    def export_table(self, table_name):
        """Export table to CSV"""
        filename = filedialog.asksaveasfilename(
            title=f"Export {table_name}",
            defaultextension=".csv",
            initialfile=f"{table_name}.csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        self.update_status("Exporting table...", self.colors['warning'])
        
        response = self.api_request(f'/api/tables/{table_name}/export')
        
        if response and response.status_code == 200:
            try:
                # Save CSV content to file
                with open(filename, 'wb') as f:
                    f.write(response.content)
                
                messagebox.showinfo("Success", f"Table exported successfully to {filename}!")
                self.update_status("Export successful", self.colors['success'])
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")
                self.update_status("Export failed", self.colors['danger'])
        else:
            messagebox.showerror("Error", "Failed to export table")
            self.update_status("Export failed", self.colors['danger'])
            
    def show_join(self):
        if not self.db_connected:
            messagebox.showwarning("Not Connected", "Please connect to database first!")
            return
        
        if len(self.tables) < 2:
            messagebox.showwarning("Insufficient Tables", "You need at least 2 tables to perform a join!")
            return
            
        self.clear_content()
        self.page_title.config(text="Inner Join")
        
        join_frame = tk.Frame(self.content_area, bg=self.colors['card'])
        join_frame.pack(fill=tk.BOTH, padx=50, pady=30)
        
        # Instructions
        tk.Label(
            join_frame,
            text="Configure Inner Join Parameters",
            font=('Helvetica', 14, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text_dark']
        ).pack(pady=20)
        
        # Left table
        left_frame = tk.Frame(join_frame, bg=self.colors['card'])
        left_frame.pack(fill=tk.X, padx=40, pady=10)
        
        tk.Label(
            left_frame,
            text="Left Table:",
            font=('Helvetica', 12, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text_dark']
        ).pack(anchor='w', pady=(10, 5))
        
        left_table = ttk.Combobox(left_frame, values=self.tables, font=('Helvetica', 11))
        left_table.pack(fill=tk.X, pady=(0, 20))
        left_table.state(['readonly'])
        if self.tables:
            left_table.set(self.tables[0])
        
        # Right table
        right_frame = tk.Frame(join_frame, bg=self.colors['card'])
        right_frame.pack(fill=tk.X, padx=40, pady=10)
        
        tk.Label(
            right_frame,
            text="Right Table:",
            font=('Helvetica', 12, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text_dark']
        ).pack(anchor='w', pady=(10, 5))
        
        right_table = ttk.Combobox(right_frame, values=self.tables, font=('Helvetica', 11))
        right_table.pack(fill=tk.X, pady=(0, 20))
        right_table.state(['readonly'])
        if len(self.tables) > 1:
            right_table.set(self.tables[1])
        
        # Join column
        col_frame = tk.Frame(join_frame, bg=self.colors['card'])
        col_frame.pack(fill=tk.X, padx=40, pady=10)
        
        tk.Label(
            col_frame,
            text="Join Column (must exist in both tables):",
            font=('Helvetica', 12, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text_dark']
        ).pack(anchor='w', pady=(10, 5))
        
        join_column = tk.Entry(
            col_frame,
            font=('Helvetica', 11),
            bg=self.colors['input_bg'],
            fg=self.colors['text_dark'],
            insertbackground=self.colors['text_dark'],
            relief=tk.FLAT,
            bd=0,
            highlightthickness=1,
            highlightbackground=self.colors['border']
        )
        join_column.pack(fill=tk.X, pady=(0, 20))
        
        # Join button
        join_btn = tk.Button(
            join_frame,
            text="Perform Inner Join",
            font=('Helvetica', 12, 'bold'),
            bg=self.colors['accent'],
            fg='white',
            cursor='hand2',
            bd=0,
            padx=30,
            pady=12,
            command=lambda: self.perform_join(
                left_table.get(),
                right_table.get(),
                join_column.get()
            ),
            relief='flat'
        )
        join_btn.pack(pady=30)
        
    def perform_join(self, left, right, column):
        """Send join request to backend"""
        if not left or not right or not column:
            messagebox.showerror("Error", "Please fill all fields!")
            return
        
        if left == right:
            messagebox.showerror("Error", "Please select two different tables!")
            return
        
        data = {
            'left_table': left,
            'right_table': right,
            'join_column': column
        }
        
        self.update_status("Performing join...", self.colors['warning'])
        
        response = self.api_request('/api/join', method='POST', data=data)
        
        if response and response.status_code == 200:
            try:
                result_data = response.json()
                
                # Display join results
                self.display_join_results(left, right, result_data)
                
                self.update_status("Join completed successfully", self.colors['success'])
                messagebox.showinfo("Success", f"Join completed: {left} ⟕ {right}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to parse join results: {str(e)}")
                self.update_status("Join failed", self.colors['danger'])
        else:
            error_msg = "Failed to perform join"
            if response:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', error_msg)
                except:
                    error_msg = f"Server error: {response.status_code}"
            messagebox.showerror("Error", error_msg)
            self.update_status("Join failed", self.colors['danger'])
    
    def display_join_results(self, left_table, right_table, data):
        """Display join results in a new window"""
        result_window = tk.Toplevel(self.root)
        result_window.title(f"Join Results: {left_table} ⟕ {right_table}")
        result_window.geometry("900x600")
        result_window.configure(bg=self.colors['bg'])
        
        # Title
        tk.Label(
            result_window,
            text=f"Join Results: {left_table} ⟕ {right_table}",
            font=('Helvetica', 16, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['text_dark']
        ).pack(pady=20)
        
        # Create treeview
        tree_frame = tk.Frame(result_window, bg=self.colors['card'])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        columns = data.get('columns', [])
        rows = data.get('rows', [])
        
        tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        
        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor='center')
        
        for row in rows:
            tree.insert('', tk.END, values=row)
        
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Info label
        tk.Label(
            result_window,
            text=f"Total rows: {len(rows)}",
            font=('Helvetica', 11),
            bg=self.colors['bg'],
            fg=self.colors['text_dark']
        ).pack(pady=10)
    
    def show_settings(self):
        """Show settings panel"""
        self.clear_content()
        self.page_title.config(text="Settings")
        self.breadcrumb.config(text="")
        
        settings_frame = tk.Frame(self.content_area, bg=self.colors['bg'])
        settings_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Connection settings
        conn_card = tk.Frame(settings_frame, bg=self.colors['card'])
        conn_card.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            conn_card,
            text="🔌 Connection Settings",
            font=('Helvetica', 14, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text_dark']
        ).pack(anchor='w', padx=20, pady=15)
        
        # Backend URL
        url_frame = tk.Frame(conn_card, bg=self.colors['card'])
        url_frame.pack(fill=tk.X, padx=20)
        
        tk.Label(
            url_frame,
            text="Backend URL:",
            font=('Helvetica', 11),
            bg=self.colors['card'],
            fg=self.colors['text_dark'],
            width=15,
            anchor='e'
        ).pack(side=tk.LEFT, pady=10)
        
        self.url_entry = tk.Entry(
            url_frame,
            font=('Helvetica', 11),
            bg=self.colors['input_bg'],
            fg=self.colors['text_dark'],
            insertbackground=self.colors['text_dark'],
            width=30,
            relief=tk.FLAT,
            bd=0,
            highlightthickness=1,
            highlightbackground=self.colors['border']
        )
        self.url_entry.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
        self.url_entry.insert(0, self.backend_url)
        
        # Update URL button
        tk.Button(
            url_frame,
            text="Update",
            font=('Helvetica', 10, 'bold'),
            bg=self.colors['accent'],
            fg='white',
            bd=0,
            padx=15,
            pady=6,
            command=self._update_backend_url,
            relief='flat'
        ).pack(side=tk.LEFT, pady=10)
        
        # Appearance settings
        appearance_card = tk.Frame(settings_frame, bg=self.colors['card'])
        appearance_card.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            appearance_card,
            text="🎨 Appearance",
            font=('Helvetica', 14, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text_dark']
        ).pack(anchor='w', padx=20, pady=15)
        
        # Theme info
        tk.Label(
            appearance_card,
            text="✓ Dark theme is currently active",
            font=('Helvetica', 11),
            bg=self.colors['card'],
            fg=self.colors['success_light']
        ).pack(anchor='w', padx=20, pady=(0, 15))
        
        # Data settings
        data_card = tk.Frame(settings_frame, bg=self.colors['card'])
        data_card.pack(fill=tk.X)
        
        tk.Label(
            data_card,
            text="💾 Data Settings",
            font=('Helvetica', 14, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text_dark']
        ).pack(anchor='w', padx=20, pady=15)
        
        # Auto-refresh option
        self.auto_refresh_var = tk.BooleanVar(value=True)
        auto_refresh_cb = tk.Checkbutton(
            data_card,
            text="Auto-refresh table data after modifications",
            variable=self.auto_refresh_var,
            font=('Helvetica', 11),
            bg=self.colors['card'],
            fg=self.colors['text_dark'],
            selectcolor=self.colors['input_bg'],
            activebackground=self.colors['card']
        )
        auto_refresh_cb.pack(anchor='w', padx=20, pady=(0, 10))
        
        # Query history limit
        hist_frame = tk.Frame(data_card, bg=self.colors['card'])
        hist_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            hist_frame,
            text="Query history limit:",
            font=('Helvetica', 11),
            bg=self.colors['card'],
            fg=self.colors['text_dark']
        ).pack(side=tk.LEFT, pady=10)
        
        self.history_limit = tk.Spinbox(
            hist_frame,
            from_=5,
            to=100,
            width=10,
            font=('Helvetica', 11),
            bg=self.colors['input_bg'],
            fg=self.colors['text_dark']
        )
        self.history_limit.pack(side=tk.LEFT, padx=10, pady=10)
        self.history_limit.delete(0, 'end')
        self.history_limit.insert(0, "20")
        
    def _update_backend_url(self):
        """Update backend URL"""
        new_url = self.url_entry.get().strip()
        if new_url and new_url != self.backend_url:
            self.backend_url = new_url
            self.db_connected = False
            self.update_connection_status(False)
            messagebox.showinfo("Settings", f"Backend URL updated to: {new_url}\n\nPlease reconnect to the server.")
    
    def show_connection_test(self):
        """Show connection testing panel with diagnostics"""
        self.clear_content()
        self.page_title.config(text="Connection Testing")
        
        test_frame = tk.Frame(self.content_area, bg=self.colors['card'])
        test_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=30)
        
        # Current configuration
        config_frame = tk.Frame(test_frame, bg=self.colors['card'])
        config_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(
            config_frame,
            text="Current Configuration",
            font=('Helvetica', 14, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text_dark']
        ).pack(anchor='w', padx=20, pady=10)
        
        tk.Label(
            config_frame,
            text=f"Backend URL: {self.backend_url}",
            font=('Helvetica', 11),
            bg=self.colors['card'],
            fg=self.colors['text_dark']
        ).pack(anchor='w', padx=20, pady=5)
        
        tk.Label(
            config_frame,
            text=f"Status: {'Connected ✓' if self.db_connected else 'Disconnected ✗'}",
            font=('Helvetica', 11),
            bg=self.colors['card'],
            fg=self.colors['success_light'] if self.db_connected else self.colors['danger']
        ).pack(anchor='w', padx=20, pady=(5, 15))
        
        # Change URL option
        url_frame = tk.Frame(test_frame, bg=self.colors['card'])
        url_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(
            url_frame,
            text="Change Backend URL:",
            font=('Helvetica', 12, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text_dark']
        ).pack(anchor='w', pady=5)
        
        url_entry = tk.Entry(
            url_frame,
            font=('Helvetica', 11),
            bg=self.colors['input_bg'],
            fg=self.colors['text_dark'],
            insertbackground=self.colors['text_dark'],
            relief=tk.FLAT,
            bd=0,
            highlightthickness=1,
            highlightbackground=self.colors['border']
        )
        url_entry.pack(fill=tk.X, pady=5)
        url_entry.insert(0, self.backend_url)
        
        def update_url():
            new_url = url_entry.get().strip()
            if new_url:
                self.backend_url = new_url
                self.db_connected = False
                self.status_indicator.config(text="● Disconnected", fg=self.colors['danger'])
                self.connect_btn.config(text="Connect to Database", state=tk.NORMAL, bg=self.colors['accent'])
                messagebox.showinfo("Success", f"Backend URL updated to: {new_url}\n\nClick 'Test Connection' to verify.")
                self.show_connection_test()
        
        tk.Button(
            url_frame,
            text="Update URL",
            font=('Helvetica', 10, 'bold'),
            bg=self.colors['accent'],
            fg='white',
            cursor='hand2',
            bd=0,
            padx=15,
            pady=8,
            command=update_url,
            relief='flat'
        ).pack(anchor='w', pady=10)
        
        # Test endpoints
        tk.Label(
            test_frame,
            text="Test Endpoints:",
            font=('Helvetica', 12, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text_dark']
        ).pack(anchor='w', padx=20, pady=(20, 10))
        
        # Results text area
        results_text = scrolledtext.ScrolledText(
            test_frame,
            height=15,
            font=('Courier', 10),
            bg=self.colors['input_bg'],
            fg=self.colors['text_dark'],
            relief=tk.FLAT,
            bd=0
        )
        results_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        def run_tests():
            results_text.delete('1.0', tk.END)
            results_text.insert('1.0', f"Testing connection to {self.backend_url}...\n\n")
            results_text.update()
            
            endpoints = [
                '/api/health',
                '/api/tables',
                '/api/status'
            ]
            
            results = []
            for endpoint in endpoints:
                results_text.insert(tk.END, f"Testing: {endpoint}... ")
                results_text.update()
                
                try:
                    import time
                    start = time.time()
                    response = requests.get(f"{self.backend_url}{endpoint}", timeout=3)
                    elapsed = time.time() - start
                    
                    status = f"✓ {response.status_code} ({elapsed:.2f}s)"
                    results_text.insert(tk.END, f"{status}\n")
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            results_text.insert(tk.END, f"  Response: {json.dumps(data)[:100]}...\n")
                        except:
                            results_text.insert(tk.END, f"  Response: {response.text[:100]}...\n")
                    
                    results.append((endpoint, True, response.status_code))
                    
                except requests.exceptions.ConnectionError:
                    results_text.insert(tk.END, "✗ Connection refused\n")
                    results.append((endpoint, False, 'Connection Error'))
                except requests.exceptions.Timeout:
                    results_text.insert(tk.END, "✗ Timeout\n")
                    results.append((endpoint, False, 'Timeout'))
                except Exception as e:
                    results_text.insert(tk.END, f"✗ Error: {str(e)}\n")
                    results.append((endpoint, False, str(e)))
                
                results_text.insert(tk.END, "\n")
                results_text.update()
            
            # Summary
            working = [r for r in results if r[1]]
            results_text.insert(tk.END, "\n" + "="*60 + "\n")
            results_text.insert(tk.END, f"Summary: {len(working)}/{len(endpoints)} endpoints responded\n")
            
            if working:
                results_text.insert(tk.END, f"\n✓ Server is running!\n")
                results_text.insert(tk.END, f"Working endpoints: {', '.join([r[0] for r in working])}\n")
            else:
                results_text.insert(tk.END, f"\n✗ Server not responding\n")
                results_text.insert(tk.END, "\nTroubleshooting:\n")
                results_text.insert(tk.END, "1. Run: python server.py\n")
                results_text.insert(tk.END, "2. Verify port 8080 is correct\n")
                results_text.insert(tk.END, "3. Check firewall settings\n")
                results_text.insert(tk.END, "4. Try: curl http://localhost:8080/api/health\n")
            
            results_text.see(tk.END)
        
        # Test button
        tk.Button(
            test_frame,
            text="Run Connection Tests",
            font=('Helvetica', 12, 'bold'),
            bg=self.colors['success_light'],
            fg='white',
            cursor='hand2',
            bd=0,
            padx=30,
            pady=12,
            command=run_tests,
            relief='flat'
        ).pack(pady=20)
    
    def show_about(self):
        self.clear_content()
        self.page_title.config(text="About MiniDB")
        self.breadcrumb.config(text="")
        
        about_frame = tk.Frame(self.content_area, bg=self.colors['bg'])
        about_frame.pack(fill=tk.BOTH, expand=True, pady=30)
        
        # Main card
        card = tk.Frame(about_frame, bg=self.colors['card'])
        card.pack(fill=tk.X, pady=(0, 30))
        
        # Logo
        tk.Label(
            card,
            text="🗄️",
            font=('Helvetica', 48),
            bg=self.colors['card'],
            fg=self.colors['success_light']
        ).pack(pady=(30, 10))
        
        tk.Label(
            card,
            text="MiniDB",
            font=('Helvetica', 28, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text_dark']
        ).pack()
        
        tk.Label(
            card,
            text="Professional Database Manager",
            font=('Helvetica', 12),
            bg=self.colors['card'],
            fg=self.colors['text_muted']
        ).pack()
        
        tk.Label(
            card,
            text=f"Version 1.0.0 | Backend: {self.backend_url}",
            font=('Helvetica', 10),
            bg=self.colors['card'],
            fg=self.colors['text_muted']
        ).pack(pady=20)
        
        # Description
        desc_text = """
A lightweight, high-performance in-memory database system 
built with modern C++ backend and an elegant Python GUI.
        """.strip()
        
        tk.Label(
            card,
            text=desc_text,
            font=('Helvetica', 11),
            bg=self.colors['card'],
            fg=self.colors['text_dark'],
            justify=tk.CENTER
        ).pack(pady=10)
        
        # Features grid
        features_frame = tk.Frame(about_frame, bg=self.colors['bg'])
        features_frame.pack(fill=tk.X)
        
        features = [
            ("💾", "In-memory storage", "Fast data access"),
            ("📊", "Table management", "Create & manage tables"),
            ("🔍", "SQL queries", "Powerful query support"),
            ("🤖", "NLP queries", "Natural language interface"),
            ("📥", "CSV import/export", "Data interchange"),
            ("🔗", "Table joins", "INNER JOIN operations"),
        ]
        
        for i, (icon, title, desc) in enumerate(features):
            feature_card = tk.Frame(features_frame, bg=self.colors['card'], padx=15, pady=15)
            row = i // 3
            col = i % 3
            feature_card.grid(row=row, column=col, padx=8, pady=8, sticky='ew')
            
            tk.Label(
                feature_card,
                text=icon,
                font=('Helvetica', 20),
                bg=self.colors['card'],
                fg=self.colors['success_light']
            ).pack(pady=(0, 5))
            
            tk.Label(
                feature_card,
                text=title,
                font=('Helvetica', 11, 'bold'),
                bg=self.colors['card'],
                fg=self.colors['text_dark']
            ).pack()
            
            tk.Label(
                feature_card,
                text=desc,
                font=('Helvetica', 9),
                bg=self.colors['card'],
                fg=self.colors['text_muted']
            ).pack()
        
        features_frame.grid_columnconfigure(0, weight=1)
        features_frame.grid_columnconfigure(1, weight=1)
        features_frame.grid_columnconfigure(2, weight=1)
        
        # Footer
        tk.Label(
            about_frame,
            text="© 2024 MiniDB Project | Open Source",
            font=('Helvetica', 9),
            bg=self.colors['bg'],
            fg=self.colors['text_muted']
        ).pack(pady=30)


def main():
    root = tk.Tk()
    app = MiniDBGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
