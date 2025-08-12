"""
CSV Data Handler for AI ITM Scalping Bot
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class CSVDataHandler:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.sample_dir = os.path.join(data_dir, "sample")
        os.makedirs(self.sample_dir, exist_ok=True)
        print(f"✅ CSV Handler initialized: {self.sample_dir}")
    
    def generate_sample_data(self, symbol: str = "NIFTY", days: int = 5) -> pd.DataFrame:
        """Generate sample OHLCV data"""
        print(f"📊 Generating {days} days of sample data for {symbol}")
        
        # Generate timestamps
        timestamps = []
        current_date = datetime.now() - timedelta(days=days)
        
        for day in range(days):
            trading_day = current_date + timedelta(days=day)
            if trading_day.weekday() >= 5:  # Skip weekends
                continue
            
            market_start = trading_day.replace(hour=9, minute=15, second=0, microsecond=0)
            for minute in range(100):  # 100 minutes of data per day
                timestamps.append(market_start + timedelta(minutes=minute))
        
        # Generate realistic price data
        np.random.seed(42)
        n_bars = len(timestamps)
        start_price = 22000
        
        data = []
        current_price = start_price
        
        for i, timestamp in enumerate(timestamps):
            # Random walk with small movements
            change = np.random.normal(0, 10)  # Average ±10 points
            current_price = max(current_price + change, 21000)  # Min 21000
            
            # Generate OHLC around current price
            open_price = current_price + np.random.normal(0, 5)
            high_price = max(open_price, current_price) + abs(np.random.normal(0, 15))
            low_price = min(open_price, current_price) - abs(np.random.normal(0, 15))
            volume = np.random.randint(10000, 100000)
            
            # Ensure valid OHLC relationships
            high_price = max(high_price, open_price, current_price)
            low_price = min(low_price, open_price, current_price)
            
            data.append({
                'timestamp': timestamp,
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(current_price, 2),
                'volume': volume,
                'vwap': round((high_price + low_price + current_price) / 3, 2)
            })
        
        df = pd.DataFrame(data)
        print(f"✅ Generated {len(df)} bars")
        print(f"   Price range: ₹{df['low'].min():.2f} - ₹{df['high'].max():.2f}")
        return df
    
    def save_sample_data(self, symbol: str = "NIFTY", days: int = 5) -> str:
        """Save sample data to CSV"""
        df = self.generate_sample_data(symbol, days)
        filename = f"{symbol}_sample_{days}days.csv"
        file_path = os.path.join(self.sample_dir, filename)
        df.to_csv(file_path, index=False)
        print(f"💾 Saved: {file_path}")
        return file_path
    
    def read_csv(self, file_path: str) -> pd.DataFrame:
        """Read CSV file with error handling"""
        try:
            df = pd.read_csv(file_path)
            print(f"✅ Loaded: {file_path} ({len(df)} rows)")
            return df
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            return pd.DataFrame()
    
    def validate_ohlcv_data(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validate OHLCV data"""
        errors = []
        
        if df.empty:
            errors.append("DataFrame is empty")
            return False, errors
        
        # Check required columns
        required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            errors.append(f"Missing columns: {missing_cols}")
        
        # Check OHLC relationships
        if all(col in df.columns for col in ['open', 'high', 'low', 'close']):
            invalid_high = df[df['high'] < df[['open', 'low', 'close']].max(axis=1)]
            if len(invalid_high) > 0:
                errors.append(f"Found {len(invalid_high)} invalid high values")
            
            invalid_low = df[df['low'] > df[['open', 'high', 'close']].min(axis=1)]
            if len(invalid_low) > 0:
                errors.append(f"Found {len(invalid_low)} invalid low values")
        
        is_valid = len(errors) == 0
        return is_valid, errors

# Test the handler
if __name__ == "__main__":
    print("🧪 Testing CSV Data Handler")
    print("=" * 50)
    
    # Initialize handler
    handler = CSVDataHandler()
    
    # Generate and save sample data
    sample_file = handler.save_sample_data("NIFTY", days=3)
    
    # Read back and validate
    df = handler.read_csv(sample_file)
    
    if not df.empty:
        is_valid, errors = handler.validate_ohlcv_data(df)
        
        print(f"\n📋 Data Validation:")
        print(f"Valid: {is_valid}")
        if errors:
            for error in errors:
                print(f"❌ {error}")
        else:
            print("✅ All validation checks passed")
        
        print(f"\n📊 Sample Data:")
        print(df.head().to_string(index=False))
        
        print(f"\n🎉 CSV Handler test completed successfully!")
    else:
        print("❌ Failed to generate sample data")
