"""
Charts Panel Component
Multi-symbol real-time charting with technical indicators
"""

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Optional
import threading
import time

class ChartsPanel:
    """Professional multi-symbol charts panel with technical indicators"""
    
    def __init__(self, parent_frame, symbols: List[str], data_callback: Callable = None):
        self.parent = parent_frame
        self.symbols = symbols
        self.data_callback = data_callback
        
        # Chart data storage
        self.chart_data = {}
        for symbol in symbols:
            self.chart_data[symbol] = pd.DataFrame()
        
        # Chart configuration
        self.chart_config = {
            'timeframe': '1m',
            'show_ema': True,
            'show_rsi': True,
            'show_volume': True,
            'show_signals': True,
            'bars_count': 100,
            'update_interval': 1000  # ms
        }
        
        # GUI components
        self.main_frame = None
        self.chart_notebook = None
        self.chart_figures = {}
        self.chart_axes = {}
        self.chart_canvases = {}
        self.chart_lines = {}
        
        # Colors and style
        self.colors = {
            'bg': '#1a1a1a',
            'panel': '#2d2d2d',
            'text': '#ffffff',
            'grid': '#444444',
            'up_candle': '#00ff88',
            'down_candle': '#ff4444',
            'ema_fast': '#00ddff',
            'ema_slow': '#ffaa00',
            'volume': '#666666',
            'rsi_line': '#ffff00',
            'signal_buy': '#00ff00',
            'signal_sell': '#ff0000'
        }
        
        self.create_panel()
        
    def create_panel(self):
        """Create the main charts panel"""
        # Main container
        self.main_frame = tk.LabelFrame(
            self.parent,
            text="📈 LIVE CHARTS - Multi-Symbol Technical Analysis",
            bg=self.colors['panel'],
            fg=self.colors['text'],
            font=('Arial', 12, 'bold'),
            padx=5,
            pady=5
        )
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create chart controls
        self.create_chart_controls()
        
        # Create chart notebook
        self.create_chart_notebook()
        
        # Create charts for each symbol
        self.create_symbol_charts()
        
        # Initialize chart data
        self.initialize_chart_data()
        
    def create_chart_controls(self):
        """Create chart control toolbar"""
        controls_frame = tk.Frame(self.main_frame, bg=self.colors['panel'])
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Left side - Chart controls
        left_controls = tk.Frame(controls_frame, bg=self.colors['panel'])
        left_controls.pack(side=tk.LEFT)
        
        # Timeframe selection
        tk.Label(left_controls, text="Timeframe:", bg=self.colors['panel'], 
                fg=self.colors['text'], font=('Arial', 9)).pack(side=tk.LEFT, padx=5)
        
        self.timeframe_var = tk.StringVar(value=self.chart_config['timeframe'])
        timeframe_combo = ttk.Combobox(
            left_controls,
            textvariable=self.timeframe_var,
            values=['1m', '3m', '5m', '15m', '30m', '1h'],
            width=8,
            state="readonly"
        )
        timeframe_combo.pack(side=tk.LEFT, padx=2)
        timeframe_combo.bind("<<ComboboxSelected>>", self.change_timeframe)
        
        # Indicator toggles
        indicator_frame = tk.Frame(left_controls, bg=self.colors['panel'])
        indicator_frame.pack(side=tk.LEFT, padx=15)
        
        # EMA toggle
        self.ema_var = tk.BooleanVar(value=self.chart_config['show_ema'])
        ema_cb = tk.Checkbutton(
            indicator_frame, text="EMA", variable=self.ema_var,
            bg=self.colors['panel'], fg=self.colors['text'],
            selectcolor=self.colors['bg'], font=('Arial', 8),
            command=self.toggle_indicators
        )
        ema_cb.pack(side=tk.LEFT, padx=2)
        
        # RSI toggle
        self.rsi_var = tk.BooleanVar(value=self.chart_config['show_rsi'])
        rsi_cb = tk.Checkbutton(
            indicator_frame, text="RSI", variable=self.rsi_var,
            bg=self.colors['panel'], fg=self.colors['text'],
            selectcolor=self.colors['bg'], font=('Arial', 8),
            command=self.toggle_indicators
        )
        rsi_cb.pack(side=tk.LEFT, padx=2)
        
        # Volume toggle
        self.volume_var = tk.BooleanVar(value=self.chart_config['show_volume'])
        volume_cb = tk.Checkbutton(
            indicator_frame, text="Volume", variable=self.volume_var,
            bg=self.colors['panel'], fg=self.colors['text'],
            selectcolor=self.colors['bg'], font=('Arial', 8),
            command=self.toggle_indicators
        )
        volume_cb.pack(side=tk.LEFT, padx=2)
        
        # Signals toggle
        self.signals_var = tk.BooleanVar(value=self.chart_config['show_signals'])
        signals_cb = tk.Checkbutton(
            indicator_frame, text="Signals", variable=self.signals_var,
            bg=self.colors['panel'], fg=self.colors['text'],
            selectcolor=self.colors['bg'], font=('Arial', 8),
            command=self.toggle_indicators
        )
        signals_cb.pack(side=tk.LEFT, padx=2)
        
        # Right side - Chart actions
        right_controls = tk.Frame(controls_frame, bg=self.colors['panel'])
        right_controls.pack(side=tk.RIGHT)
        
        # Action buttons
        buttons = [
            ("🔄 Refresh", self.refresh_charts, '#0088ff'),
            ("💾 Save", self.save_charts, '#666666'),
            ("🔍 Reset Zoom", self.reset_zoom, '#666666'),
            ("⚙️ Settings", self.chart_settings, '#666666')
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(
                right_controls, text=text, command=command,
                bg=color, fg='white', font=('Arial', 8, 'bold'),
                padx=8, pady=2, relief='raised', bd=1
            )
            btn.pack(side=tk.LEFT, padx=2)
            
    def create_chart_notebook(self):
        """Create notebook for multi-symbol charts"""
        self.chart_notebook = ttk.Notebook(self.main_frame)
        self.chart_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure notebook style
        style = ttk.Style()
        style.configure('TNotebook', background=self.colors['panel'])
        style.configure('TNotebook.Tab', padding=[15, 8])
        
    def create_symbol_charts(self):
        """Create charts for each symbol"""
        for symbol in self.symbols:
            self.create_symbol_chart(symbol)
            
    def create_symbol_chart(self, symbol: str):
        """Create chart for specific symbol"""
        # Create frame for this symbol's chart
        symbol_frame = tk.Frame(self.chart_notebook, bg=self.colors['bg'])
        self.chart_notebook.add(symbol_frame, text=f"{symbol} Chart")
        
        # Create matplotlib figure
        fig = plt.figure(figsize=(12, 8), facecolor=self.colors['bg'])
        
        # Create subplots with proper ratios
        gs = fig.add_gridspec(4, 1, height_ratios=[3, 1, 1, 0.5], hspace=0.1)
        
        # Price chart (main)
        price_ax = fig.add_subplot(gs[0])
        price_ax.set_facecolor(self.colors['bg'])
        price_ax.tick_params(colors=self.colors['text'], labelsize=8)
        price_ax.grid(True, alpha=0.3, color=self.colors['grid'])
        price_ax.set_title(f'{symbol} - {self.chart_config["timeframe"]} Chart', 
                          color=self.colors['text'], fontsize=12, pad=15)
        
        # RSI subplot
        rsi_ax = fig.add_subplot(gs[1], sharex=price_ax)
        rsi_ax.set_facecolor(self.colors['bg'])
        rsi_ax.tick_params(colors=self.colors['text'], labelsize=8)
        rsi_ax.grid(True, alpha=0.3, color=self.colors['grid'])
        rsi_ax.set_ylabel('RSI', color=self.colors['text'], fontsize=9)
        rsi_ax.set_ylim(0, 100)
        rsi_ax.axhline(y=70, color=self.colors['down_candle'], linestyle='--', alpha=0.7)
        rsi_ax.axhline(y=30, color=self.colors['up_candle'], linestyle='--', alpha=0.7)
        rsi_ax.axhline(y=50, color=self.colors['grid'], linestyle='-', alpha=0.5)
        
        # Volume subplot
        volume_ax = fig.add_subplot(gs[2], sharex=price_ax)
        volume_ax.set_facecolor(self.colors['bg'])
        volume_ax.tick_params(colors=self.colors['text'], labelsize=8)
        volume_ax.grid(True, alpha=0.3, color=self.colors['grid'])
        volume_ax.set_ylabel('Volume', color=self.colors['text'], fontsize=9)
        
        # Info subplot (for statistics)
        info_ax = fig.add_subplot(gs[3])
        info_ax.set_facecolor(self.colors['bg'])
        info_ax.axis('off')  # Hide axes for info panel
        
        # Store references
        self.chart_figures[symbol] = fig
        self.chart_axes[symbol] = {
            'price': price_ax,
            'rsi': rsi_ax,
            'volume': volume_ax,
            'info': info_ax
        }
        
        # Initialize line containers
        self.chart_lines[symbol] = {
            'price_line': None,
            'ema_fast': None,
            'ema_slow': None,
            'rsi_line': None,
            'volume_bars': None,
            'buy_signals': [],
            'sell_signals': []
        }
        
        # Embed chart in tkinter
        canvas = FigureCanvasTkAgg(fig, symbol_frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.chart_canvases[symbol] = canvas
        
        # Add chart toolbar
        self.create_symbol_toolbar(symbol_frame, symbol)
        
    def create_symbol_toolbar(self, parent, symbol: str):
        """Create toolbar for individual symbol chart"""
        toolbar_frame = tk.Frame(parent, bg=self.colors['panel'], height=30)
        toolbar_frame.pack(fill=tk.X, side=tk.BOTTOM)
        toolbar_frame.pack_propagate(False)
        
        # Current price display
        self.current_price_label = tk.Label(
            toolbar_frame, text=f"{symbol}: ₹0.00",
            bg=self.colors['panel'], fg=self.colors['text'],
            font=('Arial', 10, 'bold')
        )
        self.current_price_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Store label reference
        if not hasattr(self, 'price_labels'):
            self.price_labels = {}
        self.price_labels[symbol] = self.current_price_label
        
        # Chart statistics
        stats_label = tk.Label(
            toolbar_frame, text="Change: 0.00% | Volume: 0 | RSI: 50",
            bg=self.colors['panel'], fg='#cccccc',
            font=('Arial', 9)
        )
        stats_label.pack(side=tk.LEFT, padx=20, pady=5)
        
        if not hasattr(self, 'stats_labels'):
            self.stats_labels = {}
        self.stats_labels[symbol] = stats_label
        
        # Last update time
        update_label = tk.Label(
            toolbar_frame, text="Updated: --:--:--",
            bg=self.colors['panel'], fg='#888888',
            font=('Arial', 8)
        )
        update_label.pack(side=tk.RIGHT, padx=10, pady=5)
        
        if not hasattr(self, 'chart_update_labels'):
            self.chart_update_labels = {}
        self.chart_update_labels[symbol] = update_label
        
    def initialize_chart_data(self):
        """Initialize chart data for all symbols"""
        for symbol in self.symbols:
            # Generate initial sample data
            self.generate_sample_data(symbol, bars=self.chart_config['bars_count'])
            
            # Update chart
            self.update_symbol_chart(symbol)
            
    def generate_sample_data(self, symbol: str, bars: int = 100):
        """Generate sample OHLCV data for symbol"""
        # Base prices for different symbols
        base_prices = {'NIFTY': 22000, 'BANKNIFTY': 48000, 'SENSEX': 72000}
        base_price = base_prices.get(symbol, 20000)
        
        # Generate timestamps
        now = datetime.now()
        timestamps = [now - timedelta(minutes=i) for i in range(bars, 0, -1)]
        
        # Generate price data
        np.random.seed(42)  # For consistent data
        
        data = []
        current_price = base_price
        
        for i, timestamp in enumerate(timestamps):
            # Random walk
            change = np.random.normal(0, base_price * 0.001)  # 0.1% volatility
            current_price = max(current_price + change, base_price * 0.9)
            
            # Generate OHLC
            open_price = current_price
            high = open_price + abs(np.random.normal(0, base_price * 0.002))
            low = open_price - abs(np.random.normal(0, base_price * 0.002))
            close = open_price + np.random.normal(0, base_price * 0.0015)
            
            # Ensure OHLC relationship
            high = max(high, open_price, close)
            low = min(low, open_price, close)
            
            volume = np.random.randint(10000, 100000)
            
            data.append({
                'timestamp': timestamp,
                'open': open_price,
                'high': high,
                'low': low,
                'close': close,
                'volume': volume
            })
            
            current_price = close
            
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Calculate technical indicators
        df = self.calculate_indicators(df)
        
        # Store data
        self.chart_data[symbol] = df
        
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators"""
        if len(df) < 21:
            return df
            
        # EMA calculations
        df['ema_9'] = df['close'].ewm(span=9).mean()
        df['ema_21'] = df['close'].ewm(span=21).mean()
        
        # RSI calculation
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD calculation
        ema_12 = df['close'].ewm(span=12).mean()
        ema_26 = df['close'].ewm(span=26).mean()
        df['macd'] = ema_12 - ema_26
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        
        # Generate trading signals
        df['signal'] = 0
        
        # EMA crossover signals
        df['ema_cross'] = np.where(
            (df['ema_9'] > df['ema_21']) & (df['ema_9'].shift(1) <= df['ema_21'].shift(1)),
            1,  # Buy signal
            np.where(
                (df['ema_9'] < df['ema_21']) & (df['ema_9'].shift(1) >= df['ema_21'].shift(1)),
                -1,  # Sell signal
                0
            )
        )
        
        # RSI signals
        df['rsi_signal'] = np.where(
            (df['rsi'] > 30) & (df['rsi'].shift(1) <= 30),
            1,  # Buy signal (oversold recovery)
            np.where(
                (df['rsi'] < 70) & (df['rsi'].shift(1) >= 70),
                -1,  # Sell signal (overbought correction)
                0
            )
        )
        
        # Combined signals
        df.loc[(df['ema_cross'] == 1) & (df['rsi'] > 30) & (df['rsi'] < 70), 'signal'] = 1
        df.loc[(df['ema_cross'] == -1) & (df['rsi'] > 30) & (df['rsi'] < 70), 'signal'] = -1
        
        return df
        
    def update_symbol_chart(self, symbol: str):
        """Update chart for specific symbol"""
        if symbol not in self.chart_data or self.chart_data[symbol].empty:
            return
            
        try:
            df = self.chart_data[symbol].tail(self.chart_config['bars_count'])
            
            if len(df) < 10:
                return
                
            # Get chart components
            fig = self.chart_figures[symbol]
            axes = self.chart_axes[symbol]
            lines = self.chart_lines[symbol]
            
            # Clear previous plots
            axes['price'].clear()
            axes['rsi'].clear()
            axes['volume'].clear()
            axes['info'].clear()
            
            # Reconfigure axes
            self.configure_axes(axes, symbol)
            
            # Plot price data (candlestick-style line)
            x_data = range(len(df))
            
            # Price line
            axes['price'].plot(x_data, df['close'], color=self.colors['text'], 
                             linewidth=1.5, label='Price')
            
            # EMA lines
            if self.chart_config['show_ema'] and 'ema_9' in df.columns:
                axes['price'].plot(x_data, df['ema_9'], color=self.colors['ema_fast'], 
                                 linewidth=1, label='EMA 9', alpha=0.8)
                axes['price'].plot(x_data, df['ema_21'], color=self.colors['ema_slow'], 
                                 linewidth=1, label='EMA 21', alpha=0.8)
            
            # Trading signals
            if self.chart_config['show_signals'] and 'signal' in df.columns:
                buy_signals = df[df['signal'] == 1]
                sell_signals = df[df['signal'] == -1]
                
                if not buy_signals.empty:
                    buy_indices = [df.index.get_loc(idx) for idx in buy_signals.index if idx in df.index]
                    if buy_indices:
                        axes['price'].scatter([x_data[i] for i in buy_indices], 
                                            buy_signals['close'], 
                                            color=self.colors['signal_buy'], 
                                            marker='^', s=60, zorder=5, label='Buy Signal')
                
                if not sell_signals.empty:
                    sell_indices = [df.index.get_loc(idx) for idx in sell_signals.index if idx in df.index]
                    if sell_indices:
                        axes['price'].scatter([x_data[i] for i in sell_indices], 
                                            sell_signals['close'],
                                            color=self.colors['signal_sell'], 
                                            marker='v', s=60, zorder=5, label='Sell Signal')
            
            # RSI plot
            if self.chart_config['show_rsi'] and 'rsi' in df.columns:
                axes['rsi'].plot(x_data, df['rsi'], color=self.colors['rsi_line'], 
                               linewidth=1.5, label='RSI')
                axes['rsi'].fill_between(x_data, df['rsi'], 50, alpha=0.3, 
                                       color=self.colors['rsi_line'])
            
            # Volume plot
            if self.chart_config['show_volume']:
                colors = [self.colors['up_candle'] if c >= o else self.colors['down_candle'] 
                         for c, o in zip(df['close'], df['open'])]
                axes['volume'].bar(x_data, df['volume'], color=colors, alpha=0.7, width=0.8)
            
            # Add info panel
            self.update_info_panel(symbol, df)
            
            # Update legends
            if self.chart_config['show_ema']:
                axes['price'].legend(loc='upper left', fontsize=8, frameon=False, 
                                   facecolor=self.colors['bg'], edgecolor='none')
            
            # Update canvas
            self.chart_canvases[symbol].draw_idle()
            
            # Update price label
            current_price = df['close'].iloc[-1]
            change = df['close'].iloc[-1] - df['close'].iloc[-2] if len(df) > 1 else 0
            change_pct = (change / df['close'].iloc[-2] * 100) if len(df) > 1 and df['close'].iloc[-2] != 0 else 0
            
            self.price_labels[symbol].config(
                text=f"{symbol}: ₹{current_price:.2f}",
                fg=self.colors['up_candle'] if change >= 0 else self.colors['down_candle']
            )
            
            # Update statistics
            rsi_current = df['rsi'].iloc[-1] if 'rsi' in df.columns and not pd.isna(df['rsi'].iloc[-1]) else 50
            volume_current = df['volume'].iloc[-1]
            
            self.stats_labels[symbol].config(
                text=f"Change: {change_pct:+.2f}% | Volume: {volume_current:,.0f} | RSI: {rsi_current:.1f}"
            )
            
            # Update timestamp
            self.chart_update_labels[symbol].config(
                text=f"Updated: {datetime.now().strftime('%H:%M:%S')}"
            )
            
        except Exception as e:
            print(f"Error updating chart for {symbol}: {e}")
            
    def configure_axes(self, axes: Dict, symbol: str):
        """Configure chart axes styling"""
        # Price axis
        axes['price'].set_facecolor(self.colors['bg'])
        axes['price'].tick_params(colors=self.colors['text'], labelsize=8)
        axes['price'].grid(True, alpha=0.3, color=self.colors['grid'])
        axes['price'].set_title(f'{symbol} - {self.chart_config["timeframe"]} Chart', 
                              color=self.colors['text'], fontsize=11, pad=10)
        axes['price'].spines['bottom'].set_color(self.colors['grid'])
        axes['price'].spines['top'].set_color(self.colors['grid'])
        axes['price'].spines['right'].set_color(self.colors['grid'])
        axes['price'].spines['left'].set_color(self.colors['grid'])
        
        # RSI axis
        axes['rsi'].set_facecolor(self.colors['bg'])
        axes['rsi'].tick_params(colors=self.colors['text'], labelsize=8)
        axes['rsi'].grid(True, alpha=0.3, color=self.colors['grid'])
        axes['rsi'].set_ylabel('RSI', color=self.colors['text'], fontsize=9)
        axes['rsi'].set_ylim(0, 100)
        axes['rsi'].axhline(y=70, color=self.colors['down_candle'], linestyle='--', alpha=0.7)
        axes['rsi'].axhline(y=30, color=self.colors['up_candle'], linestyle='--', alpha=0.7)
        axes['rsi'].axhline(y=50, color=self.colors['grid'], linestyle='-', alpha=0.5)
        
        # Volume axis
        axes['volume'].set_facecolor(self.colors['bg'])
        axes['volume'].tick_params(colors=self.colors['text'], labelsize=8)
        axes['volume'].grid(True, alpha=0.3, color=self.colors['grid'])
        axes['volume'].set_ylabel('Volume', color=self.colors['text'], fontsize=9)
        
        # Info axis
        axes['info'].set_facecolor(self.colors['bg'])
        axes['info'].axis('off')
        
    def update_info_panel(self, symbol: str, df: pd.DataFrame):
        """Update info panel with statistics"""
        if df.empty:
            return
            
        axes = self.chart_axes[symbol]['info']
        
        # Calculate statistics
        current_price = df['close'].iloc[-1]
        high_24h = df['high'].tail(24).max() if len(df) >= 24 else df['high'].max()
        low_24h = df['low'].tail(24).min() if len(df) >= 24 else df['low'].min()
        volume_avg = df['volume'].tail(20).mean() if len(df) >= 20 else df['volume'].mean()
        
        # Create info text
        info_text = f"High: ₹{high_24h:.2f} | Low: ₹{low_24h:.2f} | Avg Vol: {volume_avg:,.0f}"
        
        axes.text(0.02, 0.5, info_text, transform=axes.transAxes,
                 fontsize=9, color=self.colors['text'], va='center',
                 bbox=dict(boxstyle='round,pad=0.3', facecolor=self.colors['panel'], 
                          edgecolor='none', alpha=0.8))
                          
    # Data update methods
    def add_data_point(self, symbol: str, data_point: Dict):
        """Add new data point to symbol chart"""
        if symbol not in self.chart_data:
            return
            
        # Create new row
        new_row = pd.DataFrame([data_point])
        
        # Append to existing data
        self.chart_data[symbol] = pd.concat([self.chart_data[symbol], new_row], ignore_index=True)
        
        # Keep only recent data
        self.chart_data[symbol] = self.chart_data[symbol].tail(self.chart_config['bars_count'] * 2)
        
        # Recalculate indicators
        self.chart_data[symbol] = self.calculate_indicators(self.chart_data[symbol])
        
        # Update chart
        self.update_symbol_chart(symbol)
        
    def update_market_data(self, symbol: str, market_data: Dict):
        """Update chart with new market data"""
        if symbol not in self.symbols:
            return
            
        # Convert market data to OHLCV format
        current_price = market_data.get('current_price', 0)
        volume = market_data.get('volume', 0)
        
        # Create data point (simplified - in real implementation, aggregate tick data)
        data_point = {
            'timestamp': datetime.now(),
            'open': current_price,
            'high': current_price,
            'low': current_price,
            'close': current_price,
            'volume': volume
        }
        
        self.add_data_point(symbol, data_point)
        
    def update_all_charts(self, market_data: Dict):
        """Update all charts with market data"""
        for symbol, data in market_data.items():
            if symbol in self.symbols:
                self.update_market_data(symbol, data)
                
    # Control methods
    def change_timeframe(self, event=None):
        """Change chart timeframe"""
        new_timeframe = self.timeframe_var.get()
        self.chart_config['timeframe'] = new_timeframe
        
        # Regenerate data for new timeframe
        for symbol in self.symbols:
            self.generate_sample_data(symbol)
            self.update_symbol_chart(symbol)
            
    def toggle_indicators(self):
        """Toggle indicators display"""
        self.chart_config['show_ema'] = self.ema_var.get()
        self.chart_config['show_rsi'] = self.rsi_var.get()
        self.chart_config['show_volume'] = self.volume_var.get()
        self.chart_config['show_signals'] = self.signals_var.get()
        
        # Update all charts
        for symbol in self.symbols:
            self.update_symbol_chart(symbol)
            
    def refresh_charts(self):
        """Refresh all charts"""
        for symbol in self.symbols:
            self.update_symbol_chart(symbol)
            
    def save_charts(self):
        """Save all charts as images"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            for symbol in self.symbols:
                filename = f"chart_{symbol}_{timestamp}.png"
                self.chart_figures[symbol].savefig(
                    filename, 
                    dpi=300, 
                    bbox_inches='tight',
                    facecolor=self.colors['bg'],
                    edgecolor='none'
                )
            
            tk.messagebox.showinfo("Charts Saved", f"All charts saved with timestamp {timestamp}")
            
        except Exception as e:
            tk.messagebox.showerror("Save Error", f"Failed to save charts: {str(e)}")
            
    def reset_zoom(self):
        """Reset zoom for all charts"""
        for symbol in self.symbols:
            axes = self.chart_axes[symbol]
            for ax in axes.values():
                if hasattr(ax, 'relim'):
                    ax.relim()
                    ax.autoscale()
            self.chart_canvases[symbol].draw()
            
    def chart_settings(self):
        """Open chart settings dialog"""
        settings_window = tk.Toplevel(self.main_frame)
        settings_window.title("Chart Settings")
        settings_window.geometry("400x500")
        settings_window.configure(bg=self.colors['panel'])
        settings_window.transient(self.main_frame)
        settings_window.grab_set()
        
        # Settings frame
        settings_frame = tk.Frame(settings_window, bg=self.colors['panel'])
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Chart bars count
        tk.Label(settings_frame, text="Chart Bars Count:", 
                bg=self.colors['panel'], fg=self.colors['text'],
                font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        bars_var = tk.StringVar(value=str(self.chart_config['bars_count']))
        bars_entry = tk.Entry(settings_frame, textvariable=bars_var, width=15)
        bars_entry.pack(anchor='w', pady=(0, 15))
        
        # Update interval
        tk.Label(settings_frame, text="Update Interval (ms):", 
                bg=self.colors['panel'], fg=self.colors['text'],
                font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        interval_var = tk.StringVar(value=str(self.chart_config['update_interval']))
        interval_entry = tk.Entry(settings_frame, textvariable=interval_var, width=15)
        interval_entry.pack(anchor='w', pady=(0, 15))
        
        # Color settings
        tk.Label(settings_frame, text="Color Theme:", 
                bg=self.colors['panel'], fg=self.colors['text'],
                font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        theme_var = tk.StringVar(value="Dark")
        theme_combo = ttk.Combobox(settings_frame, textvariable=theme_var,
                                  values=["Dark", "Light", "Blue", "Green"],
                                  width=12, state="readonly")
        theme_combo.pack(anchor='w', pady=(0, 15))
        
        # Buttons
        button_frame = tk.Frame(settings_frame, bg=self.colors['panel'])
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        def apply_settings():
            try:
                self.chart_config['bars_count'] = int(bars_var.get())
                self.chart_config['update_interval'] = int(interval_var.get())
                
                # Apply theme (simplified)
                if theme_var.get() != "Dark":
                    tk.messagebox.showinfo("Theme", f"{theme_var.get()} theme will be applied in next update")
                
                # Refresh charts
                self.refresh_charts()
                settings_window.destroy()
                
            except ValueError:
                tk.messagebox.showerror("Invalid Input", "Please enter valid numbers")
        
        tk.Button(button_frame, text="Apply", command=apply_settings,
                 bg='#00aa00', fg='white', padx=20).pack(side=tk.RIGHT, padx=5)
        tk.Button(button_frame, text="Cancel", command=settings_window.destroy,
                 bg='#666666', fg='white', padx=20).pack(side=tk.RIGHT)
                 
    # Utility methods
    def get_chart_data(self, symbol: str) -> pd.DataFrame:
        """Get chart data for symbol"""
        return self.chart_data.get(symbol, pd.DataFrame()).copy()
        
    def set_data_callback(self, callback: Callable):
        """Set data update callback"""
        self.data_callback = callback
        
    def highlight_chart(self, symbol: str, highlight: bool = True):
        """Highlight specific chart tab"""
        try:
            # Find tab index
            for i in range(self.chart_notebook.index("end")):
                tab_text = self.chart_notebook.tab(i, "text")
                if symbol in tab_text:
                    if highlight:
                        self.chart_notebook.tab(i, text=f"● {symbol} Chart")
                    else:
                        self.chart_notebook.tab(i, text=f"{symbol} Chart")
                    break
        except:
            pass
            
    def switch_to_symbol(self, symbol: str):
        """Switch to specific symbol chart"""
        try:
            for i in range(self.chart_notebook.index("end")):
                tab_text = self.chart_notebook.tab(i, "text")
                if symbol in tab_text:
                    self.chart_notebook.select(i)
                    break
        except:
            pass
            
    def add_chart_annotation(self, symbol: str, x_pos: int, y_pos: float, text: str, color: str = None):
        """Add annotation to chart"""
        if symbol in self.chart_axes:
            color = color or self.colors['text']
            axes = self.chart_axes[symbol]['price']
            axes.annotate(text, xy=(x_pos, y_pos), xytext=(x_pos + 5, y_pos + 10),
                         arrowprops=dict(arrowstyle='->', color=color),
                         fontsize=8, color=color,
                         bbox=dict(boxstyle='round,pad=0.3', facecolor=self.colors['panel'], 
                                  edgecolor=color, alpha=0.8))
            self.chart_canvases[symbol].draw()
            
    def clear_chart_annotations(self, symbol: str):
        """Clear all annotations from chart"""
        if symbol in self.chart_axes:
            axes = self.chart_axes[symbol]['price']
            # Remove annotations
            for child in axes.get_children():
                if hasattr(child, 'get_text'):
                    child.remove()
            self.chart_canvases[symbol].draw()
            
    def export_chart_data(self, symbol: str, filename: str = None):
        """Export chart data to CSV"""
        if symbol not in self.chart_data:
            return False
            
        try:
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"chart_data_{symbol}_{timestamp}.csv"
                
            self.chart_data[symbol].to_csv(filename, index=False)
            return True
            
        except Exception as e:
            print(f"Error exporting chart data: {e}")
            return False
            
    def get_current_signals(self, symbol: str) -> Dict:
        """Get current trading signals for symbol"""
        if symbol not in self.chart_data or self.chart_data[symbol].empty:
            return {}
            
        df = self.chart_data[symbol]
        latest = df.iloc[-1]
        
        return {
            'symbol': symbol,
            'timestamp': latest.get('timestamp', datetime.now()),
            'price': latest.get('close', 0),
            'signal': latest.get('signal', 0),
            'rsi': latest.get('rsi', 50),
            'ema_9': latest.get('ema_9', 0),
            'ema_21': latest.get('ema_21', 0),
            'volume': latest.get('volume', 0),
            'signal_strength': abs(latest.get('signal', 0))
        }
        
    def start_auto_update(self, interval_ms: int = None):
        """Start automatic chart updates"""
        interval = interval_ms or self.chart_config['update_interval']
        
        def update_loop():
            # Simulate new data (in real implementation, get from data feed)
            for symbol in self.symbols:
                if self.chart_data[symbol].empty:
                    continue
                    
                # Get last price
                last_price = self.chart_data[symbol]['close'].iloc[-1]
                
                # Generate new price (random walk)
                change = np.random.normal(0, last_price * 0.001)
                new_price = max(last_price + change, last_price * 0.95)
                
                # Create new data point
                data_point = {
                    'timestamp': datetime.now(),
                    'open': last_price,
                    'high': max(last_price, new_price),
                    'low': min(last_price, new_price),
                    'close': new_price,
                    'volume': np.random.randint(10000, 50000)
                }
                
                self.add_data_point(symbol, data_point)
            
            # Schedule next update
            self.main_frame.after(interval, update_loop)
            
        # Start the update loop
        update_loop()
        
    def stop_auto_update(self):
        """Stop automatic chart updates"""
        # Cancel any pending updates
        self.main_frame.after_cancel("all")
        
    def destroy(self):
        """Clean up the panel"""
        self.stop_auto_update()
        if self.main_frame:
            self.main_frame.destroy()


# Example usage and testing
if __name__ == "__main__":
    import tkinter.messagebox
    
    root = tk.Tk()
    root.title("Charts Panel Test")
    root.geometry("1400x900")
    root.configure(bg='#1a1a1a')
    
    # Data callback function
    def on_data_update(symbol, data):
        print(f"Chart data update for {symbol}: {data}")
    
    # Create charts panel
    symbols = ['NIFTY', 'BANKNIFTY', 'SENSEX']
    charts_panel = ChartsPanel(root, symbols, on_data_update)
    
    # Start auto-updates
    charts_panel.start_auto_update(3000)  # Update every 3 seconds
    
    # Test highlight feature
    def test_features():
        # Highlight NIFTY chart
        charts_panel.highlight_chart('NIFTY', True)
        
        # Switch to BANKNIFTY
        root.after(5000, lambda: charts_panel.switch_to_symbol('BANKNIFTY'))
        
        # Add annotation
        root.after(8000, lambda: charts_panel.add_chart_annotation('NIFTY', 50, 22000, 'Test Signal', '#00ff00'))
        
    test_features()
    
    root.mainloop()