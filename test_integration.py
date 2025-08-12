import sys
sys.path.append('src')

print("🧪 Integration Test")
print("=" * 30)

try:
    # Test CSV Handler
    from data_handler.csv_handler import CSVDataHandler
    handler = CSVDataHandler()
    df = handler.generate_sample_data("NIFTY", 2)
    print(f"✅ CSV Handler: {len(df)} bars generated")
    
    # Test Indicators
    from indicators.moving_averages import MovingAverages
    ema_9 = MovingAverages.ema(df['close'], 9)
    ema_21 = MovingAverages.ema(df['close'], 21)
    print(f"✅ Indicators: EMA calculated")
    
    # Test signal generation
    signals = MovingAverages.ema_crossover(ema_9, ema_21)
    print(f"✅ Signals: {(signals != 0).sum()} crossover signals found")
    
    print(f"\n🎉 Integration test passed! Ready for next phase.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
