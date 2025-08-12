import sys
sys.path.append('src')

print("🧪 Complete Indicators Test")
print("=" * 40)

try:
    # Generate data
    from data_handler.csv_handler import CSVDataHandler
    handler = CSVDataHandler()
    df = handler.generate_sample_data("NIFTY", 3)
    print(f"✅ Data: {len(df)} bars generated")
    
    # Test Moving Averages
    from indicators.moving_averages import MovingAverages
    ema_9 = MovingAverages.ema(df['close'], 9)
    ema_21 = MovingAverages.ema(df['close'], 21)
    vwap = MovingAverages.vwap(df)
    ema_signals = MovingAverages.ema_crossover(ema_9, ema_21)
    print(f"✅ Moving Averages: EMA crossovers = {(ema_signals != 0).sum()}")
    
    # Test Momentum Indicators
    from indicators.momentum import MomentumIndicators
    rsi = MomentumIndicators.rsi(df['close'])
    macd_line, signal_line, histogram = MomentumIndicators.macd(df['close'])
    rsi_signals = MomentumIndicators.rsi_signals(rsi)
    macd_signals = MomentumIndicators.macd_signals(macd_line, signal_line)
    print(f"✅ Momentum: RSI signals = {(rsi_signals != 0).sum()}, MACD signals = {(macd_signals != 0).sum()}")
    
    # Test Database (fixed version)
    from data_handler.database import TradingDatabase
    db = TradingDatabase("data/test_all.db")
    rows_inserted = db.insert_historical_data(df, "NIFTY", "1m")
    print(f"✅ Database: {rows_inserted} rows inserted successfully")
    
    # Combined analysis
    print(f"\n📊 Technical Analysis Summary:")
    print(f"   - Data points: {len(df)}")
    print(f"   - EMA (9): {ema_9.iloc[-1]:.2f}")
    print(f"   - EMA (21): {ema_21.iloc[-1]:.2f}")
    print(f"   - RSI: {rsi.iloc[-1]:.2f}")
    print(f"   - MACD: {macd_line.iloc[-1]:.2f}")
    print(f"   - VWAP: {vwap.iloc[-1]:.2f}")
    
    # Signal summary
    total_ema_signals = (ema_signals != 0).sum()
    total_rsi_signals = (rsi_signals != 0).sum()
    total_macd_signals = (macd_signals != 0).sum()
    
    print(f"\n📈 Signal Summary:")
    print(f"   - EMA crossovers: {total_ema_signals}")
    print(f"   - RSI signals: {total_rsi_signals}")
    print(f"   - MACD signals: {total_macd_signals}")
    print(f"   - Total signals: {total_ema_signals + total_rsi_signals + total_macd_signals}")
    
    print(f"\n🎉 All indicators working perfectly! Ready for strategy engine.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
