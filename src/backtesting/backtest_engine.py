"""
Backtesting Engine for AI ITM Scalping Bot
Comprehensive backtesting with performance metrics
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from strategy.signal_generator import ITMScalpingSignals
from data_handler.csv_handler import CSVDataHandler
from data_handler.database import TradingDatabase

class ITMBacktester:
    """
    Advanced backtesting engine for ITM scalping strategy
    """
    
    def __init__(self, initial_capital: float = 100000, config: Dict = None):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.config = config or self._default_config()
        
        # Trading results storage
        self.trades = []
        self.equity_curve = []
        self.daily_returns = []
        
        # Performance metrics
        self.metrics = {}
        
        # Strategy engine
        self.strategy = ITMScalpingSignals(config)
        
    def _default_config(self) -> Dict:
        """Default backtesting configuration"""
        return {
            # Position sizing
            'position_size_per_trade': 10000,  # Fixed amount per trade
            'max_positions': 3,  # Maximum concurrent positions
            'risk_per_trade': 0.02,  # 2% risk per trade
            
            # Transaction costs
            'commission_per_trade': 20,  # ₹20 per trade
            'slippage_points': 0.5,  # 0.5 points slippage
            
            # ITM Options simulation
            'option_multiplier': 75,  # NIFTY option multiplier
            'itm_premium_factor': 0.02,  # ITM premium as % of spot
            
            # Exit rules
            'force_exit_minutes': 5,  # Maximum hold time
            'stop_loss_points': 10,  # Maximum loss points
            'profit_target_1': 8,   # First profit target
            'profit_target_2': 15,  # Second profit target
        }
    
    def calculate_option_premium(self, spot_price: float, strike_price: float, 
                                option_type: str = 'CE') -> float:
        """
        Simplified option premium calculation for ITM options
        """
        intrinsic_value = max(0, spot_price - strike_price) if option_type == 'CE' else max(0, strike_price - spot_price)
        time_value = spot_price * self.config['itm_premium_factor']
        
        return intrinsic_value + time_value
    
    def get_itm_strike(self, spot_price: float, option_type: str = 'CE') -> float:
        """Get ITM strike price based on spot price"""
        if option_type == 'CE':
            # For ITM CE, strike should be below spot
            return round(spot_price - 50, 0)  # 50 points ITM
        else:
            # For ITM PE, strike should be above spot  
            return round(spot_price + 50, 0)  # 50 points ITM
    
    def execute_trade(self, signal: pd.Series, data: pd.DataFrame, index: int) -> Dict:
        """Execute a trade based on signal"""
        
        spot_price = signal['close']
        signal_type = signal['signal_type']
        timestamp = signal['timestamp']
        
        # Determine option type and strike
        if signal_type == 'BUY_CE':
            option_type = 'CE'
            strike = self.get_itm_strike(spot_price, 'CE')
        elif signal_type == 'BUY_PE':
            option_type = 'PE'
            strike = self.get_itm_strike(spot_price, 'PE')
        else:
            return None
        
        # Calculate option premium
        entry_premium = self.calculate_option_premium(spot_price, strike, option_type)
        
        # Apply slippage
        entry_premium += self.config['slippage_points']
        
        # Calculate position size
        position_value = self.config['position_size_per_trade']
        quantity = int(position_value / (entry_premium * self.config['option_multiplier']))
        quantity = max(quantity, 1)  # Minimum 1 lot
        
        # Create trade record
        trade = {
            'entry_time': timestamp,
            'entry_index': index,
            'signal_type': signal_type,
            'option_type': option_type,
            'strike': strike,
            'spot_price': spot_price,
            'entry_premium': entry_premium,
            'quantity': quantity,
            'signal_strength': signal['signal_strength'],
            'status': 'OPEN',
            'exit_time': None,
            'exit_premium': None,
            'pnl': 0,
            'pnl_points': 0,
            'exit_reason': None,
            'hold_time_minutes': 0,
            'commission': self.config['commission_per_trade'] * 2  # Entry + Exit
        }
        
        return trade
    
    def check_exit_conditions(self, trade: Dict, current_data: pd.Series, 
                            minutes_held: float) -> Tuple[bool, str, float]:
        """
        Check if trade should be exited
        Returns: (should_exit, exit_reason, exit_premium)
        """
        
        current_spot = current_data['close']
        option_type = trade['option_type']
        strike = trade['strike']
        
        # Calculate current option premium
        current_premium = self.calculate_option_premium(current_spot, strike, option_type)
        
        # Calculate P&L in points
        pnl_points = current_premium - trade['entry_premium']
        
        # 1. Time-based exit (force exit after max hold time)
        if minutes_held >= self.config['force_exit_minutes']:
            return True, 'time_limit', current_premium
        
        # 2. Stop loss
        if pnl_points <= -self.config['stop_loss_points']:
            return True, 'stop_loss', current_premium
        
        # 3. Profit targets
        if pnl_points >= self.config['profit_target_2']:
            return True, 'profit_target_2', current_premium
        elif pnl_points >= self.config['profit_target_1']:
            return True, 'profit_target_1', current_premium
        
        # 4. Reverse signal (optional aggressive exit)
        opposite_signal = 'BUY_PE' if trade['signal_type'] == 'BUY_CE' else 'BUY_CE'
        if (hasattr(current_data, 'signal_type') and 
            current_data['signal_type'] == opposite_signal and
            current_data['signal_strength'] > 0.7):
            return True, 'reverse_signal', current_premium
        
        return False, None, current_premium
    
    def run_backtest(self, data: pd.DataFrame) -> Dict:
        """
        Run complete backtest on historical data
        """
        
        print(f"🔄 Starting backtest on {len(data)} bars")
        print(f"💰 Initial capital: ₹{self.initial_capital:,.2f}")
        
        # Generate signals
        signals_data = self.strategy.generate_signals(data)
        
        # Get signal rows
        signal_rows = signals_data[signals_data['signal_type'] != 'NONE']
        print(f"📊 Found {len(signal_rows)} trading signals")
        
        if len(signal_rows) == 0:
            print("⚠️ No signals found in data")
            return self._generate_results()
        
        # Track open positions
        open_trades = []
        
        # Process each bar
        for i, (index, row) in enumerate(signals_data.iterrows()):
            current_time = row['timestamp']
            
            # Check exit conditions for open trades
            for trade in open_trades[:]:  # Copy list to allow removal during iteration
                
                # Calculate hold time
                hold_time = (current_time - trade['entry_time']).total_seconds() / 60
                
                # Check exit conditions
                should_exit, exit_reason, exit_premium = self.check_exit_conditions(
                    trade, row, hold_time
                )
                
                if should_exit:
                    # Close trade
                    trade['exit_time'] = current_time
                    trade['exit_premium'] = exit_premium - self.config['slippage_points']  # Exit slippage
                    trade['hold_time_minutes'] = hold_time
                    trade['exit_reason'] = exit_reason
                    trade['status'] = 'CLOSED'
                    
                    # Calculate P&L
                    pnl_points = trade['exit_premium'] - trade['entry_premium']
                    trade['pnl_points'] = pnl_points
                    trade['pnl'] = (pnl_points * trade['quantity'] * 
                                   self.config['option_multiplier'] - trade['commission'])
                    
                    # Update capital
                    self.current_capital += trade['pnl']
                    
                    # Move to completed trades
                    self.trades.append(trade)
                    open_trades.remove(trade)
                    
                    print(f"📤 Trade closed: {trade['signal_type']} | "
                          f"P&L: {trade['pnl']:+.0f} | Reason: {exit_reason}")
            
            # Check for new entry signals
            if (row['signal_type'] != 'NONE' and 
                len(open_trades) < self.config['max_positions'] and
                self.current_capital > self.config['position_size_per_trade']):
                
                # Execute new trade
                new_trade = self.execute_trade(row, signals_data, index)
                if new_trade:
                    open_trades.append(new_trade)
                    print(f"📥 Trade opened: {new_trade['signal_type']} @ "
                          f"₹{new_trade['entry_premium']:.2f}")
            
            # Record equity curve
            total_unrealized_pnl = 0
            for trade in open_trades:
                current_premium = self.calculate_option_premium(
                    row['close'], trade['strike'], trade['option_type']
                )
                unrealized_pnl = ((current_premium - trade['entry_premium']) * 
                                 trade['quantity'] * self.config['option_multiplier'])
                total_unrealized_pnl += unrealized_pnl
            
            total_equity = self.current_capital + total_unrealized_pnl
            self.equity_curve.append({
                'timestamp': current_time,
                'equity': total_equity,
                'realized_pnl': self.current_capital - self.initial_capital,
                'unrealized_pnl': total_unrealized_pnl,
                'open_positions': len(open_trades)
            })
        
        # Close any remaining open trades at the end
        for trade in open_trades:
            last_row = signals_data.iloc[-1]
            trade['exit_time'] = last_row['timestamp']
            exit_premium = self.calculate_option_premium(
                last_row['close'], trade['strike'], trade['option_type']
            )
            trade['exit_premium'] = exit_premium - self.config['slippage_points']
            trade['hold_time_minutes'] = (trade['exit_time'] - trade['entry_time']).total_seconds() / 60
            trade['exit_reason'] = 'end_of_data'
            trade['status'] = 'CLOSED'
            
            pnl_points = trade['exit_premium'] - trade['entry_premium']
            trade['pnl_points'] = pnl_points
            trade['pnl'] = (pnl_points * trade['quantity'] * 
                           self.config['option_multiplier'] - trade['commission'])
            
            self.current_capital += trade['pnl']
            self.trades.append(trade)
        
        print(f"✅ Backtest completed")
        print(f"💰 Final capital: ₹{self.current_capital:,.2f}")
        print(f"📈 Total return: {((self.current_capital/self.initial_capital-1)*100):+.2f}%")
        
        return self._generate_results()
    
    def _generate_results(self) -> Dict:
        """Generate comprehensive backtest results"""
        
        if not self.trades:
            return {
                'summary': {'total_trades': 0, 'total_return': 0},
                'trades': [],
                'equity_curve': self.equity_curve
            }
        
        trades_df = pd.DataFrame(self.trades)
        
        # Basic metrics
        total_trades = len(trades_df)
        winning_trades = len(trades_df[trades_df['pnl'] > 0])
        losing_trades = len(trades_df[trades_df['pnl'] < 0])
        
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        total_pnl = trades_df['pnl'].sum()
        total_return = (self.current_capital / self.initial_capital - 1) * 100
        
        gross_profit = trades_df[trades_df['pnl'] > 0]['pnl'].sum()
        gross_loss = abs(trades_df[trades_df['pnl'] < 0]['pnl'].sum())
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        avg_win = trades_df[trades_df['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
        avg_loss = trades_df[trades_df['pnl'] < 0]['pnl'].mean() if losing_trades > 0 else 0
        
        # Risk metrics
        if len(self.equity_curve) > 0:
            equity_series = pd.Series([eq['equity'] for eq in self.equity_curve])
            returns_series = equity_series.pct_change().dropna()
            
            max_drawdown = ((equity_series.cummax() - equity_series) / equity_series.cummax()).max() * 100
            sharpe_ratio = returns_series.mean() / returns_series.std() * np.sqrt(252) if returns_series.std() > 0 else 0
        else:
            max_drawdown = 0
            sharpe_ratio = 0
        
        # Hold time analysis
        avg_hold_time = trades_df['hold_time_minutes'].mean()
        
        # Exit reason analysis
        exit_reasons = trades_df['exit_reason'].value_counts().to_dict()
        
        self.metrics = {
            'summary': {
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': win_rate,
                'total_pnl': total_pnl,
                'total_return': total_return,
                'profit_factor': profit_factor,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'max_drawdown': max_drawdown,
                'sharpe_ratio': sharpe_ratio,
                'avg_hold_time': avg_hold_time
            },
            'exit_reasons': exit_reasons,
            'trades': self.trades,
            'equity_curve': self.equity_curve
        }
        
        return self.metrics
    
    def print_results(self):
        """Print formatted backtest results"""
        
        if not self.metrics:
            print("No results to display")
            return
        
        summary = self.metrics['summary']
        
        print(f"\n📊 BACKTEST RESULTS")
        print(f"=" * 50)
        print(f"💰 Capital: ₹{self.initial_capital:,.0f} → ₹{self.current_capital:,.0f}")
        print(f"📈 Total Return: {summary['total_return']:+.2f}%")
        print(f"📊 Total Trades: {summary['total_trades']}")
        print(f"✅ Win Rate: {summary['win_rate']*100:.1f}% ({summary['winning_trades']}/{summary['total_trades']})")
        print(f"💵 Profit Factor: {summary['profit_factor']:.2f}")
        print(f"🎯 Avg Win: ₹{summary['avg_win']:,.0f}")
        print(f"🔻 Avg Loss: ₹{summary['avg_loss']:,.0f}")
        print(f"📉 Max Drawdown: {summary['max_drawdown']:.2f}%")
        print(f"📊 Sharpe Ratio: {summary['sharpe_ratio']:.2f}")
        print(f"⏱️ Avg Hold Time: {summary['avg_hold_time']:.1f} minutes")
        
        print(f"\n🎯 Exit Reasons:")
        for reason, count in self.metrics['exit_reasons'].items():
            print(f"   {reason}: {count} trades")

# Test backtesting engine
if __name__ == "__main__":
    print("🧪 Testing ITM Backtesting Engine")
    print("=" * 50)
    
    # Generate more comprehensive test data
    handler = CSVDataHandler()
    df = handler.generate_sample_data("NIFTY", days=10)  # 10 days for better backtest
    
    print(f"📊 Testing with {len(df)} bars over {df['timestamp'].max() - df['timestamp'].min()}")
    
    # Initialize backtester
    backtester = ITMBacktester(initial_capital=100000)
    
    # Run backtest
    results = backtester.run_backtest(df)
    
    # Print results
    backtester.print_results()
    
    # Show sample trades
    if len(backtester.trades) > 0:
        print(f"\n📋 Sample Trades (first 5):")
        trades_df = pd.DataFrame(backtester.trades)
        sample_trades = trades_df.head()[['entry_time', 'signal_type', 'entry_premium', 
                                        'exit_premium', 'pnl', 'exit_reason']]
        print(sample_trades.round(2).to_string(index=False))
    
    print(f"\n🎉 Backtesting engine test completed!")
