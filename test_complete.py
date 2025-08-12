import sys
sys.path.append('src')

print("🧪 Complete Integration Test")
print("=" * 40)

try:
    # Test 1: CSV Handler
    from data_handler.csv_handler import CSVDataHandler
    handler = CSVDataHandler()
    df = handler.generate_sample_data("NIFTY", 2)
    print(f"✅ CSV: {len(df)} bars generated")
    
    # Test 2: Technical Indicators
    from indicators.moving_averages import MovingAverages
    ema_9 = MovingAverages.ema(df['close'], 9)
    ema_21 = MovingAverages.ema(df['close'], 21)
    vwap = MovingAverages.vwap(df)
    signals = MovingAverages.ema_crossover(ema_9, ema_21)
    print(f"✅ Indicators: EMA, VWAP calculated")
    
    # Test 3: Database
    from data_handler.database import TradingDatabase
    db = TradingDatabase("data/test_complete.db")
    
    # Insert data to database
    rows_inserted = db.insert_historical_data(df, "NIFTY", "1m")
    print(f"✅ Database: {rows_inserted} rows inserted")
    
    # Retrieve data
    retrieved_df = db.get_historical_data("NIFTY", "1m", limit=10)
    print(f"✅ Database: {len(retrieved_df)} rows retrieved")
    
    # Test trade insertion
    from datetime import datetime
    trade_data = {
        'trade_id': 'COMPLETE_TEST_001',
        'symbol': 'NIFTY22000CE',
        'side': 'BUY',
        'quantity': 100,
        'entry_price': 45.5,
        'entry_time': datetime.now(),
        'strategy': 'EMA_Crossover',
        'notes': 'Complete integration test'
    }
    
    db.insert_trade(trade_data)
    print(f"✅ Trade: Sample trade inserted")
    
    # Get database stats
    stats = db.get_database_stats()
    print(f"✅ Stats: {stats.get('historical_data_count', 0)} historical records")
    
    print(f"\n📊 Summary:")
    print(f"   - Data points: {len(df)}")
    print(f"   - EMA crossovers: {(signals != 0).sum()}")
    print(f"   - Database records: {stats.get('historical_data_count', 0)}")
    print(f"   - Trade records: {stats.get('trades_count', 0)}")
    
    print(f"\n🎉 All components working! Ready for strategy development.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
