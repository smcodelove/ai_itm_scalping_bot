"""
Order Management Panel Component  
Excel-style position and order management interface
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Optional
import pandas as pd

class OrderManagementPanel:
    """Professional Excel-style order management panel"""
    
    def __init__(self, parent_frame, position_callback: Callable = None, trade_callback: Callable = None):
        self.parent = parent_frame
        self.position_callback = position_callback
        self.trade_callback = trade_callback
        
        # Data storage
        self.positions = []
        self.trades_history = []
        self.selected_position = None
        
        # GUI components
        self.main_frame = None
        self.notebook = None
        self.positions_tree = None
        self.trades_tree = None
        self.summary_labels = {}
        
        # Colors and styles
        self.colors = {
            'bg': '#2d2d2d',
            'panel': '#3d3d3d', 
            'text': '#ffffff',
            'profit': '#00ff88',
            'loss': '#ff4444',
            'neutral': '#ffaa00',
            'header': '#1a1a1a'
        }
        
        self.create_panel()
        
    def create_panel(self):
        """Create the main order management panel"""
        # Main container
        self.main_frame = tk.LabelFrame(
            self.parent,
            text="📋 POSITIONS & ORDERS MANAGEMENT (Excel Style)",
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=('Arial', 12, 'bold'),
            padx=5,
            pady=5
        )
        self.main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 3))
        
        # Create toolbar
        self.create_toolbar()
        
        # Create notebook with tabs
        self.create_notebook()
        
        # Create positions tab
        self.create_positions_tab()
        
        # Create trades tab
        self.create_trades_tab()
        
        # Create summary tab
        self.create_summary_tab()
        
    def create_toolbar(self):
        """Create toolbar with action buttons and summary"""
        toolbar_frame = tk.Frame(self.main_frame, bg=self.colors['bg'])
        toolbar_frame.pack(fill=tk.X, padx=5, pady=(5, 10))
        
        # Left side - Action buttons
        left_buttons = tk.Frame(toolbar_frame, bg=self.colors['bg'])
        left_buttons.pack(side=tk.LEFT)
        
        # Button configurations
        buttons = [
            ("🔄 Refresh", self.refresh_data, '#0088ff'),
            ("❌ Close All", self.close_all_positions, '#ff4444'),
            ("📊 Export", self.export_data, '#666666'),
            ("⚙️ Settings", self.open_settings, '#666666')
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(
                left_buttons,
                text=text,
                command=command,
                bg=color,
                fg='white',
                font=('Arial', 9, 'bold'),
                padx=12,
                pady=3,
                relief='raised',
                bd=2
            )
            btn.pack(side=tk.LEFT, padx=2)
            
        # Right side - Summary info
        right_summary = tk.Frame(toolbar_frame, bg=self.colors['bg'])
        right_summary.pack(side=tk.RIGHT)
        
        # Summary labels
        self.summary_labels['positions'] = tk.Label(
            right_summary,
            text="Active: 0",
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=('Arial', 10, 'bold')
        )
        self.summary_labels['positions'].pack(side=tk.RIGHT, padx=5)
        
        self.summary_labels['value'] = tk.Label(
            right_summary,
            text="Total Value: ₹0",
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=('Arial', 10, 'bold')
        )
        self.summary_labels['value'].pack(side=tk.RIGHT, padx=5)
        
        self.summary_labels['pnl'] = tk.Label(
            right_summary,
            text="Unrealized P&L: ₹0",
            bg=self.colors['bg'],
            fg=self.colors['neutral'],
            font=('Arial', 10, 'bold')
        )
        self.summary_labels['pnl'].pack(side=tk.RIGHT, padx=5)
        
    def create_notebook(self):
        """Create notebook for different tabs"""
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure notebook style
        style = ttk.Style()
        style.configure('TNotebook', background=self.colors['bg'])
        style.configure('TNotebook.Tab', padding=[12, 8])
        
    def create_positions_tab(self):
        """Create active positions tab"""
        # Positions frame
        positions_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(positions_frame, text="🔥 Active Positions")
        
        # Positions sub-toolbar
        pos_toolbar = tk.Frame(positions_frame, bg=self.colors['bg'])
        pos_toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # Quick action buttons for positions
        quick_buttons = [
            ("➕ Add Position", self.add_position_dialog, '#00aa00'),
            ("✏️ Modify Selected", self.modify_position, '#0088ff'),
            ("❌ Close Selected", self.close_selected_position, '#ff4444'),
            ("📈 Square Off", self.square_off_selected, '#ff8800')
        ]
        
        for text, command, color in quick_buttons:
            btn = tk.Button(
                pos_toolbar,
                text=text,
                command=command,
                bg=color,
                fg='white',
                font=('Arial', 8, 'bold'),
                padx=8,
                pady=2
            )
            btn.pack(side=tk.LEFT, padx=2)
            
        # Filter options
        filter_frame = tk.Frame(pos_toolbar, bg=self.colors['bg'])
        filter_frame.pack(side=tk.RIGHT)
        
        tk.Label(filter_frame, text="Filter:", bg=self.colors['bg'], fg=self.colors['text'], 
                font=('Arial', 9)).pack(side=tk.LEFT, padx=5)
        
        self.filter_var = tk.StringVar(value="All")
        filter_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.filter_var,
            values=["All", "NIFTY", "BANKNIFTY", "SENSEX", "Profitable", "Loss Making"],
            width=12,
            state="readonly"
        )
        filter_combo.pack(side=tk.LEFT, padx=2)
        filter_combo.bind("<<ComboboxSelected>>", self.apply_position_filter)
        
        # Positions tree container
        tree_container = tk.Frame(positions_frame, bg=self.colors['bg'])
        tree_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Define columns (Excel-style)
        columns = [
            "ID", "Symbol", "Strike", "Type", "Qty", "Entry ₹", "Current ₹", 
            "P&L ₹", "P&L %", "Status", "Entry Time", "Risk %", "Target ₹", "SL ₹"
        ]
        
        # Create treeview
        self.positions_tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show="headings",
            height=12
        )
        
        # Configure columns
        column_configs = {
            "ID": {"width": 40, "anchor": "center"},
            "Symbol": {"width": 80, "anchor": "center"},
            "Strike": {"width": 60, "anchor": "center"},
            "Type": {"width": 50, "anchor": "center"},
            "Qty": {"width": 50, "anchor": "center"},
            "Entry ₹": {"width": 80, "anchor": "e"},
            "Current ₹": {"width": 80, "anchor": "e"},
            "P&L ₹": {"width": 80, "anchor": "e"},
            "P&L %": {"width": 60, "anchor": "e"},
            "Status": {"width": 80, "anchor": "center"},
            "Entry Time": {"width": 80, "anchor": "center"},
            "Risk %": {"width": 60, "anchor": "e"},
            "Target ₹": {"width": 80, "anchor": "e"},
            "SL ₹": {"width": 80, "anchor": "e"}
        }
        
        for col in columns:
            self.positions_tree.heading(col, text=col, command=lambda c=col: self.sort_positions(c))
            config = column_configs.get(col, {"width": 80, "anchor": "center"})
            self.positions_tree.column(col, width=config["width"], anchor=config["anchor"])
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.positions_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal", command=self.positions_tree.xview)
        self.positions_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.positions_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.positions_tree.bind("<Button-3>", self.show_position_context_menu)
        self.positions_tree.bind("<<TreeviewSelect>>", self.on_position_select)
        self.positions_tree.bind("<Double-1>", self.edit_position)
        
    def create_trades_tab(self):
        """Create trades history tab"""
        # Trades frame
        trades_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(trades_frame, text="📊 Trades History")
        
        # Trades toolbar
        trades_toolbar = tk.Frame(trades_frame, bg=self.colors['bg'])
        trades_toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # Date filter
        date_frame = tk.Frame(trades_toolbar, bg=self.colors['bg'])
        date_frame.pack(side=tk.LEFT)
        
        tk.Label(date_frame, text="Period:", bg=self.colors['bg'], fg=self.colors['text'], 
                font=('Arial', 9)).pack(side=tk.LEFT, padx=5)
        
        self.period_var = tk.StringVar(value="Today")
        period_combo = ttk.Combobox(
            date_frame,
            textvariable=self.period_var,
            values=["Today", "Yesterday", "This Week", "This Month", "All"],
            width=12,
            state="readonly"
        )
        period_combo.pack(side=tk.LEFT, padx=2)
        period_combo.bind("<<ComboboxSelected>>", self.apply_trades_filter)
        
        # Trade statistics
        stats_frame = tk.Frame(trades_toolbar, bg=self.colors['bg'])
        stats_frame.pack(side=tk.RIGHT)
        
        self.trade_stats_label = tk.Label(
            stats_frame,
            text="Total: 0 | Winners: 0 | Losers: 0 | Win Rate: 0%",
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=('Arial', 9, 'bold')
        )
        self.trade_stats_label.pack(side=tk.RIGHT, padx=5)
        
        # Trades tree container
        trades_tree_container = tk.Frame(trades_frame, bg=self.colors['bg'])
        trades_tree_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Define trades columns
        trade_columns = [
            "Trade ID", "Entry Time", "Exit Time", "Symbol", "Strike", "Type", "Qty",
            "Entry ₹", "Exit ₹", "P&L ₹", "P&L %", "Duration", "Strategy", "Fees", "Net P&L"
        ]
        
        # Create trades treeview
        self.trades_tree = ttk.Treeview(
            trades_tree_container,
            columns=trade_columns,
            show="headings",
            height=12
        )
        
        # Configure trade columns
        trade_column_configs = {
            "Trade ID": {"width": 80, "anchor": "center"},
            "Entry Time": {"width": 80, "anchor": "center"},
            "Exit Time": {"width": 80, "anchor": "center"},
            "Symbol": {"width": 80, "anchor": "center"},
            "Strike": {"width": 60, "anchor": "center"},
            "Type": {"width": 50, "anchor": "center"},
            "Qty": {"width": 50, "anchor": "center"},
            "Entry ₹": {"width": 70, "anchor": "e"},
            "Exit ₹": {"width": 70, "anchor": "e"},
            "P&L ₹": {"width": 80, "anchor": "e"},
            "P&L %": {"width": 60, "anchor": "e"},
            "Duration": {"width": 80, "anchor": "center"},
            "Strategy": {"width": 100, "anchor": "center"},
            "Fees": {"width": 60, "anchor": "e"},
            "Net P&L": {"width": 80, "anchor": "e"}
        }
        
        for col in trade_columns:
            self.trades_tree.heading(col, text=col, command=lambda c=col: self.sort_trades(c))
            config = trade_column_configs.get(col, {"width": 80, "anchor": "center"})
            self.trades_tree.column(col, width=config["width"], anchor=config["anchor"])
        
        # Trades scrollbars
        trades_v_scrollbar = ttk.Scrollbar(trades_tree_container, orient="vertical", command=self.trades_tree.yview)
        trades_h_scrollbar = ttk.Scrollbar(trades_tree_container, orient="horizontal", command=self.trades_tree.xview)
        self.trades_tree.configure(yscrollcommand=trades_v_scrollbar.set, xscrollcommand=trades_h_scrollbar.set)
        
        # Pack trades tree and scrollbars
        self.trades_tree.grid(row=0, column=0, sticky="nsew")
        trades_v_scrollbar.grid(row=0, column=1, sticky="ns")
        trades_h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        trades_tree_container.grid_rowconfigure(0, weight=1)
        trades_tree_container.grid_columnconfigure(0, weight=1)
        
        # Bind trades events
        self.trades_tree.bind("<Button-3>", self.show_trade_context_menu)
        self.trades_tree.bind("<Double-1>", self.show_trade_details)
        
    def create_summary_tab(self):
        """Create summary and analytics tab"""
        # Summary frame
        summary_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(summary_frame, text="📈 Summary & Analytics")
        
        # Create summary sections
        self.create_portfolio_summary(summary_frame)
        self.create_performance_summary(summary_frame)
        self.create_risk_summary(summary_frame)
        
    def create_portfolio_summary(self, parent):
        """Create portfolio summary section"""
        portfolio_frame = tk.LabelFrame(
            parent,
            text="💼 Portfolio Summary",
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=('Arial', 11, 'bold')
        )
        portfolio_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Create grid for portfolio metrics
        metrics_frame = tk.Frame(portfolio_frame, bg=self.colors['bg'])
        metrics_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Portfolio metrics
        portfolio_metrics = [
            ("Total Positions:", "total_positions", "0"),
            ("Total Investment:", "total_investment", "₹0"),
            ("Current Value:", "current_value", "₹0"),
            ("Unrealized P&L:", "unrealized_pnl", "₹0"),
            ("Realized P&L:", "realized_pnl", "₹0"),
            ("Total P&L:", "total_pnl", "₹0")
        ]
        
        self.portfolio_labels = {}
        
        for i, (label_text, key, default_value) in enumerate(portfolio_metrics):
            row = i // 3
            col = (i % 3) * 2
            
            # Label
            tk.Label(
                metrics_frame,
                text=label_text,
                bg=self.colors['bg'],
                fg=self.colors['text'],
                font=('Arial', 10)
            ).grid(row=row, column=col, sticky='w', padx=5, pady=3)
            
            # Value
            value_label = tk.Label(
                metrics_frame,
                text=default_value,
                bg=self.colors['bg'],
                fg=self.colors['text'],
                font=('Arial', 10, 'bold')
            )
            value_label.grid(row=row, column=col+1, sticky='w', padx=5, pady=3)
            self.portfolio_labels[key] = value_label
            
    def create_performance_summary(self, parent):
        """Create performance summary section"""
        performance_frame = tk.LabelFrame(
            parent,
            text="📊 Performance Summary",
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=('Arial', 11, 'bold')
        )
        performance_frame.pack(fill=tk.X, padx=10, pady=5)
        
        perf_metrics_frame = tk.Frame(performance_frame, bg=self.colors['bg'])
        perf_metrics_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Performance metrics
        perf_metrics = [
            ("Win Rate:", "win_rate", "0%"),
            ("Profit Factor:", "profit_factor", "0.00"),
            ("Average Trade:", "avg_trade", "₹0"),
            ("Best Trade:", "best_trade", "₹0"),
            ("Worst Trade:", "worst_trade", "₹0"),
            ("Max Drawdown:", "max_drawdown", "0%")
        ]
        
        self.performance_labels = {}
        
        for i, (label_text, key, default_value) in enumerate(perf_metrics):
            row = i // 3
            col = (i % 3) * 2
            
            tk.Label(
                perf_metrics_frame,
                text=label_text,
                bg=self.colors['bg'],
                fg=self.colors['text'],
                font=('Arial', 10)
            ).grid(row=row, column=col, sticky='w', padx=5, pady=3)
            
            value_label = tk.Label(
                perf_metrics_frame,
                text=default_value,
                bg=self.colors['bg'],
                fg=self.colors['text'],
                font=('Arial', 10, 'bold')
            )
            value_label.grid(row=row, column=col+1, sticky='w', padx=5, pady=3)
            self.performance_labels[key] = value_label
            
    def create_risk_summary(self, parent):
        """Create risk summary section"""
        risk_frame = tk.LabelFrame(
            parent,
            text="⚠️ Risk Summary",
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=('Arial', 11, 'bold')
        )
        risk_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        risk_metrics_frame = tk.Frame(risk_frame, bg=self.colors['bg'])
        risk_metrics_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Risk metrics
        risk_metrics = [
            ("Position Risk:", "position_risk", "0%"),
            ("Portfolio Risk:", "portfolio_risk", "0%"),
            ("Daily Loss Limit:", "daily_loss_limit", "5%"),
            ("Used Margin:", "used_margin", "₹0"),
            ("Available Margin:", "available_margin", "₹0"),
            ("Risk-Reward Ratio:", "risk_reward", "1:0")
        ]
        
        self.risk_labels = {}
        
        for i, (label_text, key, default_value) in enumerate(risk_metrics):
            row = i // 3
            col = (i % 3) * 2
            
            tk.Label(
                risk_metrics_frame,
                text=label_text,
                bg=self.colors['bg'],
                fg=self.colors['text'],
                font=('Arial', 10)
            ).grid(row=row, column=col, sticky='w', padx=5, pady=3)
            
            value_label = tk.Label(
                risk_metrics_frame,
                text=default_value,
                bg=self.colors['bg'],
                fg=self.colors['text'],
                font=('Arial', 10, 'bold')
            )
            value_label.grid(row=row, column=col+1, sticky='w', padx=5, pady=3)
            self.risk_labels[key] = value_label
            
    # Data management methods
    def add_position(self, position_data: Dict):
        """Add a new position"""
        position_data['id'] = len(self.positions) + 1
        position_data['entry_time'] = position_data.get('entry_time', datetime.now())
        position_data['status'] = position_data.get('status', 'ACTIVE')
        
        self.positions.append(position_data)
        self.refresh_positions_display()
        
        if self.position_callback:
            self.position_callback('add', position_data)
            
    def update_position(self, position_id: int, updates: Dict):
        """Update an existing position"""
        for position in self.positions:
            if position['id'] == position_id:
                position.update(updates)
                break
                
        self.refresh_positions_display()
        
        if self.position_callback:
            self.position_callback('update', {'id': position_id, 'updates': updates})
            
    def close_position(self, position_id: int, exit_data: Dict = None):
        """Close a position"""
        for position in self.positions:
            if position['id'] == position_id:
                position['status'] = 'CLOSED'
                if exit_data:
                    position.update(exit_data)
                    
                # Create trade record
                trade_record = self.create_trade_record(position)
                self.trades_history.append(trade_record)
                break
                
        self.refresh_positions_display()
        self.refresh_trades_display()
        
        if self.position_callback:
            self.position_callback('close', {'id': position_id, 'exit_data': exit_data})
            
    def create_trade_record(self, position: Dict) -> Dict:
        """Create trade record from closed position"""
        entry_time = position.get('entry_time', datetime.now())
        exit_time = position.get('exit_time', datetime.now())
        duration = exit_time - entry_time
        
        return {
            'trade_id': f"T{position['id']:04d}",
            'entry_time': entry_time,
            'exit_time': exit_time,
            'symbol': position.get('symbol', ''),
            'strike': position.get('strike', ''),
            'type': position.get('type', ''),
            'quantity': position.get('quantity', 0),
            'entry_price': position.get('entry_price', 0),
            'exit_price': position.get('exit_price', 0),
            'pnl': position.get('pnl', 0),
            'pnl_pct': position.get('pnl_pct', 0),
            'duration': duration,
            'strategy': position.get('strategy', 'Manual'),
            'fees': position.get('fees', 0),
            'net_pnl': position.get('pnl', 0) - position.get('fees', 0)
        }
        
    def refresh_positions_display(self):
        """Refresh positions treeview"""
        # Clear existing items
        for item in self.positions_tree.get_children():
            self.positions_tree.delete(item)
            
        # Apply current filter
        filtered_positions = self.apply_position_filter()
        
        # Add positions to tree
        for position in filtered_positions:
            # Format values
            entry_time_str = position.get('entry_time', datetime.now()).strftime("%H:%M")
            
            # Color tags based on P&L
            pnl = position.get('pnl', 0)
            if pnl > 0:
                tags = ('profit',)
            elif pnl < 0:
                tags = ('loss',)
            else:
                tags = ('neutral',)
                
            values = (
                position.get('id', ''),
                position.get('symbol', ''),
                position.get('strike', ''),
                position.get('type', ''),
                position.get('quantity', 0),
                f"₹{position.get('entry_price', 0):.2f}",
                f"₹{position.get('current_price', 0):.2f}",
                f"₹{pnl:+.2f}",
                f"{position.get('pnl_pct', 0):+.1f}%",
                position.get('status', 'ACTIVE'),
                entry_time_str,
                f"{position.get('risk_pct', 0):.1f}%",
                f"₹{position.get('target', 0):.2f}",
                f"₹{position.get('stop_loss', 0):.2f}"
            )
            
            self.positions_tree.insert("", "end", values=values, tags=tags)
            
        # Configure tag colors
        self.positions_tree.tag_configure("profit", foreground=self.colors['profit'])
        self.positions_tree.tag_configure("loss", foreground=self.colors['loss'])
        self.positions_tree.tag_configure("neutral", foreground=self.colors['neutral'])
        
        # Update summary
        self.update_positions_summary()
        
    def refresh_trades_display(self):
        """Refresh trades treeview"""
        # Clear existing items
        for item in self.trades_tree.get_children():
            self.trades_tree.delete(item)
            
        # Apply current filter
        filtered_trades = self.apply_trades_filter()
        
        # Add trades to tree
        for trade in filtered_trades:
            # Format values
            entry_time_str = trade.get('entry_time', datetime.now()).strftime("%H:%M:%S")
            exit_time_str = trade.get('exit_time', datetime.now()).strftime("%H:%M:%S")
            duration_str = str(trade.get('duration', timedelta(0))).split('.')[0]
            
            # Color tags based on P&L
            pnl = trade.get('pnl', 0)
            if pnl > 0:
                tags = ('profit',)
            elif pnl < 0:
                tags = ('loss',)
            else:
                tags = ('neutral',)
                
            values = (
                trade.get('trade_id', ''),
                entry_time_str,
                exit_time_str,
                trade.get('symbol', ''),
                trade.get('strike', ''),
                trade.get('type', ''),
                trade.get('quantity', 0),
                f"₹{trade.get('entry_price', 0):.2f}",
                f"₹{trade.get('exit_price', 0):.2f}",
                f"₹{pnl:+.2f}",
                f"{trade.get('pnl_pct', 0):+.1f}%",
                duration_str,
                trade.get('strategy', 'Manual'),
                f"₹{trade.get('fees', 0):.2f}",
                f"₹{trade.get('net_pnl', 0):+.2f}"
            )
            
            self.trades_tree.insert("", "end", values=values, tags=tags)
            
        # Configure tag colors
        self.trades_tree.tag_configure("profit", foreground=self.colors['profit'])
        self.trades_tree.tag_configure("loss", foreground=self.colors['loss'])
        self.trades_tree.tag_configure("neutral", foreground=self.colors['neutral'])
        
        # Update trade statistics
        self.update_trade_statistics()
        
    def apply_position_filter(self, event=None):
        """Apply filter to positions"""
        filter_value = self.filter_var.get()
        
        if filter_value == "All":
            return [p for p in self.positions if p.get('status') == 'ACTIVE']
        elif filter_value in ["NIFTY", "BANKNIFTY", "SENSEX"]:
            return [p for p in self.positions if p.get('status') == 'ACTIVE' and p.get('symbol') == filter_value]
        elif filter_value == "Profitable":
            return [p for p in self.positions if p.get('status') == 'ACTIVE' and p.get('pnl', 0) > 0]
        elif filter_value == "Loss Making":
            return [p for p in self.positions if p.get('status') == 'ACTIVE' and p.get('pnl', 0) < 0]
        else:
            return [p for p in self.positions if p.get('status') == 'ACTIVE']
            
    def apply_trades_filter(self, event=None):
        """Apply filter to trades"""
        period = self.period_var.get()
        now = datetime.now()
        
        if period == "Today":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            return [t for t in self.trades_history if t.get('entry_time', now) >= start_date]
        elif period == "Yesterday":
            yesterday = now - timedelta(days=1)
            start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
            return [t for t in self.trades_history if start_date <= t.get('entry_time', now) < end_date]
        elif period == "This Week":
            start_date = now - timedelta(days=now.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            return [t for t in self.trades_history if t.get('entry_time', now) >= start_date]
        elif period == "This Month":
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            return [t for t in self.trades_history if t.get('entry_time', now) >= start_date]
        else:  # All
            return self.trades_history
            
    def update_positions_summary(self):
        """Update positions summary in toolbar"""
        active_positions = [p for p in self.positions if p.get('status') == 'ACTIVE']
        
        # Calculate totals
        total_value = sum(p.get('entry_price', 0) * p.get('quantity', 0) for p in active_positions)
        total_pnl = sum(p.get('pnl', 0) for p in active_positions)
        
        # Update labels
        self.summary_labels['positions'].config(text=f"Active: {len(active_positions)}")
        self.summary_labels['value'].config(text=f"Total Value: ₹{total_value:,.0f}")
        
        # Color code P&L
        pnl_color = self.colors['profit'] if total_pnl >= 0 else self.colors['loss']
        self.summary_labels['pnl'].config(
            text=f"Unrealized P&L: ₹{total_pnl:+,.2f}",
            fg=pnl_color
        )
        
    def update_trade_statistics(self):
        """Update trade statistics"""
        filtered_trades = self.apply_trades_filter()
        
        if not filtered_trades:
            self.trade_stats_label.config(text="Total: 0 | Winners: 0 | Losers: 0 | Win Rate: 0%")
            return
            
        total_trades = len(filtered_trades)
        winners = sum(1 for t in filtered_trades if t.get('pnl', 0) > 0)
        losers = sum(1 for t in filtered_trades if t.get('pnl', 0) < 0)
        win_rate = (winners / total_trades * 100) if total_trades > 0 else 0
        
        self.trade_stats_label.config(
            text=f"Total: {total_trades} | Winners: {winners} | Losers: {losers} | Win Rate: {win_rate:.1f}%"
        )
        
    # Event handlers
    def on_position_select(self, event):
        """Handle position selection"""
        selection = self.positions_tree.selection()
        if selection:
            item = selection[0]
            values = self.positions_tree.item(item, 'values')
            if values:
                position_id = int(values[0])
                self.selected_position = next((p for p in self.positions if p['id'] == position_id), None)
                
    def sort_positions(self, column):
        """Sort positions by column"""
        # Implement sorting logic
        pass
        
    def sort_trades(self, column):
        """Sort trades by column"""
        # Implement sorting logic
        pass
        
    # Action methods
    def refresh_data(self):
        """Refresh all data"""
        self.refresh_positions_display()
        self.refresh_trades_display()
        
    def close_all_positions(self):
        """Close all active positions"""
        active_positions = [p for p in self.positions if p.get('status') == 'ACTIVE']
        
        if not active_positions:
            messagebox.showinfo("No Positions", "No active positions to close")
            return
            
        if messagebox.askyesno("Close All", f"Close all {len(active_positions)} active positions?"):
            for position in active_positions:
                self.close_position(position['id'], {'exit_time': datetime.now()})
                
    def close_selected_position(self):
        """Close selected position"""
        if not self.selected_position:
            messagebox.showwarning("No Selection", "Please select a position to close")
            return
            
        if messagebox.askyesno("Close Position", f"Close position {self.selected_position['id']}?"):
            self.close_position(self.selected_position['id'], {'exit_time': datetime.now()})
            
    def export_data(self):
        """Export positions and trades data"""
        try:
            # Export positions
            if self.positions:
                positions_df = pd.DataFrame(self.positions)
                pos_filename = f"positions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                positions_df.to_csv(pos_filename, index=False)
                
            # Export trades
            if self.trades_history:
                trades_df = pd.DataFrame(self.trades_history)
                trades_filename = f"trades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                trades_df.to_csv(trades_filename, index=False)
                
            messagebox.showinfo("Export Complete", "Data exported successfully")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")
            
    def add_position_dialog(self):
        """Show add position dialog"""
        messagebox.showinfo("Add Position", "Add position dialog coming soon!")
        
    def modify_position(self):
        """Modify selected position"""
        if not self.selected_position:
            messagebox.showwarning("No Selection", "Please select a position to modify")
            return
        messagebox.showinfo("Modify Position", "Modify position dialog coming soon!")
        
    def square_off_selected(self):
        """Square off selected position"""
        if not self.selected_position:
            messagebox.showwarning("No Selection", "Please select a position to square off")
            return
        messagebox.showinfo("Square Off", "Square off functionality coming soon!")
        
    def edit_position(self, event):
        """Edit position on double click"""
        if self.selected_position:
            messagebox.showinfo("Edit Position", f"Edit position {self.selected_position['id']} dialog coming soon!")
            
    def show_position_context_menu(self, event):
        """Show context menu for positions"""
        # Create context menu
        context_menu = tk.Menu(self.main_frame, tearoff=0, bg=self.colors['bg'], fg=self.colors['text'])
        context_menu.add_command(label="📈 Modify Quantity", command=self.modify_position)
        context_menu.add_command(label="❌ Close Position", command=self.close_selected_position)
        context_menu.add_command(label="📊 Position Details", command=self.show_position_details)
        context_menu.add_separator()
        context_menu.add_command(label="📋 Copy Position ID", command=self.copy_position_id)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
            
    def show_trade_context_menu(self, event):
        """Show context menu for trades"""
        context_menu = tk.Menu(self.main_frame, tearoff=0, bg=self.colors['bg'], fg=self.colors['text'])
        context_menu.add_command(label="📊 Trade Details", command=self.show_trade_details)
        context_menu.add_command(label="📋 Copy Trade ID", command=self.copy_trade_id)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
            
    def show_position_details(self):
        """Show detailed position information"""
        if self.selected_position:
            messagebox.showinfo("Position Details", f"Position details for {self.selected_position['id']} coming soon!")
            
    def show_trade_details(self, event=None):
        """Show detailed trade information"""
        messagebox.showinfo("Trade Details", "Trade details dialog coming soon!")
        
    def copy_position_id(self):
        """Copy position ID to clipboard"""
        if self.selected_position:
            self.main_frame.clipboard_clear()
            self.main_frame.clipboard_append(str(self.selected_position['id']))
            
    def copy_trade_id(self):
        """Copy trade ID to clipboard"""
        messagebox.showinfo("Copy Trade ID", "Copy trade ID functionality coming soon!")
        
    def open_settings(self):
        """Open panel settings"""
        messagebox.showinfo("Settings", "Panel settings dialog coming soon!")
        
    def get_positions(self) -> List[Dict]:
        """Get all positions"""
        return self.positions.copy()
        
    def get_trades(self) -> List[Dict]:
        """Get all trades"""
        return self.trades_history.copy()
        
    def get_active_positions(self) -> List[Dict]:
        """Get only active positions"""
        return [p for p in self.positions if p.get('status') == 'ACTIVE']
        
    def destroy(self):
        """Clean up the panel"""
        if self.main_frame:
            self.main_frame.destroy()


# Example usage and testing
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Order Management Test")
    root.geometry("1200x700")
    root.configure(bg='#1a1a1a')
    
    # Callback functions
    def on_position_change(action, data):
        print(f"Position {action}: {data}")
        
    def on_trade_change(action, data):
        print(f"Trade {action}: {data}")
    
    # Create order management panel
    order_panel = OrderManagementPanel(root, on_position_change, on_trade_change)
    
    # Add sample data
    sample_positions = [
        {
            'symbol': 'NIFTY',
            'strike': '22200',
            'type': 'CE',
            'quantity': 50,
            'entry_price': 45.75,
            'current_price': 52.30,
            'pnl': 327.50,
            'pnl_pct': 14.3,
            'target': 55.0,
            'stop_loss': 40.0,
            'risk_pct': 2.1,
            'strategy': 'EMA_Cross'
        },
        {
            'symbol': 'BANKNIFTY',
            'strike': '48600',
            'type': 'PE',
            'quantity': 25,
            'entry_price': 78.25,
            'current_price': 71.90,
            'pnl': -158.75,
            'pnl_pct': -8.1,
            'target': 70.0,
            'stop_loss': 85.0,
            'risk_pct': 1.8,
            'strategy': 'RSI_Reversal'
        }
    ]
    
    for pos in sample_positions:
        order_panel.add_position(pos)
    
    root.mainloop()