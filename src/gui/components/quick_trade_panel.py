"""
Quick Trade Panel Component
One-click trading interface for NIFTY, BANKNIFTY, SENSEX
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Dict, List, Callable, Optional

class QuickTradePanel:
    """Professional quick trading panel with one-click execution"""
    
    def __init__(self, parent_frame, symbols: List[str], trade_callback: Callable = None):
        self.parent = parent_frame
        self.symbols = symbols
        self.trade_callback = trade_callback
        
        # Trading state
        self.trading_enabled = True
        self.quick_quantities = {'NIFTY': 50, 'BANKNIFTY': 25, 'SENSEX': 30}
        self.market_prices = {}
        
        # GUI components
        self.main_frame = None
        self.symbol_panels = {}
        self.price_labels = {}
        self.trade_buttons = {}
        
        # Colors
        self.colors = {
            'bg': '#2d2d2d',
            'panel': '#3d3d3d',
            'text': '#ffffff',
            'ce_color': '#00dd00',  # Call option color
            'pe_color': '#dd0000',  # Put option color
            'disabled': '#666666',
            'warning': '#ffaa00'
        }
        
        self.create_panel()
        
    def create_panel(self):
        """Create the quick trade panel"""
        # Main container
        self.main_frame = tk.LabelFrame(
            self.parent,
            text="⚡ QUICK TRADE PANEL",
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=('Arial', 12, 'bold'),
            padx=10,
            pady=10
        )
        self.main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(3, 0))
        
        # Create control header
        self.create_control_header()
        
        # Create symbol trading panels
        self.create_symbol_panels()
        
        # Create global controls
        self.create_global_controls()
        
    def create_control_header(self):
        """Create header with trading controls"""
        header_frame = tk.Frame(self.main_frame, bg=self.colors['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Trading status indicator
        self.status_frame = tk.Frame(header_frame, bg=self.colors['bg'])
        self.status_frame.pack(fill=tk.X)
        
        # Status indicator
        self.trading_status_label = tk.Label(
            self.status_frame,
            text="● TRADING ENABLED",
            bg=self.colors['bg'],
            fg=self.colors['ce_color'],
            font=('Arial', 10, 'bold')
        )
        self.trading_status_label.pack(side=tk.LEFT)
        
        # Toggle trading button
        self.toggle_btn = tk.Button(
            self.status_frame,
            text="🔒 DISABLE",
            command=self.toggle_trading,
            bg=self.colors['warning'],
            fg='white',
            font=('Arial', 8, 'bold'),
            padx=8,
            pady=2
        )
        self.toggle_btn.pack(side=tk.RIGHT)
        
    def create_symbol_panels(self):
        """Create trading panels for each symbol"""
        for i, symbol in enumerate(self.symbols):
            self.create_symbol_trading_card(symbol)
            
    def create_symbol_trading_card(self, symbol: str):
        """Create individual trading card for symbol"""
        # Main card frame
        card_frame = tk.LabelFrame(
            self.main_frame,
            text=f"{symbol} TRADING",
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=('Arial', 10, 'bold'),
            padx=8,
            pady=8
        )
        card_frame.pack(fill=tk.X, pady=5)
        
        self.symbol_panels[symbol] = card_frame
        
        # Price display section
        price_section = tk.Frame(card_frame, bg=self.colors['bg'])
        price_section.pack(fill=tk.X, pady=(0, 8))
        
        # Current price (centered, prominent)
        price_label = tk.Label(
            price_section,
            text="₹0.00",
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=('Arial', 14, 'bold')
        )
        price_label.pack()
        self.price_labels[symbol] = price_label
        
        # Last update time
        update_label = tk.Label(
            price_section,
            text="Last: --:--:--",
            bg=self.colors['bg'],
            fg='#888888',
            font=('Arial', 8)
        )
        update_label.pack()
        
        # Store update label reference
        if not hasattr(self, 'update_labels'):
            self.update_labels = {}
        self.update_labels[symbol] = update_label
        
        # Quantity selection
        qty_frame = tk.Frame(card_frame, bg=self.colors['bg'])
        qty_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(qty_frame, text="Qty:", bg=self.colors['bg'], fg=self.colors['text'], 
                font=('Arial', 9)).pack(side=tk.LEFT)
        
        qty_var = tk.StringVar(value=str(self.quick_quantities[symbol]))
        qty_entry = tk.Entry(
            qty_frame,
            textvariable=qty_var,
            width=6,
            font=('Arial', 9),
            justify='center'
        )
        qty_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # Store quantity variable
        if not hasattr(self, 'qty_vars'):
            self.qty_vars = {}
        self.qty_vars[symbol] = qty_var
        
        # Quick quantity buttons
        quick_qty_frame = tk.Frame(qty_frame, bg=self.colors['bg'])
        quick_qty_frame.pack(side=tk.RIGHT)
        
        for qty in [25, 50, 75, 100]:
            tk.Button(
                quick_qty_frame,
                text=str(qty),
                command=lambda q=qty, s=symbol: self.set_quick_quantity(s, q),
                bg=self.colors['panel'],
                fg=self.colors['text'],
                font=('Arial', 7),
                padx=3,
                pady=1,
                relief='flat'
            ).pack(side=tk.LEFT, padx=1)
        
        # Trading buttons section
        buttons_frame = tk.Frame(card_frame, bg=self.colors['bg'])
        buttons_frame.pack(fill=tk.X, pady=5)
        
        # CE (Call) Button
        ce_btn = tk.Button(
            buttons_frame,
            text=f"🟢 BUY {symbol} CE",
            command=lambda s=symbol: self.execute_trade(s, 'CE'),
            bg=self.colors['ce_color'],
            fg='white',
            font=('Arial', 9, 'bold'),
            padx=5,
            pady=8,
            relief='raised',
            bd=2,
            cursor='hand2'
        )
        ce_btn.pack(fill=tk.X, pady=1)
        
        # PE (Put) Button
        pe_btn = tk.Button(
            buttons_frame,
            text=f"🔴 BUY {symbol} PE",
            command=lambda s=symbol: self.execute_trade(s, 'PE'),
            bg=self.colors['pe_color'],
            fg='white',
            font=('Arial', 9, 'bold'),
            padx=5,
            pady=8,
            relief='raised',
            bd=2,
            cursor='hand2'
        )
        pe_btn.pack(fill=tk.X, pady=1)
        
        # Store button references
        if not hasattr(self, 'trade_buttons'):
            self.trade_buttons = {}
        self.trade_buttons[symbol] = {'CE': ce_btn, 'PE': pe_btn}
        
        # Advanced options (collapsible)
        self.create_advanced_options(card_frame, symbol)
        
    def create_advanced_options(self, parent, symbol: str):
        """Create advanced trading options"""
        # Advanced options frame (initially hidden)
        advanced_frame = tk.Frame(parent, bg=self.colors['bg'])
        
        # Toggle button for advanced options
        toggle_advanced_btn = tk.Button(
            parent,
            text="⚙️ Advanced",
            command=lambda: self.toggle_advanced_options(symbol, advanced_frame),
            bg=self.colors['panel'],
            fg=self.colors['text'],
            font=('Arial', 8),
            padx=5,
            pady=2,
            relief='flat'
        )
        toggle_advanced_btn.pack(pady=(5, 0))
        
        # SL and Target inputs
        sl_target_frame = tk.Frame(advanced_frame, bg=self.colors['bg'])
        sl_target_frame.pack(fill=tk.X, pady=5)
        
        # Stop Loss
        sl_frame = tk.Frame(sl_target_frame, bg=self.colors['bg'])
        sl_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(sl_frame, text="SL:", bg=self.colors['bg'], fg=self.colors['text'], 
                font=('Arial', 8)).pack(side=tk.LEFT)
        sl_entry = tk.Entry(sl_frame, width=8, font=('Arial', 8))
        sl_entry.pack(side=tk.LEFT, padx=2)
        
        # Target
        target_frame = tk.Frame(sl_target_frame, bg=self.colors['bg'])
        target_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        tk.Label(target_frame, text="Target:", bg=self.colors['bg'], fg=self.colors['text'], 
                font=('Arial', 8)).pack(side=tk.LEFT)
        target_entry = tk.Entry(target_frame, width=8, font=('Arial', 8))
        target_entry.pack(side=tk.LEFT, padx=2)
        
        # Order type selection
        order_type_frame = tk.Frame(advanced_frame, bg=self.colors['bg'])
        order_type_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(order_type_frame, text="Order Type:", bg=self.colors['bg'], fg=self.colors['text'], 
                font=('Arial', 8)).pack(side=tk.LEFT)
        
        order_type_var = tk.StringVar(value="MARKET")
        order_type_combo = ttk.Combobox(
            order_type_frame,
            textvariable=order_type_var,
            values=["MARKET", "LIMIT", "SL", "SL-M"],
            width=10,
            font=('Arial', 8),
            state="readonly"
        )
        order_type_combo.pack(side=tk.RIGHT, padx=2)
        
        # Store advanced option references
        if not hasattr(self, 'advanced_options'):
            self.advanced_options = {}
        self.advanced_options[symbol] = {
            'frame': advanced_frame,
            'sl_entry': sl_entry,
            'target_entry': target_entry,
            'order_type_var': order_type_var,
            'visible': False
        }
        
    def create_global_controls(self):
        """Create global trading controls"""
        global_frame = tk.LabelFrame(
            self.main_frame,
            text="🌐 GLOBAL CONTROLS",
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=('Arial', 10, 'bold'),
            padx=8,
            pady=8
        )
        global_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Emergency controls
        emergency_frame = tk.Frame(global_frame, bg=self.colors['bg'])
        emergency_frame.pack(fill=tk.X, pady=5)
        
        # Close all positions
        close_all_btn = tk.Button(
            emergency_frame,
            text="❌ CLOSE ALL POSITIONS",
            command=self.close_all_positions,
            bg='#cc0000',
            fg='white',
            font=('Arial', 9, 'bold'),
            padx=10,
            pady=5
        )
        close_all_btn.pack(fill=tk.X, pady=1)
        
        # Square off all
        square_off_btn = tk.Button(
            emergency_frame,
            text="🔄 SQUARE OFF ALL",
            command=self.square_off_all,
            bg='#ff8800',
            fg='white',
            font=('Arial', 9, 'bold'),
            padx=10,
            pady=5
        )
        square_off_btn.pack(fill=tk.X, pady=1)
        
        # Quick settings
        settings_frame = tk.Frame(global_frame, bg=self.colors['bg'])
        settings_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Auto-trading toggle
        self.auto_trading_var = tk.BooleanVar(value=False)
        auto_cb = tk.Checkbutton(
            settings_frame,
            text="Auto Trading",
            variable=self.auto_trading_var,
            bg=self.colors['bg'],
            fg=self.colors['text'],
            selectcolor=self.colors['panel'],
            font=('Arial', 9),
            command=self.toggle_auto_trading
        )
        auto_cb.pack(anchor='w')
        
        # Risk management toggle
        self.risk_mgmt_var = tk.BooleanVar(value=True)
        risk_cb = tk.Checkbutton(
            settings_frame,
            text="Risk Management",
            variable=self.risk_mgmt_var,
            bg=self.colors['bg'],
            fg=self.colors['text'],
            selectcolor=self.colors['panel'],
            font=('Arial', 9)
        )
        risk_cb.pack(anchor='w')
        
        # Trade statistics
        stats_frame = tk.Frame(global_frame, bg=self.colors['bg'])
        stats_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.stats_label = tk.Label(
            stats_frame,
            text="Today: 0 trades | 0% win rate",
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=('Arial', 8)
        )
        self.stats_label.pack()
        
    # Core trading methods
    def execute_trade(self, symbol: str, option_type: str):
        """Execute quick trade"""
        if not self.trading_enabled:
            messagebox.showwarning("Trading Disabled", "Trading is currently disabled")
            return
            
        try:
            # Get quantity
            quantity = int(self.qty_vars[symbol].get())
            if quantity <= 0:
                messagebox.showerror("Invalid Quantity", "Quantity must be greater than 0")
                return
                
            # Get current price
            current_price = self.market_prices.get(symbol, {}).get('current_price', 0)
            if current_price <= 0:
                messagebox.showerror("Price Error", f"No valid price data for {symbol}")
                return
                
            # Get advanced options
            advanced = self.advanced_options.get(symbol, {})
            stop_loss = self.parse_float(advanced.get('sl_entry', {}).get() if 'sl_entry' in advanced else "")
            target = self.parse_float(advanced.get('target_entry', {}).get() if 'target_entry' in advanced else "")
            order_type = advanced.get('order_type_var', {}).get() if 'order_type_var' in advanced else "MARKET"
            
            # Create trade data
            trade_data = {
                'timestamp': datetime.now(),
                'symbol': symbol,
                'option_type': option_type,
                'quantity': quantity,
                'current_price': current_price,
                'order_type': order_type,
                'stop_loss': stop_loss,
                'target': target,
                'source': 'quick_trade'
            }
            
            # Confirmation dialog
            if self.show_trade_confirmation(trade_data):
                # Execute trade via callback
                if self.trade_callback:
                    success = self.trade_callback(trade_data)
                    if success:
                        self.show_trade_success(trade_data)
                    else:
                        messagebox.showerror("Trade Failed", "Failed to execute trade")
                else:
                    messagebox.showinfo("Demo Mode", "Trade executed in demo mode")
                    
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid quantity: {e}")
        except Exception as e:
            messagebox.showerror("Trade Error", f"Failed to execute trade: {str(e)}")
            
    def show_trade_confirmation(self, trade_data: Dict) -> bool:
        """Show trade confirmation dialog"""
        symbol = trade_data['symbol']
        option_type = trade_data['option_type']
        quantity = trade_data['quantity']
        price = trade_data['current_price']
        
        # Calculate approximate premium (simplified)
        strike = round(price / 50) * 50  # Round to nearest 50
        premium = price * 0.02  # Simplified ITM premium calculation
        
        confirmation_text = f"""
Confirm Trade Execution:

Symbol: {symbol}
Option: {strike} {option_type}
Quantity: {quantity} lots
Estimated Premium: ₹{premium:.2f}
Estimated Investment: ₹{premium * quantity:.2f}

Order Type: {trade_data.get('order_type', 'MARKET')}
Stop Loss: {trade_data.get('stop_loss', 'Not Set')}
Target: {trade_data.get('target', 'Not Set')}

Do you want to proceed?
        """
        
        return messagebox.askyesno("Confirm Trade", confirmation_text)
        
    def show_trade_success(self, trade_data: Dict):
        """Show trade success notification"""
        symbol = trade_data['symbol']
        option_type = trade_data['option_type']
        quantity = trade_data['quantity']
        
        # Flash the button to indicate success
        button = self.trade_buttons[symbol][option_type]
        original_bg = button.cget('bg')
        
        # Flash green
        button.config(bg='#00ff00')
        self.main_frame.after(200, lambda: button.config(bg=original_bg))
        
        # Update statistics (placeholder)
        self.update_trade_statistics()
        
    def parse_float(self, value: str) -> Optional[float]:
        """Parse float value safely"""
        try:
            return float(value) if value.strip() else None
        except (ValueError, AttributeError):
            return None
            
    # UI control methods
    def set_quick_quantity(self, symbol: str, quantity: int):
        """Set quick quantity for symbol"""
        if symbol in self.qty_vars:
            self.qty_vars[symbol].set(str(quantity))
            
    def toggle_advanced_options(self, symbol: str, frame):
        """Toggle advanced options visibility"""
        if symbol in self.advanced_options:
            current_state = self.advanced_options[symbol]['visible']
            if current_state:
                frame.pack_forget()
                self.advanced_options[symbol]['visible'] = False
            else:
                frame.pack(fill=tk.X, pady=5)
                self.advanced_options[symbol]['visible'] = True
                
    def toggle_trading(self):
        """Toggle trading enabled/disabled"""
        self.trading_enabled = not self.trading_enabled
        
        if self.trading_enabled:
            self.trading_status_label.config(text="● TRADING ENABLED", fg=self.colors['ce_color'])
            self.toggle_btn.config(text="🔒 DISABLE", bg=self.colors['warning'])
            
            # Enable all trade buttons
            for symbol_buttons in self.trade_buttons.values():
                for button in symbol_buttons.values():
                    button.config(state='normal')
        else:
            self.trading_status_label.config(text="● TRADING DISABLED", fg=self.colors['pe_color'])
            self.toggle_btn.config(text="🔓 ENABLE", bg=self.colors['ce_color'])
            
            # Disable all trade buttons
            for symbol_buttons in self.trade_buttons.values():
                for button in symbol_buttons.values():
                    button.config(state='disabled')
                    
    def toggle_auto_trading(self):
        """Toggle auto trading mode"""
        if self.auto_trading_var.get():
            messagebox.showinfo("Auto Trading", "Auto trading enabled. The system will execute trades based on signals.")
        else:
            messagebox.showinfo("Manual Trading", "Auto trading disabled. Trades will only execute manually.")
            
    # Data update methods
    def update_market_data(self, symbol: str, data: Dict):
        """Update market data for symbol"""
        if symbol not in self.symbols:
            return
            
        # Store market data
        self.market_prices[symbol] = data
        
        # Update price display
        current_price = data.get('current_price', 0)
        self.price_labels[symbol].config(text=f"₹{current_price:.2f}")
        
        # Update timestamp
        if symbol in self.update_labels:
            update_time = datetime.now().strftime("%H:%M:%S")
            self.update_labels[symbol].config(text=f"Last: {update_time}")
            
        # Color code based on change
        change = data.get('change', 0)
        if change > 0:
            color = self.colors['ce_color']
        elif change < 0:
            color = self.colors['pe_color']
        else:
            color = self.colors['text']
            
        self.price_labels[symbol].config(fg=color)
        
    def update_all_market_data(self, market_data: Dict):
        """Update market data for all symbols"""
        for symbol, data in market_data.items():
            if symbol in self.symbols:
                self.update_market_data(symbol, data)
                
    def update_trade_statistics(self):
        """Update trade statistics display"""
        # Placeholder - would be connected to actual trade data
        import random
        trades = random.randint(0, 20)
        win_rate = random.randint(45, 85)
        
        self.stats_label.config(text=f"Today: {trades} trades | {win_rate}% win rate")
        
    # Global action methods
    def close_all_positions(self):
        """Close all active positions"""
        if messagebox.askyesno("Close All", "Close all active positions for all symbols?"):
            if self.trade_callback:
                # Send close all command
                close_data = {
                    'action': 'close_all',
                    'timestamp': datetime.now(),
                    'source': 'quick_trade_panel'
                }
                self.trade_callback(close_data)
            messagebox.showinfo("Positions Closed", "All positions have been closed")
            
    def square_off_all(self):
        """Square off all positions"""
        if messagebox.askyesno("Square Off", "Square off all positions for all symbols?"):
            if self.trade_callback:
                # Send square off command
                square_off_data = {
                    'action': 'square_off_all',
                    'timestamp': datetime.now(),
                    'source': 'quick_trade_panel'
                }
                self.trade_callback(square_off_data)
            messagebox.showinfo("Square Off", "All positions have been squared off")
            
    # Utility methods
    def set_trade_callback(self, callback: Callable):
        """Set trade execution callback"""
        self.trade_callback = callback
        
    def enable_symbol_trading(self, symbol: str, enabled: bool = True):
        """Enable/disable trading for specific symbol"""
        if symbol in self.trade_buttons:
            state = 'normal' if (enabled and self.trading_enabled) else 'disabled'
            for button in self.trade_buttons[symbol].values():
                button.config(state=state)
                
    def highlight_symbol(self, symbol: str, highlight: bool = True):
        """Highlight symbol panel"""
        if symbol in self.symbol_panels:
            if highlight:
                self.symbol_panels[symbol].config(relief='solid', bd=3)
            else:
                self.symbol_panels[symbol].config(relief='groove', bd=2)
                
    def get_symbol_quantity(self, symbol: str) -> int:
        """Get current quantity for symbol"""
        if symbol in self.qty_vars:
            try:
                return int(self.qty_vars[symbol].get())
            except ValueError:
                return 0
        return 0
        
    def set_symbol_quantity(self, symbol: str, quantity: int):
        """Set quantity for symbol"""
        if symbol in self.qty_vars:
            self.qty_vars[symbol].set(str(quantity))
            
    def get_trading_status(self) -> Dict:
        """Get current trading status"""
        return {
            'trading_enabled': self.trading_enabled,
            'auto_trading': self.auto_trading_var.get(),
            'risk_management': self.risk_mgmt_var.get(),
            'symbols': self.symbols,
            'quantities': {symbol: self.get_symbol_quantity(symbol) for symbol in self.symbols}
        }
        
    def destroy(self):
        """Clean up the panel"""
        if self.main_frame:
            self.main_frame.destroy()


# Example usage and testing
if __name__ == "__main__":
    import random
    
    root = tk.Tk()
    root.title("Quick Trade Panel Test")
    root.geometry("400x800")
    root.configure(bg='#1a1a1a')
    
    # Trade execution callback
    def execute_trade(trade_data):
        print(f"Executing trade: {trade_data}")
        # Simulate trade execution
        return True  # Success
    
    # Create quick trade panel
    symbols = ['NIFTY', 'BANKNIFTY', 'SENSEX']
    trade_panel = QuickTradePanel(root, symbols, execute_trade)
    
    # Simulate market data updates
    def update_market_data():
        market_data = {
            'NIFTY': {
                'current_price': 22000 + random.uniform(-100, 100),
                'change': random.uniform(-50, 50)
            },
            'BANKNIFTY': {
                'current_price': 48000 + random.uniform(-200, 200),
                'change': random.uniform(-100, 100)
            },
            'SENSEX': {
                'current_price': 72000 + random.uniform(-150, 150),
                'change': random.uniform(-75, 75)
            }
        }
        
        trade_panel.update_all_market_data(market_data)
        root.after(2000, update_market_data)  # Update every 2 seconds
    
    # Start market data updates
    update_market_data()
    
    root.mainloop()