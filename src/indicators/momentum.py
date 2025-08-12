"""
Momentum Indicators: RSI, MACD, Stochastic
"""

import pandas as pd
import numpy as np
from typing import Tuple, Union

class MomentumIndicators:
    
    @staticmethod
    def rsi(data: Union[pd.Series, list], period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI)
        
        Args:
            data: Price data (typically close prices)
            period: RSI period (default 14)
            
        Returns:
            pd.Series: RSI values (0-100)
        """
        if isinstance(data, list):
            data = pd.Series(data)
        
        # Calculate price changes
        delta = data.diff()
        
        # Separate gains and losses
        gains = delta.where(delta > 0, 0.0)
        losses = -delta.where(delta < 0, 0.0)
        
        # Calculate average gains and losses using EMA
        avg_gains = gains.ewm(span=period, adjust=False).mean()
        avg_losses = losses.ewm(span=period, adjust=False).mean()
        
        # Calculate relative strength
        rs = avg_gains / avg_losses
        
        # Calculate RSI
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def macd(data: Union[pd.Series, list], 
             fast_period: int = 12, 
             slow_period: int = 26, 
             signal_period: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Args:
            data: Price data (typically close prices)
            fast_period: Fast EMA period (default 12)
            slow_period: Slow EMA period (default 26)
            signal_period: Signal line EMA period (default 9)
            
        Returns:
            Tuple[pd.Series, pd.Series, pd.Series]: (MACD line, Signal line, Histogram)
        """
        if isinstance(data, list):
            data = pd.Series(data)
        
        # Calculate EMAs
        fast_ema = data.ewm(span=fast_period, adjust=False).mean()
        slow_ema = data.ewm(span=slow_period, adjust=False).mean()
        
        # MACD line
        macd_line = fast_ema - slow_ema
        
        # Signal line
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        
        # Histogram
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def stochastic(df: pd.DataFrame, 
                   k_period: int = 14, 
                   d_period: int = 3) -> Tuple[pd.Series, pd.Series]:
        """
        Calculate Stochastic Oscillator
        
        Args:
            df: DataFrame with high, low, close columns
            k_period: %K period (default 14)
            d_period: %D period (default 3)
            
        Returns:
            Tuple[pd.Series, pd.Series]: (%K, %D)
        """
        if not all(col in df.columns for col in ['high', 'low', 'close']):
            raise ValueError("DataFrame must contain 'high', 'low', 'close' columns")
        
        # Calculate %K
        lowest_low = df['low'].rolling(window=k_period).min()
        highest_high = df['high'].rolling(window=k_period).max()
        
        k_percent = 100 * ((df['close'] - lowest_low) / (highest_high - lowest_low))
        
        # Calculate %D (SMA of %K)
        d_percent = k_percent.rolling(window=d_period).mean()
        
        return k_percent, d_percent
    
    @staticmethod
    def rsi_signals(rsi: pd.Series, 
                   oversold: float = 30, 
                   overbought: float = 70) -> pd.Series:
        """
        Generate RSI-based trading signals
        
        Args:
            rsi: RSI values
            oversold: Oversold threshold (default 30)
            overbought: Overbought threshold (default 70)
            
        Returns:
            pd.Series: 1 for buy signal, -1 for sell signal, 0 for no signal
        """
        signals = pd.Series(0, index=rsi.index)
        
        # Buy signal: RSI crosses above oversold level
        buy_condition = (rsi > oversold) & (rsi.shift(1) <= oversold)
        signals[buy_condition] = 1
        
        # Sell signal: RSI crosses below overbought level
        sell_condition = (rsi < overbought) & (rsi.shift(1) >= overbought)
        signals[sell_condition] = -1
        
        return signals
    
    @staticmethod
    def macd_signals(macd_line: pd.Series, signal_line: pd.Series) -> pd.Series:
        """
        Generate MACD-based trading signals
        
        Args:
            macd_line: MACD line
            signal_line: Signal line
            
        Returns:
            pd.Series: 1 for bullish signal, -1 for bearish signal, 0 for no signal
        """
        signals = pd.Series(0, index=macd_line.index)
        
        # Bullish signal: MACD crosses above signal line
        bullish_cross = (macd_line > signal_line) & (macd_line.shift(1) <= signal_line.shift(1))
        signals[bullish_cross] = 1
        
        # Bearish signal: MACD crosses below signal line
        bearish_cross = (macd_line < signal_line) & (macd_line.shift(1) >= signal_line.shift(1))
        signals[bearish_cross] = -1
        
        return signals

# Test
if __name__ == "__main__":
    print("🧪 Testing Momentum Indicators")
    print("=" * 50)
    
    # Import sample data
    import sys, os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from data_handler.csv_handler import CSVDataHandler
    
    # Generate data
    handler = CSVDataHandler()
    df = handler.generate_sample_data("NIFTY", days=3)
    
    print(f"📊 Testing with {len(df)} data points")
    
    # Test RSI
    rsi = MomentumIndicators.rsi(df['close'])
    rsi_signals = MomentumIndicators.rsi_signals(rsi)
    
    print(f"✅ RSI calculated: {rsi.notna().sum()} valid values")
    print(f"   RSI range: {rsi.min():.2f} - {rsi.max():.2f}")
    print(f"   RSI signals: {(rsi_signals != 0).sum()} total")
    
    # Test MACD
    macd_line, signal_line, histogram = MomentumIndicators.macd(df['close'])
    macd_signals = MomentumIndicators.macd_signals(macd_line, signal_line)
    
    print(f"✅ MACD calculated: {macd_line.notna().sum()} valid values")
    print(f"   MACD signals: {(macd_signals != 0).sum()} total")
    
    # Test Stochastic
    stoch_k, stoch_d = MomentumIndicators.stochastic(df)
    
    print(f"✅ Stochastic calculated: %K={stoch_k.notna().sum()}, %D={stoch_d.notna().sum()} valid values")
    
    # Show sample values
    print(f"\n📈 Sample Values (last 5 rows):")
    results_df = pd.DataFrame({
        'Close': df['close'].tail(5),
        'RSI': rsi.tail(5),
        'MACD': macd_line.tail(5),
        'Signal': signal_line.tail(5),
        'Stoch_K': stoch_k.tail(5),
        'RSI_Sig': rsi_signals.tail(5),
        'MACD_Sig': macd_signals.tail(5)
    })
    print(results_df.round(2).to_string())
    
    print(f"\n🎉 Momentum indicators test completed!")
