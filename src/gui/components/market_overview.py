"""
Market Overview Panel Component
Real-time market data display for NIFTY, BANKNIFTY, SENSEX
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from datetime import datetime
from typing import Dict, List, Callable

class MarketOverviewPanel:
    """Professional market overview panel with live data"""
    
    def __init__(self, parent_frame, symbols: List[str], update_callback: Callable = None):
        self.parent = parent_frame
        self.symbols = symbols
        self.update_callback = update_callback
        
        # Market data storage
        self.market_data = {}
        for symbol in symbols:
            self.market_data[symbol] = {
                'current_price': 0.0,
                'change': 0.0,
                'change_pct': 0.0,
                'volume': 0,
                'high': 0.0,
                'low': 0.0,
                'open': 0.0,
                'last_update': datetime.now()
            }
        
        # GUI components
        self.main_frame = None
        self.symbol_frames = {}
        self.price_labels = {}
        self.change_labels = {}
        self.volume_labels = {}
        self.high_low_labels = {}
        
        # Colors
        self.colors = {
            'bg': '#2d2d2d',
            'panel': '#3d3d3d',
            'text': '#ffffff',
            'profit': '#00ff88',
            'loss': '#ff4444',
            'neutral': '#ffaa00'
        }
        
        self.create_panel()
        
    def create_panel(self):
        """Create the market overview panel"""
        # Main container
        self.main_frame = tk.LabelFrame(
            self.parent, 
            text="📊 LIVE MARKET OVERVIEW", 
            bg=self.colors['bg'], 
            fg=self.colors['text'], 
            font=('Arial', 12, 'bold'),
            padx=10,
            pady=10
        )
        self.main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 3))
        
        # Create symbol panels
        self.create_symbol_panels()
        
        # Create control buttons
        self.create_control_buttons()
        
    def create_symbol_panels(self):
        """Create individual panels for each symbol"""
        # Container for symbol panels
        symbols_container = tk.Frame(self.main_frame, bg=self.colors['bg'])
        symbols_container.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create grid layout
        for i, symbol in enumerate(self.symbols):
            self.create_symbol_card(symbols_container, symbol, i)
            
        # Configure grid weights for responsive layout
        for i in range(len(self.symbols)):
            symbols_container.grid_columnconfigure(i, weight=1)
        symbols_container.grid_rowconfigure(0, weight=1)
        
    def create_symbol_card(self, parent, symbol: str, column: int):
        """Create a card for individual symbol"""
        # Main card frame
        card_frame = tk.Frame(
            parent, 
            bg=self.colors['panel'], 
            relief='raised', 
            bd=2,
            padx=15,
            pady=15
        )
        card_frame.grid(row=0, column=column, padx=8, pady=5, sticky='nsew')
        
        self.symbol_frames[symbol] = card_frame
        
        # Symbol name (header)
        symbol_label = tk.Label(
            card_frame, 
            text=symbol, 
            bg=self.colors['panel'], 
            fg=self.colors['text'], 
            font=('Arial', 16, 'bold')
        )
        symbol_label.pack(pady=(0, 8))
        
        # Current price (large, prominent)
        price_label = tk.Label(
            card_frame, 
            text="₹0.00", 
            bg=self.colors['panel'], 
            fg=self.colors['text'], 
            font=('Arial', 20, 'bold')
        )
        price_label.pack(pady=(0, 5))
        self.price_labels[symbol] = price_label
        
        # Change and percentage
        change_label = tk.Label(
            card_frame, 
            text="±0.00 (0.00%)", 
            bg=self.colors['panel'], 
            fg=self.colors['neutral'], 
            font=('Arial', 11, 'bold')
        )
        change_label.pack(pady=(0, 8))
        self.change_labels[symbol] = change_label
        
        # High/Low container
        high_low_frame = tk.Frame(card_frame, bg=self.colors['panel'])
        high_low_frame.pack(fill=tk.X, pady=(0, 5))
        
        # High
        high_container = tk.Frame(high_low_frame, bg=self.colors['panel'])
        high_container.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(high_container, text="High:", bg=self.colors['panel'], 
                fg='#cccccc', font=('Arial', 9)).pack()
        high_label = tk.Label(high_container, text="₹0.00", bg=self.colors['panel'], 
                             fg=self.colors['profit'], font=('Arial', 10, 'bold'))
        high_label.pack()
        
        # Low
        low_container = tk.Frame(high_low_frame, bg=self.colors['panel'])
        low_container.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        tk.Label(low_container, text="Low:", bg=self.colors['panel'], 
                fg='#cccccc', font=('Arial', 9)).pack()
        low_label = tk.Label(low_container, text="₹0.00", bg=self.colors['panel'], 
                            fg=self.colors['loss'], font=('Arial', 10, 'bold'))
        low_label.pack()
        
        self.high_low_labels[symbol] = {'high': high_label, 'low': low_label}
        
        # Volume
        volume_label = tk.Label(
            card_frame, 
            text="Vol: 0", 
            bg=self.colors['panel'], 
            fg='#cccccc', 
            font=('Arial', 9)
        )
        volume_label.pack(pady=(5, 0))
        self.volume_labels[symbol] = volume_label
        
        # Last update time
        update_label = tk.Label(
            card_frame, 
            text="Updated: --:--:--", 
            bg=self.colors['panel'], 
            fg='#888888', 
            font=('Arial', 8)
        )
        update_label.pack(pady=(3, 0))
        
        # Store update label reference
        if not hasattr(self, 'update_labels'):
            self.update_labels = {}
        self.update_labels[symbol] = update_label
        
    def create_control_buttons(self):
        """Create control buttons for the panel"""
        control_frame = tk.Frame(self.main_frame, bg=self.colors['bg'])
        control_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Refresh button
        refresh_btn = tk.Button(
            control_frame,
            text="🔄 Refresh All",
            command=self.refresh_data,
            bg='#0088ff',
            fg='white',
            font=('Arial', 9, 'bold'),
            padx=15,
            pady=3,
            relief='raised',
            bd=2
        )
        refresh_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Auto-update toggle
        self.auto_update_var = tk.BooleanVar(value=True)
        auto_update_cb = tk.Checkbutton(
            control_frame,
            text="Auto Update",
            variable=self.auto_update_var,
            bg=self.colors['bg'],
            fg=self.colors['text'],
            selectcolor=self.colors['panel'],
            font=('Arial', 9),
            command=self.toggle_auto_update
        )
        auto_update_cb.pack(side=tk.LEFT, padx=5)
        
        # Status indicator
        self.status_label = tk.Label(
            control_frame,
            text="● Live",
            bg=self.colors['bg'],
            fg=self.colors['profit'],
            font=('Arial', 9, 'bold')
        )
        self.status_label.pack(side=tk.RIGHT, padx=5)
        
    def update_symbol_data(self, symbol: str, data: Dict):
        """Update data for a specific symbol"""
        if symbol not in self.symbols:
            return
            
        try:
            # Update internal data
            self.market_data[symbol].update(data)
            self.market_data[symbol]['last_update'] = datetime.now()
            
            # Update price
            current_price = data.get('current_price', 0)
            self.price_labels[symbol].config(text=f"₹{current_price:.2f}")
            
            # Update change with color coding
            change = data.get('change', 0)
            change_pct = data.get('change_pct', 0)
            
            if change > 0:
                change_color = self.colors['profit']
                change_text = f"+₹{change:.2f} (+{change_pct:.2f}%)"
            elif change < 0:
                change_color = self.colors['loss']
                change_text = f"₹{change:.2f} ({change_pct:.2f}%)"
            else:
                change_color = self.colors['neutral']
                change_text = f"₹{change:.2f} ({change_pct:.2f}%)"
                
            self.change_labels[symbol].config(text=change_text, fg=change_color)
            
            # Update high/low
            if 'high' in data:
                self.high_low_labels[symbol]['high'].config(text=f"₹{data['high']:.2f}")
            if 'low' in data:
                self.high_low_labels[symbol]['low'].config(text=f"₹{data['low']:.2f}")
                
            # Update volume
            volume = data.get('volume', 0)
            if volume >= 1000000:
                volume_text = f"Vol: {volume/1000000:.1f}M"
            elif volume >= 1000:
                volume_text = f"Vol: {volume/1000:.0f}K"
            else:
                volume_text = f"Vol: {volume:,}"
            self.volume_labels[symbol].config(text=volume_text)
            
            # Update timestamp
            if symbol in self.update_labels:
                update_time = self.market_data[symbol]['last_update'].strftime("%H:%M:%S")
                self.update_labels[symbol].config(text=f"Updated: {update_time}")
            
            # Call update callback if provided
            if self.update_callback:
                self.update_callback(symbol, data)
                
        except Exception as e:
            print(f"Error updating {symbol} data: {e}")
            
    def update_all_symbols(self, market_data_dict: Dict):
        """Update data for all symbols at once"""
        for symbol, data in market_data_dict.items():
            if symbol in self.symbols:
                self.update_symbol_data(symbol, data)
                
    def refresh_data(self):
        """Manual refresh of all market data"""
        self.status_label.config(text="● Refreshing...", fg=self.colors['neutral'])
        
        # Simulate data refresh (in real implementation, call API)
        import numpy as np
        
        for symbol in self.symbols:
            # Simulate price update
            current = self.market_data[symbol]['current_price']
            if current == 0:
                # Initialize with realistic values
                base_prices = {'NIFTY': 22000, 'BANKNIFTY': 48000, 'SENSEX': 72000}
                current = base_prices.get(symbol, 20000)
                
            # Random price movement
            change = np.random.normal(0, current * 0.001)  # 0.1% volatility
            new_price = max(current + change, current * 0.95)  # Prevent too large drops
            
            # Update data
            price_change = new_price - current
            change_pct = (price_change / current) * 100 if current > 0 else 0
            
            updated_data = {
                'current_price': new_price,
                'change': price_change,
                'change_pct': change_pct,
                'high': max(self.market_data[symbol]['high'], new_price),
                'low': min(self.market_data[symbol]['low'], new_price) if self.market_data[symbol]['low'] > 0 else new_price,
                'volume': np.random.randint(50000, 500000)
            }
            
            self.update_symbol_data(symbol, updated_data)
            
        self.status_label.config(text="● Live", fg=self.colors['profit'])
        
    def toggle_auto_update(self):
        """Toggle auto-update functionality"""
        if self.auto_update_var.get():
            self.status_label.config(text="● Live", fg=self.colors['profit'])
            # In real implementation, restart auto-update timer
        else:
            self.status_label.config(text="● Manual", fg=self.colors['neutral'])
            # In real implementation, stop auto-update timer
            
    def get_symbol_data(self, symbol: str) -> Dict:
        """Get current data for a symbol"""
        return self.market_data.get(symbol, {})
        
    def get_all_data(self) -> Dict:
        """Get all market data"""
        return self.market_data.copy()
        
    def set_update_callback(self, callback: Callable):
        """Set callback function for data updates"""
        self.update_callback = callback
        
    def highlight_symbol(self, symbol: str, highlight: bool = True):
        """Highlight a specific symbol (useful for showing active trades)"""
        if symbol in self.symbol_frames:
            if highlight:
                self.symbol_frames[symbol].config(bg='#4d4d4d', relief='solid', bd=3)
            else:
                self.symbol_frames[symbol].config(bg=self.colors['panel'], relief='raised', bd=2)
                
    def show_symbol_alert(self, symbol: str, message: str, alert_type: str = 'info'):
        """Show alert for specific symbol"""
        if symbol not in self.symbol_frames:
            return
            
        # Create temporary alert label
        alert_colors = {
            'info': '#0088ff',
            'warning': '#ffaa00', 
            'error': '#ff4444',
            'success': '#00ff88'
        }
        
        alert_label = tk.Label(
            self.symbol_frames[symbol],
            text=message,
            bg=alert_colors.get(alert_type, '#0088ff'),
            fg='white',
            font=('Arial', 8, 'bold'),
            padx=5,
            pady=2
        )
        alert_label.pack(pady=(5, 0))
        
        # Auto-remove after 3 seconds
        def remove_alert():
            try:
                alert_label.destroy()
            except:
                pass
                
        self.main_frame.after(3000, remove_alert)
        
    def start_auto_update(self, update_interval: int = 1000):
        """Start automatic data updates"""
        if self.auto_update_var.get():
            self.refresh_data()
            self.main_frame.after(update_interval, lambda: self.start_auto_update(update_interval))
            
    def destroy(self):
        """Clean up the panel"""
        if self.main_frame:
            self.main_frame.destroy()


# Example usage and testing
if __name__ == "__main__":
    # Test the component
    import random
    
    root = tk.Tk()
    root.title("Market Overview Test")
    root.geometry("800x300")
    root.configure(bg='#1a1a1a')
    
    # Callback function for updates
    def on_market_update(symbol, data):
        print(f"Market update for {symbol}: Price = ₹{data['current_price']:.2f}")
    
    # Create market overview panel
    symbols = ['NIFTY', 'BANKNIFTY', 'SENSEX']
    market_panel = MarketOverviewPanel(root, symbols, on_market_update)
    
    # Simulate initial data
    initial_data = {
        'NIFTY': {'current_price': 22145.75, 'change': 125.40, 'change_pct': 0.56, 'volume': 150000, 'high': 22200, 'low': 22000},
        'BANKNIFTY': {'current_price': 48570.40, 'change': -89.25, 'change_pct': -0.18, 'volume': 85000, 'high': 48700, 'low': 48400},
        'SENSEX': {'current_price': 72891.35, 'change': 245.80, 'change_pct': 0.34, 'volume': 120000, 'high': 73000, 'low': 72500}
    }
    
    market_panel.update_all_symbols(initial_data)
    
    # Start auto-updates
    market_panel.start_auto_update(2000)  # Update every 2 seconds
    
    # Test highlight feature
    def test_highlight():
        market_panel.highlight_symbol('NIFTY', True)
        root.after(2000, lambda: market_panel.highlight_symbol('NIFTY', False))
        
    def test_alert():
        market_panel.show_symbol_alert('BANKNIFTY', 'Strong Signal!', 'success')
        
    root.after(5000, test_highlight)
    root.after(8000, test_alert)
    
    root.mainloop()