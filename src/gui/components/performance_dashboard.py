"""
Performance Dashboard Component
Comprehensive performance analytics and metrics display
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Optional
import json

class PerformanceDashboard:
    """Professional performance dashboard with real-time analytics"""
    
    def __init__(self, parent_frame, update_callback: Callable = None):
        self.parent = parent_frame
        self.update_callback = update_callback
        
        # Performance data storage
        self.performance_data = {
            'pnl': {
                'total': 0.0,
                'realized': 0.0,
                'unrealized': 0.0,
                'today': 0.0,
                'yesterday': 0.0,
                'week': 0.0,
                'month': 0.0
            },
            'trades': {
                'total': 0,
                'winning': 0,
                'losing': 0,
                'today': 0,
                'avg_trade': 0.0,
                'best_trade': 0.0,
                'worst_trade': 0.0
            },
            'metrics': {
                'win_rate': 0.0,
                'profit_factor': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'avg_hold_time': 0.0,
                'return_rate': 0.0
            },
            'risk': {
                'daily_risk': 0.0,
                'position_risk': 0.0,
                'var_1_percent': 0.0,
                'var_5_percent': 0.0,
                'beta': 0.0,
                'volatility': 0.0
            }
        }
        
        # Historical data for charts
        self.equity_curve = []
        self.daily_pnl_history = []
        self.trade_history = []
        
        # GUI components
        self.main_frame = None
        self.notebook = None
        self.pnl_labels = {}
        self.metric_labels = {}
        self.risk_labels = {}
        
        # Chart components
        self.performance_fig = None
        self.performance_canvas = None
        
        # Colors
        self.colors = {
            'bg': '#2d2d2d',
            'panel': '#3d3d3d',
            'text': '#ffffff',
            'profit': '#00ff88',
            'loss': '#ff4444',
            'neutral': '#ffaa00',
            'accent': '#0088ff',
            'chart_bg': '#1a1a1a'
        }
        
        self.create_dashboard()
        
    def create_dashboard(self):
        """Create the main performance dashboard"""
        # Main container
        self.main_frame = tk.LabelFrame(
            self.parent,
            text="💰 PERFORMANCE DASHBOARD",
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=('Arial', 12, 'bold'),
            padx=5,
            pady=5
        )
        self.main_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(3, 0))
        
        # Create dashboard sections
        self.create_pnl_section()
        self.create_metrics_section()
        self.create_risk_section()
        self.create_activity_section()
        self.create_chart_section()
        
    def create_pnl_section(self):
        """Create P&L display section"""
        pnl_frame = tk.LabelFrame(
            self.main_frame,
            text="💰 P&L Overview",
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=('Arial', 10, 'bold'),
            padx=8,
            pady=8
        )
        pnl_frame.pack(fill=tk.X, padx=5, pady=(5, 10))
        
        # Total P&L (prominent display)
        total_frame = tk.Frame(pnl_frame, bg=self.colors['bg'])
        total_frame.pack(fill=tk.X, pady=(0, 8))
        
        tk.Label(total_frame, text="TOTAL P&L:", bg=self.colors['bg'], fg=self.colors['text'], 
                font=('Arial', 11, 'bold')).pack(side=tk.LEFT)
        
        self.pnl_labels['total'] = tk.Label(
            total_frame, text="₹0.00", bg=self.colors['bg'], fg=self.colors['accent'], 
            font=('Arial', 14, 'bold')
        )
        self.pnl_labels['total'].pack(side=tk.RIGHT)
        
        # Realized vs Unrealized
        realized_frame = tk.Frame(pnl_frame, bg=self.colors['bg'])
        realized_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(realized_frame, text="Realized:", bg=self.colors['bg'], fg=self.colors['text'], 
                font=('Arial', 9)).pack(side=tk.LEFT)
        self.pnl_labels['realized'] = tk.Label(realized_frame, text="₹0.00", bg=self.colors['bg'], 
                                              fg=self.colors['text'], font=('Arial', 9, 'bold'))
        self.pnl_labels['realized'].pack(side=tk.RIGHT)
        
        unrealized_frame = tk.Frame(pnl_frame, bg=self.colors['bg'])
        unrealized_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(unrealized_frame, text="Unrealized:", bg=self.colors['bg'], fg=self.colors['text'], 
                font=('Arial', 9)).pack(side=tk.LEFT)
        self.pnl_labels['unrealized'] = tk.Label(unrealized_frame, text="₹0.00", bg=self.colors['bg'], 
                                                 fg=self.colors['text'], font=('Arial', 9))
        self.pnl_labels['unrealized'].pack(side=tk.RIGHT)
        
        # Time-based P&L
        tk.Frame(pnl_frame, bg=self.colors['neutral'], height=1).pack(fill=tk.X, pady=5)
        
        time_periods = [('Today:', 'today'), ('This Week:', 'week'), ('This Month:', 'month')]
        
        for label_text, key in time_periods:
            period_frame = tk.Frame(pnl_frame, bg=self.colors['bg'])
            period_frame.pack(fill=tk.X, pady=1)
            
            tk.Label(period_frame, text=label_text, bg=self.colors['bg'], fg=self.colors['text'], 
                    font=('Arial', 8)).pack(side=tk.LEFT)
            self.pnl_labels[key] = tk.Label(period_frame, text="₹0.00", bg=self.colors['bg'], 
                                           fg=self.colors['text'], font=('Arial', 8, 'bold'))
            self.pnl_labels[key].pack(side=tk.RIGHT)
            
    def create_metrics_section(self):
        """Create trading metrics section"""
        metrics_frame = tk.LabelFrame(
            self.main_frame,
            text="📊 Trading Metrics",
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=('Arial', 10, 'bold'),
            padx=8,
            pady=8
        )
        metrics_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Key metrics
        metrics_list = [
            ('Win Rate:', 'win_rate', '%'),
            ('Profit Factor:', 'profit_factor', ''),
            ('Sharpe Ratio:', 'sharpe_ratio', ''),
            ('Max Drawdown:', 'max_drawdown', '%'),
            ('Avg Trade:', 'avg_trade', '₹'),
            ('Best Trade:', 'best_trade', '₹'),
            ('Worst Trade:', 'worst_trade', '₹'),
            ('Total Trades:', 'total_trades', ''),
        ]
        
        for i, (label_text, key, suffix) in enumerate(metrics_list):
            metric_frame = tk.Frame(metrics_frame, bg=self.colors['bg'])
            metric_frame.pack(fill=tk.X, pady=1)
            
            tk.Label(metric_frame, text=label_text, bg=self.colors['bg'], fg=self.colors['text'], 
                    font=('Arial', 8)).pack(side=tk.LEFT)
            
            self.metric_labels[key] = tk.Label(
                metric_frame, text=f"0{suffix}", bg=self.colors['bg'], fg=self.colors['text'], 
                font=('Arial', 8, 'bold')
            )
            self.metric_labels[key].pack(side=tk.RIGHT)
            
    def create_risk_section(self):
        """Create risk management section"""
        risk_frame = tk.LabelFrame(
            self.main_frame,
            text="⚠️ Risk Metrics",
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=('Arial', 10, 'bold'),
            padx=8,
            pady=8
        )
        risk_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Risk metrics
        risk_metrics = [
            ('Daily Risk:', 'daily_risk', '%'),
            ('Position Risk:', 'position_risk', '%'),
            ('VaR (1%):', 'var_1_percent', '₹'),
            ('VaR (5%):', 'var_5_percent', '₹'),
            ('Portfolio Beta:', 'beta', ''),
            ('Volatility:', 'volatility', '%'),
        ]
        
        for label_text, key, suffix in risk_metrics:
            risk_metric_frame = tk.Frame(risk_frame, bg=self.colors['bg'])
            risk_metric_frame.pack(fill=tk.X, pady=1)
            
            tk.Label(risk_metric_frame, text=label_text, bg=self.colors['bg'], fg=self.colors['text'], 
                    font=('Arial', 8)).pack(side=tk.LEFT)
            
            self.risk_labels[key] = tk.Label(
                risk_metric_frame, text=f"0{suffix}", bg=self.colors['bg'], fg=self.colors['text'], 
                font=('Arial', 8, 'bold')
            )
            self.risk_labels[key].pack(side=tk.RIGHT)
            
    def create_activity_section(self):
        """Create live activity log section"""
        activity_frame = tk.LabelFrame(
            self.main_frame,
            text="🔔 Live Activity",
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=('Arial', 10, 'bold'),
            padx=5,
            pady=5
        )
        activity_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Activity text with scrollbar
        activity_container = tk.Frame(activity_frame, bg=self.colors['bg'])
        activity_container.pack(fill=tk.X, padx=5, pady=5)
        
        self.activity_text = tk.Text(
            activity_container, height=8, width=32, 
            bg=self.colors['chart_bg'], fg=self.colors['text'], 
            font=("Consolas", 8), wrap=tk.WORD,
            insertbackground=self.colors['text']
        )
        
        activity_scroll = ttk.Scrollbar(activity_container, orient="vertical", 
                                       command=self.activity_text.yview)
        self.activity_text.configure(yscrollcommand=activity_scroll.set)
        
        self.activity_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        activity_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add initial messages
        self.add_activity_log("💰 Performance Dashboard Ready")
        self.add_activity_log("📊 Real-time monitoring active")
        
    def create_chart_section(self):
        """Create performance charts section"""
        chart_frame = tk.LabelFrame(
            self.main_frame,
            text="📈 Performance Charts",
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=('Arial', 10, 'bold'),
            padx=5,
            pady=5
        )
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Chart controls
        chart_controls = tk.Frame(chart_frame, bg=self.colors['bg'])
        chart_controls.pack(fill=tk.X, pady=(0, 5))
        
        # Chart type selection
        tk.Label(chart_controls, text="Chart:", bg=self.colors['bg'], fg=self.colors['text'], 
                font=('Arial', 8)).pack(side=tk.LEFT, padx=5)
        
        self.chart_type_var = tk.StringVar(value="Equity Curve")
        chart_combo = ttk.Combobox(
            chart_controls,
            textvariable=self.chart_type_var,
            values=["Equity Curve", "Daily P&L", "Drawdown", "Win/Loss Distribution"],
            width=15,
            state="readonly"
        )
        chart_combo.pack(side=tk.LEFT, padx=2)
        chart_combo.bind("<<ComboboxSelected>>", self.update_performance_chart)
        
        # Chart refresh button
        tk.Button(chart_controls, text="🔄", command=self.update_performance_chart,
                 bg=self.colors['accent'], fg='white', font=('Arial', 8), 
                 padx=5, pady=1).pack(side=tk.RIGHT, padx=2)
        
        # Create matplotlib figure
        self.performance_fig, self.performance_ax = plt.subplots(figsize=(6, 4))
        self.performance_fig.patch.set_facecolor(self.colors['chart_bg'])
        self.performance_ax.set_facecolor(self.colors['chart_bg'])
        
        # Embed chart
        self.performance_canvas = FigureCanvasTkAgg(self.performance_fig, chart_frame)
        self.performance_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize chart
        self.initialize_performance_chart()
        
    def initialize_performance_chart(self):
        """Initialize performance chart with sample data"""
        # Generate sample equity curve
        np.random.seed(42)
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), 
                             end=datetime.now(), freq='D')
        
        # Simulate equity curve
        returns = np.random.normal(0.001, 0.02, len(dates))  # Daily returns
        equity = [100000]  # Starting capital
        
        for ret in returns:
            equity.append(equity[-1] * (1 + ret))
            
        self.equity_curve = [{'date': date, 'equity': eq} 
                            for date, eq in zip(dates, equity)]
        
        # Update chart
        self.update_performance_chart()
        
    def update_performance_chart(self, event=None):
        """Update performance chart based on selected type"""
        if not self.performance_ax:
            return
            
        self.performance_ax.clear()
        self.performance_ax.set_facecolor(self.colors['chart_bg'])
        
        chart_type = self.chart_type_var.get()
        
        try:
            if chart_type == "Equity Curve":
                self.plot_equity_curve()
            elif chart_type == "Daily P&L":
                self.plot_daily_pnl()
            elif chart_type == "Drawdown":
                self.plot_drawdown()
            elif chart_type == "Win/Loss Distribution":
                self.plot_win_loss_distribution()
                
        except Exception as e:
            # Show error message on chart
            self.performance_ax.text(0.5, 0.5, f"Chart Error: {str(e)}", 
                                   transform=self.performance_ax.transAxes,
                                   ha='center', va='center', 
                                   color=self.colors['text'])
        
        self.performance_ax.tick_params(colors=self.colors['text'], labelsize=8)
        self.performance_ax.set_title(chart_type, color=self.colors['text'], fontsize=10)
        
        self.performance_canvas.draw()
        
    def plot_equity_curve(self):
        """Plot equity curve chart"""
        if not self.equity_curve:
            self.performance_ax.text(0.5, 0.5, "No equity data available", 
                                   transform=self.performance_ax.transAxes,
                                   ha='center', va='center', color=self.colors['text'])
            return
            
        dates = [item['date'] for item in self.equity_curve]
        equity = [item['equity'] for item in self.equity_curve]
        
        self.performance_ax.plot(dates, equity, color=self.colors['accent'], linewidth=2)
        self.performance_ax.fill_between(dates, equity, alpha=0.3, color=self.colors['accent'])
        
        # Add performance annotations
        start_equity = equity[0]
        end_equity = equity[-1]
        total_return = (end_equity / start_equity - 1) * 100
        
        self.performance_ax.text(0.02, 0.98, f"Total Return: {total_return:+.1f}%", 
                               transform=self.performance_ax.transAxes,
                               va='top', color=self.colors['profit'] if total_return >= 0 else self.colors['loss'],
                               fontweight='bold')
        
    def plot_daily_pnl(self):
        """Plot daily P&L chart"""
        if not self.daily_pnl_history:
            # Generate sample daily P&L
            dates = pd.date_range(start=datetime.now() - timedelta(days=30), 
                                 end=datetime.now(), freq='D')
            daily_pnl = np.random.normal(200, 800, len(dates))  # Sample daily P&L
            
            self.daily_pnl_history = [{'date': date, 'pnl': pnl} 
                                     for date, pnl in zip(dates, daily_pnl)]
        
        dates = [item['date'] for item in self.daily_pnl_history]
        pnl_values = [item['pnl'] for item in self.daily_pnl_history]
        
        colors = [self.colors['profit'] if pnl >= 0 else self.colors['loss'] for pnl in pnl_values]
        self.performance_ax.bar(dates, pnl_values, color=colors, alpha=0.8)
        
        # Add horizontal line at zero
        self.performance_ax.axhline(y=0, color=self.colors['text'], linestyle='-', alpha=0.5)
        
        # Statistics
        avg_pnl = np.mean(pnl_values)
        win_days = len([p for p in pnl_values if p > 0])
        total_days = len(pnl_values)
        
        self.performance_ax.text(0.02, 0.98, f"Avg Daily P&L: ₹{avg_pnl:.0f}", 
                               transform=self.performance_ax.transAxes, va='top', 
                               color=self.colors['text'])
        self.performance_ax.text(0.02, 0.92, f"Win Days: {win_days}/{total_days} ({win_days/total_days*100:.0f}%)", 
                               transform=self.performance_ax.transAxes, va='top', 
                               color=self.colors['text'])
        
    def plot_drawdown(self):
        """Plot drawdown chart"""
        if not self.equity_curve:
            self.performance_ax.text(0.5, 0.5, "No equity data for drawdown", 
                                   transform=self.performance_ax.transAxes,
                                   ha='center', va='center', color=self.colors['text'])
            return
            
        dates = [item['date'] for item in self.equity_curve]
        equity = [item['equity'] for item in self.equity_curve]
        
        # Calculate drawdown
        peak = np.maximum.accumulate(equity)
        drawdown = (equity - peak) / peak * 100  # Percentage drawdown
        
        self.performance_ax.fill_between(dates, drawdown, 0, color=self.colors['loss'], alpha=0.6)
        self.performance_ax.plot(dates, drawdown, color=self.colors['loss'], linewidth=2)
        
        # Max drawdown
        max_dd = np.min(drawdown)
        max_dd_date = dates[np.argmin(drawdown)]
        
        self.performance_ax.text(0.02, 0.98, f"Max Drawdown: {max_dd:.1f}%", 
                               transform=self.performance_ax.transAxes, va='top', 
                               color=self.colors['loss'], fontweight='bold')
        
        # Mark max drawdown point
        self.performance_ax.scatter([max_dd_date], [max_dd], color=self.colors['loss'], 
                                  s=50, zorder=5)
        
    def plot_win_loss_distribution(self):
        """Plot win/loss distribution"""
        if not self.trade_history:
            # Generate sample trade data
            np.random.seed(42)
            trade_pnl = []
            
            # Generate winning trades (60% probability)
            for _ in range(100):
                if np.random.random() < 0.6:  # Win
                    pnl = np.random.exponential(500)  # Positive skewed wins
                else:  # Loss
                    pnl = -np.random.exponential(300)  # Negative skewed losses
                trade_pnl.append(pnl)
            
            self.trade_history = [{'pnl': pnl} for pnl in trade_pnl]
        
        pnl_values = [trade['pnl'] for trade in self.trade_history]
        
        # Create histogram
        self.performance_ax.hist(pnl_values, bins=20, alpha=0.7, 
                               color=self.colors['accent'], edgecolor=self.colors['text'])
        
        # Add vertical line at zero
        self.performance_ax.axvline(x=0, color=self.colors['text'], linestyle='--', alpha=0.8)
        
        # Statistics
        wins = [p for p in pnl_values if p > 0]
        losses = [p for p in pnl_values if p < 0]
        
        self.performance_ax.text(0.02, 0.98, f"Trades: {len(pnl_values)}", 
                               transform=self.performance_ax.transAxes, va='top', 
                               color=self.colors['text'])
        self.performance_ax.text(0.02, 0.92, f"Wins: {len(wins)} | Losses: {len(losses)}", 
                               transform=self.performance_ax.transAxes, va='top', 
                               color=self.colors['text'])
        self.performance_ax.text(0.02, 0.86, f"Avg Win: ₹{np.mean(wins):.0f} | Avg Loss: ₹{np.mean(losses):.0f}", 
                               transform=self.performance_ax.transAxes, va='top', 
                               color=self.colors['text'])
        
    def add_activity_log(self, message: str):
        """Add message to activity log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.activity_text.insert(tk.END, formatted_message)
        self.activity_text.see(tk.END)
        
        # Keep only last 100 lines
        lines = self.activity_text.get("1.0", tk.END).split('\n')
        if len(lines) > 100:
            self.activity_text.delete("1.0", f"{len(lines)-100}.0")
    
    def update_pnl(self, pnl_data: Dict):
        """Update P&L displays with new data"""
        # Update stored data
        self.performance_data['pnl'].update(pnl_data)
        
        # Update labels with color coding
        for key, value in pnl_data.items():
            if key in self.pnl_labels:
                formatted_value = f"₹{value:.2f}"
                self.pnl_labels[key].config(text=formatted_value)
                
                # Color coding
                if value > 0:
                    color = self.colors['profit']
                elif value < 0:
                    color = self.colors['loss']
                else:
                    color = self.colors['text']
                    
                self.pnl_labels[key].config(fg=color)
        
        # Log activity
        if 'total' in pnl_data:
            self.add_activity_log(f"💰 P&L Updated: ₹{pnl_data['total']:.2f}")
    
    def update_metrics(self, metrics_data: Dict):
        """Update trading metrics"""
        self.performance_data['metrics'].update(metrics_data)
        
        for key, value in metrics_data.items():
            if key in self.metric_labels:
                if key == 'win_rate' or key == 'max_drawdown':
                    formatted_value = f"{value:.1f}%"
                elif key in ['avg_trade', 'best_trade', 'worst_trade']:
                    formatted_value = f"₹{value:.0f}"
                elif key == 'total_trades':
                    formatted_value = str(int(value))
                else:
                    formatted_value = f"{value:.2f}"
                    
                self.metric_labels[key].config(text=formatted_value)
    
    def update_risk_metrics(self, risk_data: Dict):
        """Update risk metrics"""
        self.performance_data['risk'].update(risk_data)
        
        for key, value in risk_data.items():
            if key in self.risk_labels:
                if key.endswith('_risk') or key == 'volatility':
                    formatted_value = f"{value:.1f}%"
                elif key.startswith('var_'):
                    formatted_value = f"₹{value:.0f}"
                else:
                    formatted_value = f"{value:.2f}"
                    
                self.risk_labels[key].config(text=formatted_value)
    
    def add_trade(self, trade_data: Dict):
        """Add new trade to history and update metrics"""
        self.trade_history.append(trade_data)
        
        # Update daily P&L history
        today = datetime.now().date()
        today_trades = [t for t in self.trade_history 
                       if t.get('date', datetime.now()).date() == today]
        today_pnl = sum(t.get('pnl', 0) for t in today_trades)
        
        # Update or add today's P&L
        existing_entry = None
        for entry in self.daily_pnl_history:
            if entry['date'].date() == today:
                existing_entry = entry
                break
        
        if existing_entry:
            existing_entry['pnl'] = today_pnl
        else:
            self.daily_pnl_history.append({
                'date': datetime.now(),
                'pnl': today_pnl
            })
        
        # Log trade
        pnl = trade_data.get('pnl', 0)
        symbol = trade_data.get('symbol', 'Unknown')
        side = trade_data.get('side', 'Unknown')
        
        icon = "📈" if pnl > 0 else "📉"
        self.add_activity_log(f"{icon} {side} {symbol}: ₹{pnl:.2f}")
        
        # Update chart if showing daily P&L
        if hasattr(self, 'chart_type_var') and self.chart_type_var.get() == "Daily P&L":
            self.update_performance_chart()
    
    def add_equity_point(self, equity_value: float):
        """Add new equity point to curve"""
        self.equity_curve.append({
            'date': datetime.now(),
            'equity': equity_value
        })
        
        # Keep only last 100 points for performance
        if len(self.equity_curve) > 100:
            self.equity_curve = self.equity_curve[-100:]
        
        # Update chart if showing equity curve
        if hasattr(self, 'chart_type_var') and self.chart_type_var.get() == "Equity Curve":
            self.update_performance_chart()
    
    def get_performance_summary(self) -> Dict:
        """Get comprehensive performance summary"""
        return {
            'pnl': self.performance_data['pnl'],
            'trades': self.performance_data['trades'],
            'metrics': self.performance_data['metrics'],
            'risk': self.performance_data['risk'],
            'equity_curve_points': len(self.equity_curve),
            'trade_history_count': len(self.trade_history),
            'daily_pnl_points': len(self.daily_pnl_history)
        }
    
    def export_performance_data(self) -> Dict:
        """Export all performance data for saving"""
        return {
            'performance_data': self.performance_data,
            'equity_curve': self.equity_curve,
            'daily_pnl_history': self.daily_pnl_history,
            'trade_history': self.trade_history,
            'export_timestamp': datetime.now().isoformat()
        }
    
    def import_performance_data(self, data: Dict):
        """Import performance data from saved file"""
        try:
            if 'performance_data' in data:
                self.performance_data = data['performance_data']
            if 'equity_curve' in data:
                self.equity_curve = data['equity_curve']
            if 'daily_pnl_history' in data:
                self.daily_pnl_history = data['daily_pnl_history']
            if 'trade_history' in data:
                self.trade_history = data['trade_history']
            
            # Update all displays
            self.update_pnl(self.performance_data['pnl'])
            self.update_metrics(self.performance_data['metrics'])
            self.update_risk_metrics(self.performance_data['risk'])
            self.update_performance_chart()
            
            self.add_activity_log("📁 Performance data imported successfully")
            
        except Exception as e:
            self.add_activity_log(f"❌ Error importing data: {str(e)}")
    
    def reset_performance_data(self):
        """Reset all performance data to initial state"""
        # Reset data structures
        self.performance_data = {
            'pnl': {
                'total': 0.0, 'realized': 0.0, 'unrealized': 0.0,
                'today': 0.0, 'yesterday': 0.0, 'week': 0.0, 'month': 0.0
            },
            'trades': {
                'total': 0, 'winning': 0, 'losing': 0, 'today': 0,
                'avg_trade': 0.0, 'best_trade': 0.0, 'worst_trade': 0.0
            },
            'metrics': {
                'win_rate': 0.0, 'profit_factor': 0.0, 'sharpe_ratio': 0.0,
                'max_drawdown': 0.0, 'avg_hold_time': 0.0, 'return_rate': 0.0
            },
            'risk': {
                'daily_risk': 0.0, 'position_risk': 0.0, 'var_1_percent': 0.0,
                'var_5_percent': 0.0, 'beta': 0.0, 'volatility': 0.0
            }
        }
        
        # Clear historical data
        self.equity_curve = []
        self.daily_pnl_history = []
        self.trade_history = []
        
        # Update displays
        self.update_pnl(self.performance_data['pnl'])
        self.update_metrics(self.performance_data['metrics'])
        self.update_risk_metrics(self.performance_data['risk'])
        
        # Clear activity log
        self.activity_text.delete(1.0, tk.END)
        self.add_activity_log("🔄 Performance data reset")
        self.add_activity_log("💰 Dashboard ready for new session")
        
        # Re-initialize chart
        self.initialize_performance_chart()
    
    def calculate_advanced_metrics(self):
        """Calculate advanced performance metrics from trade history"""
        if not self.trade_history:
            return
        
        pnl_values = [trade.get('pnl', 0) for trade in self.trade_history]
        
        if not pnl_values:
            return
        
        # Basic metrics
        total_trades = len(pnl_values)
        winning_trades = [p for p in pnl_values if p > 0]
        losing_trades = [p for p in pnl_values if p < 0]
        
        win_rate = len(winning_trades) / total_trades * 100 if total_trades > 0 else 0
        avg_trade = np.mean(pnl_values)
        best_trade = max(pnl_values) if pnl_values else 0
        worst_trade = min(pnl_values) if pnl_values else 0
        
        # Profit factor
        gross_profit = sum(winning_trades) if winning_trades else 0
        gross_loss = abs(sum(losing_trades)) if losing_trades else 0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Sharpe ratio (simplified)
        if len(pnl_values) > 1:
            returns = np.array(pnl_values)
            sharpe_ratio = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
        else:
            sharpe_ratio = 0
        
        # Max drawdown from equity curve
        if self.equity_curve:
            equity_values = [point['equity'] for point in self.equity_curve]
            peak = np.maximum.accumulate(equity_values)
            drawdown = (equity_values - peak) / peak * 100
            max_drawdown = abs(min(drawdown)) if drawdown.size > 0 else 0
        else:
            max_drawdown = 0
        
        # Update metrics
        metrics_update = {
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'avg_trade': avg_trade,
            'best_trade': best_trade,
            'worst_trade': worst_trade,
            'total_trades': total_trades
        }
        
        self.update_metrics(metrics_update)
    
    def update_real_time_metrics(self, current_positions: List[Dict]):
        """Update real-time risk metrics based on current positions"""
        if not current_positions:
            return
        
        total_exposure = sum(pos.get('value', 0) for pos in current_positions)
        unrealized_pnl = sum(pos.get('unrealized_pnl', 0) for pos in current_positions)
        
        # Calculate position risk as percentage of total capital
        total_capital = 1000000  # Default capital, should be configurable
        position_risk = (total_exposure / total_capital) * 100 if total_capital > 0 else 0
        
        # Simple VaR calculation (1% and 5%)
        position_values = [pos.get('value', 0) for pos in current_positions]
        if position_values:
            var_1_percent = np.percentile(position_values, 1)
            var_5_percent = np.percentile(position_values, 5)
        else:
            var_1_percent = var_5_percent = 0
        
        # Update risk metrics
        risk_update = {
            'position_risk': position_risk,
            'var_1_percent': var_1_percent,
            'var_5_percent': var_5_percent,
            'daily_risk': position_risk * 0.1,  # Simplified daily risk
            'volatility': np.std([pos.get('pnl', 0) for pos in current_positions]) if current_positions else 0
        }
        
        self.update_risk_metrics(risk_update)
        
        # Update unrealized P&L
        self.update_pnl({'unrealized': unrealized_pnl})
    
    def generate_performance_report(self) -> str:
        """Generate detailed text performance report"""
        report = "TRADING PERFORMANCE REPORT\n"
        report += "=" * 50 + "\n\n"
        
        # P&L Summary
        report += "P&L SUMMARY:\n"
        report += f"Total P&L: ₹{self.performance_data['pnl']['total']:.2f}\n"
        report += f"Realized P&L: ₹{self.performance_data['pnl']['realized']:.2f}\n"
        report += f"Unrealized P&L: ₹{self.performance_data['pnl']['unrealized']:.2f}\n"
        report += f"Today's P&L: ₹{self.performance_data['pnl']['today']:.2f}\n"
        report += f"This Week: ₹{self.performance_data['pnl']['week']:.2f}\n"
        report += f"This Month: ₹{self.performance_data['pnl']['month']:.2f}\n\n"
        
        # Trading Metrics
        report += "TRADING METRICS:\n"
        report += f"Total Trades: {self.performance_data['metrics']['total_trades']}\n"
        report += f"Win Rate: {self.performance_data['metrics']['win_rate']:.1f}%\n"
        report += f"Profit Factor: {self.performance_data['metrics']['profit_factor']:.2f}\n"
        report += f"Sharpe Ratio: {self.performance_data['metrics']['sharpe_ratio']:.2f}\n"
        report += f"Average Trade: ₹{self.performance_data['metrics']['avg_trade']:.2f}\n"
        report += f"Best Trade: ₹{self.performance_data['metrics']['best_trade']:.2f}\n"
        report += f"Worst Trade: ₹{self.performance_data['metrics']['worst_trade']:.2f}\n"
        report += f"Max Drawdown: {self.performance_data['metrics']['max_drawdown']:.1f}%\n\n"
        
        # Risk Metrics
        report += "RISK METRICS:\n"
        report += f"Daily Risk: {self.performance_data['risk']['daily_risk']:.1f}%\n"
        report += f"Position Risk: {self.performance_data['risk']['position_risk']:.1f}%\n"
        report += f"VaR (1%): ₹{self.performance_data['risk']['var_1_percent']:.0f}\n"
        report += f"VaR (5%): ₹{self.performance_data['risk']['var_5_percent']:.0f}\n"
        report += f"Portfolio Beta: {self.performance_data['risk']['beta']:.2f}\n"
        report += f"Volatility: {self.performance_data['risk']['volatility']:.1f}%\n\n"
        
        # Historical Data Summary
        report += "DATA SUMMARY:\n"
        report += f"Equity Curve Points: {len(self.equity_curve)}\n"
        report += f"Daily P&L History: {len(self.daily_pnl_history)} days\n"
        report += f"Trade History: {len(self.trade_history)} trades\n\n"
        
        report += f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return report
    
    def save_chart_image(self, filename: str = None):
        """Save current chart as image"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            chart_type = self.chart_type_var.get().replace(" ", "_").lower()
            filename = f"performance_chart_{chart_type}_{timestamp}.png"
        
        try:
            self.performance_fig.savefig(filename, dpi=300, bbox_inches='tight',
                                       facecolor=self.colors['chart_bg'],
                                       edgecolor='none')
            self.add_activity_log(f"📊 Chart saved: {filename}")
            return filename
        except Exception as e:
            self.add_activity_log(f"❌ Error saving chart: {str(e)}")
            return None


# Usage Example and Testing
if __name__ == "__main__":
    import random
    
    # Create test window
    root = tk.Tk()
    root.title("Performance Dashboard Test")
    root.geometry("800x1000")
    root.configure(bg='#2d2d2d')
    
    # Create dashboard
    dashboard = PerformanceDashboard(root)
    
    # Test data updates
    def update_test_data():
        """Update dashboard with random test data"""
        # Random P&L update
        pnl_update = {
            'total': random.uniform(-5000, 10000),
            'realized': random.uniform(-3000, 8000),
            'unrealized': random.uniform(-2000, 2000),
            'today': random.uniform(-1000, 3000),
            'week': random.uniform(-5000, 8000),
            'month': random.uniform(-10000, 15000)
        }
        dashboard.update_pnl(pnl_update)
        
        # Random trade
        trade = {
            'symbol': random.choice(['NIFTY', 'BANKNIFTY', 'FINNIFTY']),
            'side': random.choice(['BUY', 'SELL']),
            'pnl': random.uniform(-500, 800),
            'date': datetime.now()
        }
        dashboard.add_trade(trade)
        
        # Random equity point
        current_equity = 100000 + pnl_update['total']
        dashboard.add_equity_point(current_equity)
        
        # Calculate metrics
        dashboard.calculate_advanced_metrics()
        
        # Schedule next update
        root.after(2000, update_test_data)  # Update every 2 seconds
    
    # Start test data updates
    root.after(1000, update_test_data)
    
    # Control buttons
    control_frame = tk.Frame(root, bg='#2d2d2d')
    control_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
    
    tk.Button(control_frame, text="Reset Data", 
             command=dashboard.reset_performance_data,
             bg='#e74c3c', fg='white', padx=20).pack(side=tk.LEFT, padx=5)
    
    tk.Button(control_frame, text="Generate Report", 
             command=lambda: print(dashboard.generate_performance_report()),
             bg='#3498db', fg='white', padx=20).pack(side=tk.LEFT, padx=5)
    
    tk.Button(control_frame, text="Save Chart", 
             command=dashboard.save_chart_image,
             bg='#27ae60', fg='white', padx=20).pack(side=tk.LEFT, padx=5)
    
    print("🚀 Performance Dashboard Test Started")
    print("Dashboard will update every 2 seconds with random data")
    print("Check console for generated reports")
    
    root.mainloop()