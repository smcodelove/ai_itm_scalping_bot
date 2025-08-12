"""
Moving Average Indicators for Trading Bot
EMA, SMA, and VWAP calculations
"""

import pandas as pd
import numpy as np
from typing import Union, Optional

class MovingAverages:
    """Moving average calculations for technical analysis"""
    
    @staticmethod
    def ema(data: Union[pd.Series, list], period: int, alpha: Optional[float] = None) -> pd.Series:
        """
        Calculate Exponential Moving Average (EMA)
        
        Args:
            data: Price data (typically close prices)
            period: EMA period
            alpha: Smoothing factor (if None, uses 2/(period+1))
            
        Returns:
            pd.Series: EMA values
        """
        if isinstance(data, list):
            data = pd.Series(data)
        
        if alpha is None:
            alpha = 2.0 / (period + 1)
        
        # Calculate EMA using pandas ewm
        ema_values = data.ewm(alpha=alpha, adjust=False).mean()
        
        return ema_values
    
    @staticmethod
    def sma(data: Union[pd.Series, list], period: int) -> pd.Series:
        """
        Calculate Simple Moving Average (SMA)
        
        Args:
            data: Price data
            period: SMA period
            
        Returns:
            pd.Series: SMA values
        """
        if isinstance(data, list):
            data = pd.Series(data)
        
        sma_values = data.rolling(window=period).mean()
        return sma_values
    
    @staticmethod
    def vwap(df: pd.DataFrame, volume_col: str = 'volume') -> pd.Series:
        """
        Calculate Volume Weighted Average Price (VWAP)
        
        Args:
            df: DataFrame with OHLCV data
            volume_col: Name of volume column
            
        Returns:
            pd.Series: VWAP values
        """
        if not all(col in df.columns for col in ['high', 'low', 'close', volume_col]):
            raise ValueError("DataFrame must contain 'high', 'low', 'close', and volume columns")
        
        # Typical price (HLC/3)
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        
        # VWAP calculation
        vwap_numerator = (typical_price * df[volume_col]).cumsum()
        vwap_denominator = df[volume_col].cumsum()
        
        vwap = vwap_numerator / vwap_denominator
        
        return vwap
    
    @staticmethod
    def ema_crossover(fast_ema: pd.Series, slow_ema: pd.Series) -> pd.Series:
        """
        Detect EMA crossover signals
        
        Args:
            fast_ema: Fast EMA series
            slow_ema: Slow EMA series
            
        Returns:
            pd.Series: 1 for bullish crossover, -1 for bearish, 0 for no signal
        """
        signals = pd.Series(0, index=fast_ema.index)
        
        # Bullish crossover: fast EMA crosses above slow EMA
        bullish_cross = (fast_ema > slow_ema) & (fast_ema.shift(1) <= slow_ema.shift(1))
        signals[bullish_cross] = 1
        
        # Bearish crossover: fast EMA crosses below slow EMA  
        bearish_cross = (fast_ema < slow_ema) & (fast_ema.shift(1) >= slow_ema.shift(1))
        signals[bearish_cross] = -1
        
        return signals

# Test the indicators
if __name__ == "__main__":
    print("🧪 Testing Moving Average Indicators")
    print("=" * 50)
    
    # Create sample data
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    
    from data_handler.csv_handler import CSVDataHandler
    
    # Generate sample data
    handler = CSVDataHandler()
    df = handler.generate_sample_data("NIFTY", days=2)
    
    print(f"📊 Testing with {len(df)} data points")
    
    # Test EMA calculations
    ema_9 = MovingAverages.ema(df['close'], 9)
    ema_21 = MovingAverages.ema(df['close'], 21)
    
    print(f"✅ EMA 9 calculated: {ema_9.notna().sum()} valid values")
    print(f"✅ EMA 21 calculated: {ema_21.notna().sum()} valid values")
    
    # Test SMA
    sma_9 = MovingAverages.sma(df['close'], 9)
    print(f"✅ SMA 9 calculated: {sma_9.notna().sum()} valid values")
    
    # Test VWAP
    vwap = MovingAverages.vwap(df)
    print(f"✅ VWAP calculated: {vwap.notna().sum()} valid values")
    
    # Test crossover signals
    crossover_signals = MovingAverages.ema_crossover(ema_9, ema_21)
    bullish_signals = (crossover_signals == 1).sum()
    bearish_signals = (crossover_signals == -1).sum()
    
    print(f"✅ Crossover signals - Bullish: {bullish_signals}, Bearish: {bearish_signals}")
    
    # Show sample calculations
    print(f"\n📈 Sample Values (last 5 rows):")
    results_df = pd.DataFrame({
        'Close': df['close'].tail(5),
        'EMA_9': ema_9.tail(5),
        'EMA_21': ema_21.tail(5),
        'VWAP': vwap.tail(5),
        'Signal': crossover_signals.tail(5)
    })
    print(results_df.round(2).to_string())
    
    print(f"\n🎉 Moving Average indicators test completed!")
