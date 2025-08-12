"""
Signal Generator for AI ITM Scalping Bot
Implements the core ITM scalping strategy from PRD
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from indicators.moving_averages import MovingAverages
from indicators.momentum import MomentumIndicators

class ITMScalpingSignals:
    """
    ITM Options Scalping Signal Generator
    Based on PRD strategy: EMA crossover + RSI + Volume + VWAP filter
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or self._default_config()
        
    def _default_config(self) -> Dict:
        """Default strategy configuration from PRD"""
        return {
            # EMA Settings
            'ema_fast': 9,
            'ema_slow': 21,
            
            # RSI Settings  
            'rsi_period': 14,
            'rsi_buy_min': 45,
            'rsi_buy_max': 65,
            'rsi_sell_min': 35,
            'rsi_sell_max': 55,
            
            # Volume Filter
            'volume_multiplier': 1.5,  # 1.5x average volume
            'volume_period': 20,
            
            # VWAP Filter
            'use_vwap_filter': True,
            
            # Time Filters (market hours)
            'avoid_first_minutes': 15,  # Avoid first 15 minutes
            'avoid_last_minutes': 15,   # Avoid last 15 minutes
            'market_start': '09:15',
            'market_end': '15:30',
            
            # Signal Confidence
            'min_confidence': 0.6,
            
            # ITM Options Criteria
            'delta_min': 0.6,
            'delta_max': 0.8,
            'min_volume': 1000,
            'max_bid_ask_spread': 2.0
        }
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all required technical indicators"""
        
        if len(df) < max(self.config['ema_slow'], self.config['rsi_period'], self.config['volume_period']):
            raise ValueError(f"Need at least {max(self.config['ema_slow'], self.config['rsi_period'], self.config['volume_period'])} data points")
        
        # Copy dataframe
        data = df.copy()
        
        # Calculate EMAs
        data['ema_9'] = MovingAverages.ema(data['close'], self.config['ema_fast'])
        data['ema_21'] = MovingAverages.ema(data['close'], self.config['ema_slow'])
        
        # Calculate RSI
        data['rsi'] = MomentumIndicators.rsi(data['close'], self.config['rsi_period'])
        
        # Calculate MACD for additional confirmation
        macd_line, signal_line, histogram = MomentumIndicators.macd(data['close'])
        data['macd'] = macd_line
        data['macd_signal'] = signal_line
        data['macd_histogram'] = histogram
        
        # Calculate VWAP
        data['vwap'] = MovingAverages.vwap(data)
        
        # Calculate volume indicators
        data['volume_avg'] = data['volume'].rolling(window=self.config['volume_period']).mean()
        data['volume_ratio'] = data['volume'] / data['volume_avg']
        
        # Price action indicators
        data['price_change'] = data['close'].pct_change()
        data['volatility'] = data['price_change'].rolling(window=10).std()
        
        return data
    
    def check_time_filter(self, timestamp: pd.Timestamp) -> bool:
        """Check if current time is within allowed trading hours"""
        
        if pd.isna(timestamp):
            return False
        
        # Extract time
        current_time = timestamp.time()
        
        # Market hours
        market_start = pd.Timestamp(self.config['market_start']).time()
        market_end = pd.Timestamp(self.config['market_end']).time()
        
        # Avoid first and last minutes
        avoid_until = (pd.Timestamp(self.config['market_start']) + 
                      timedelta(minutes=self.config['avoid_first_minutes'])).time()
        avoid_after = (pd.Timestamp(self.config['market_end']) - 
                      timedelta(minutes=self.config['avoid_last_minutes'])).time()
        
        # Check if within allowed time
        if current_time >= avoid_until and current_time <= avoid_after:
            return True
        
        return False
    
    def generate_bullish_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate bullish (CE ITM) signals based on PRD criteria
        
        Primary Conditions (ALL Required):
        - 5-min: Price > VWAP (trend filter)
        - 3-min: EMA 9 > EMA 21 (momentum)  
        - 1-min: Fresh EMA crossover (9 crosses 21 up)
        - 1-min: RSI between 45-65
        - Volume: >1.5x average volume
        - Time Filter: Not first/last 15 minutes
        """
        
        signals = pd.Series(0, index=data.index, name='bullish_signals')
        
        if len(data) < 2:
            return signals
        
        for i in range(1, len(data)):
            
            # Time filter
            if not self.check_time_filter(data.iloc[i]['timestamp']):
                continue
            
            # Primary Conditions (ALL required)
            conditions_met = 0
            total_conditions = 6
            
            # 1. VWAP Filter: Price > VWAP (trend filter)
            if data.iloc[i]['close'] > data.iloc[i]['vwap']:
                conditions_met += 1
            
            # 2. EMA Momentum: EMA 9 > EMA 21
            if (pd.notna(data.iloc[i]['ema_9']) and pd.notna(data.iloc[i]['ema_21']) and
                data.iloc[i]['ema_9'] > data.iloc[i]['ema_21']):
                conditions_met += 1
            
            # 3. Fresh EMA Crossover: EMA 9 crosses above EMA 21
            if (pd.notna(data.iloc[i]['ema_9']) and pd.notna(data.iloc[i-1]['ema_9']) and
                pd.notna(data.iloc[i]['ema_21']) and pd.notna(data.iloc[i-1]['ema_21']) and
                data.iloc[i]['ema_9'] > data.iloc[i]['ema_21'] and
                data.iloc[i-1]['ema_9'] <= data.iloc[i-1]['ema_21']):
                conditions_met += 1
            
            # 4. RSI Filter: Between 45-65 (not oversold/overbought)
            if (pd.notna(data.iloc[i]['rsi']) and
                self.config['rsi_buy_min'] <= data.iloc[i]['rsi'] <= self.config['rsi_buy_max']):
                conditions_met += 1
            
            # 5. Volume Filter: >1.5x average volume
            if (pd.notna(data.iloc[i]['volume_ratio']) and
                data.iloc[i]['volume_ratio'] >= self.config['volume_multiplier']):
                conditions_met += 1
            
            # 6. Price Action: Strong green candle
            if (data.iloc[i]['close'] > data.iloc[i]['open'] and
                data.iloc[i]['price_change'] > 0):
                conditions_met += 1
            
            # Signal strength based on conditions met
            signal_strength = conditions_met / total_conditions
            
            # Generate signal if minimum conditions met
            if signal_strength >= self.config['min_confidence']:
                signals.iloc[i] = signal_strength
        
        return signals
    
    def generate_bearish_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate bearish (PE ITM) signals - inverse of bullish conditions
        """
        
        signals = pd.Series(0, index=data.index, name='bearish_signals')
        
        if len(data) < 2:
            return signals
        
        for i in range(1, len(data)):
            
            # Time filter
            if not self.check_time_filter(data.iloc[i]['timestamp']):
                continue
            
            # Primary Conditions (ALL required)
            conditions_met = 0
            total_conditions = 6
            
            # 1. VWAP Filter: Price < VWAP (trend filter)
            if data.iloc[i]['close'] < data.iloc[i]['vwap']:
                conditions_met += 1
            
            # 2. EMA Momentum: EMA 9 < EMA 21
            if (pd.notna(data.iloc[i]['ema_9']) and pd.notna(data.iloc[i]['ema_21']) and
                data.iloc[i]['ema_9'] < data.iloc[i]['ema_21']):
                conditions_met += 1
            
            # 3. Fresh EMA Crossover: EMA 9 crosses below EMA 21
            if (pd.notna(data.iloc[i]['ema_9']) and pd.notna(data.iloc[i-1]['ema_9']) and
                pd.notna(data.iloc[i]['ema_21']) and pd.notna(data.iloc[i-1]['ema_21']) and
                data.iloc[i]['ema_9'] < data.iloc[i]['ema_21'] and
                data.iloc[i-1]['ema_9'] >= data.iloc[i-1]['ema_21']):
                conditions_met += 1
            
            # 4. RSI Filter: Between 35-55 (not oversold/overbought)
            if (pd.notna(data.iloc[i]['rsi']) and
                self.config['rsi_sell_min'] <= data.iloc[i]['rsi'] <= self.config['rsi_sell_max']):
                conditions_met += 1
            
            # 5. Volume Filter: >1.5x average volume
            if (pd.notna(data.iloc[i]['volume_ratio']) and
                data.iloc[i]['volume_ratio'] >= self.config['volume_multiplier']):
                conditions_met += 1
            
            # 6. Price Action: Strong red candle
            if (data.iloc[i]['close'] < data.iloc[i]['open'] and
                data.iloc[i]['price_change'] < 0):
                conditions_met += 1
            
            # Signal strength based on conditions met
            signal_strength = conditions_met / total_conditions
            
            # Generate signal if minimum conditions met
            if signal_strength >= self.config['min_confidence']:
                signals.iloc[i] = signal_strength
        
        return signals
    
    def generate_exit_signals(self, data: pd.DataFrame, entry_signal: str, entry_index: int) -> Dict:
        """
        Generate exit signals based on PRD exit strategy
        
        Multi-Level Profit Taking:
        - Level 1: 50% exit at 8 points (quick booking)
        - Level 2: 30% exit at 15 points (momentum target) 
        - Level 3: 20% trailing stop (5-point trail)
        - Force Exit: 5 minutes maximum hold
        """
        
        exit_info = {
            'exit_type': None,
            'exit_index': None,
            'exit_price': None,
            'target_levels': {
                'level_1': 8,   # Quick profit (50% exit)
                'level_2': 15,  # Momentum target (30% exit)
                'level_3': 5    # Trailing stop distance (20% exit)
            },
            'max_hold_minutes': 5,
            'stop_loss': 300  # Maximum loss per lot
        }
        
        if entry_index >= len(data) - 1:
            return exit_info
        
        entry_price = data.iloc[entry_index]['close']
        entry_time = data.iloc[entry_index]['timestamp']
        
        # Check subsequent bars for exit conditions
        for i in range(entry_index + 1, len(data)):
            current_price = data.iloc[i]['close']
            current_time = data.iloc[i]['timestamp']
            
            # Time-based exit (5 minutes maximum)
            time_diff = (current_time - entry_time).total_seconds() / 60
            if time_diff >= exit_info['max_hold_minutes']:
                exit_info.update({
                    'exit_type': 'time_limit',
                    'exit_index': i,
                    'exit_price': current_price
                })
                break
            
            # Profit/Loss based exits
            if entry_signal == 'bullish':
                pnl_points = current_price - entry_price
                
                # Stop loss
                if pnl_points <= -exit_info['stop_loss']:
                    exit_info.update({
                        'exit_type': 'stop_loss',
                        'exit_index': i,
                        'exit_price': current_price
                    })
                    break
                
                # Profit targets
                if pnl_points >= exit_info['target_levels']['level_2']:
                    exit_info.update({
                        'exit_type': 'profit_target_2',
                        'exit_index': i,
                        'exit_price': current_price
                    })
                    break
                elif pnl_points >= exit_info['target_levels']['level_1']:
                    exit_info.update({
                        'exit_type': 'profit_target_1',
                        'exit_index': i,
                        'exit_price': current_price
                    })
                    break
                    
            elif entry_signal == 'bearish':
                pnl_points = entry_price - current_price
                
                # Stop loss
                if pnl_points <= -exit_info['stop_loss']:
                    exit_info.update({
                        'exit_type': 'stop_loss',
                        'exit_index': i,
                        'exit_price': current_price
                    })
                    break
                
                # Profit targets
                if pnl_points >= exit_info['target_levels']['level_2']:
                    exit_info.update({
                        'exit_type': 'profit_target_2',
                        'exit_index': i,
                        'exit_price': current_price
                    })
                    break
                elif pnl_points >= exit_info['target_levels']['level_1']:
                    exit_info.update({
                        'exit_type': 'profit_target_1',
                        'exit_index': i,
                        'exit_price': current_price
                    })
                    break
        
        return exit_info
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Main function to generate all trading signals
        
        Returns:
            pd.DataFrame: Original data with added signal columns
        """
        
        print(f"🎯 Generating ITM scalping signals for {len(df)} bars")
        
        # Calculate indicators
        data = self.calculate_indicators(df)
        
        # Generate signals
        data['bullish_signals'] = self.generate_bullish_signals(data)
        data['bearish_signals'] = self.generate_bearish_signals(data)
        
        # Combine signals
        data['signal_type'] = 'NONE'
        data['signal_strength'] = 0.0
        
        # Mark bullish signals
        bullish_mask = data['bullish_signals'] > 0
        data.loc[bullish_mask, 'signal_type'] = 'BUY_CE'
        data.loc[bullish_mask, 'signal_strength'] = data.loc[bullish_mask, 'bullish_signals']
        
        # Mark bearish signals
        bearish_mask = data['bearish_signals'] > 0
        data.loc[bearish_mask, 'signal_type'] = 'BUY_PE'
        data.loc[bearish_mask, 'signal_strength'] = data.loc[bearish_mask, 'bearish_signals']
        
        # Signal summary
        total_signals = (data['signal_type'] != 'NONE').sum()
        bullish_count = (data['signal_type'] == 'BUY_CE').sum()
        bearish_count = (data['signal_type'] == 'BUY_PE').sum()
        
        print(f"✅ Signal Generation Complete:")
        print(f"   Total signals: {total_signals}")
        print(f"   Bullish (CE): {bullish_count}")
        print(f"   Bearish (PE): {bearish_count}")
        print(f"   Avg strength: {data['signal_strength'][data['signal_strength'] > 0].mean():.2f}")
        
        return data

# Test the strategy
if __name__ == "__main__":
    print("🧪 Testing ITM Scalping Strategy Engine")
    print("=" * 50)
    
    # Import data handler
    from data_handler.csv_handler import CSVDataHandler
    
    # Generate test data
    handler = CSVDataHandler()
    df = handler.generate_sample_data("NIFTY", days=3)
    
    print(f"📊 Testing with {len(df)} data points")
    
    # Initialize strategy
    strategy = ITMScalpingSignals()
    
    # Generate signals
    signals_df = strategy.generate_signals(df)
    
    # Show signal summary
    signal_rows = signals_df[signals_df['signal_type'] != 'NONE']
    
    if len(signal_rows) > 0:
        print(f"\n📈 Signal Details:")
        print(signal_rows[['timestamp', 'close', 'signal_type', 'signal_strength', 
                          'ema_9', 'ema_21', 'rsi', 'vwap']].round(2).to_string(index=False))
        
        # Test exit signal generation
        if len(signal_rows) > 0:
            first_signal = signal_rows.iloc[0]
            entry_index = signal_rows.index[0]
            signal_type = 'bullish' if first_signal['signal_type'] == 'BUY_CE' else 'bearish'
            
            exit_info = strategy.generate_exit_signals(signals_df, signal_type, entry_index)
            print(f"\n🎯 Sample Exit Strategy:")
            print(f"   Exit type: {exit_info.get('exit_type', 'None')}")
            print(f"   Target levels: {exit_info['target_levels']}")
    else:
        print(f"\n⚠️ No signals generated in test data")
    
    print(f"\n🎉 ITM Scalping Strategy test completed!")
