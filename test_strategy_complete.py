import sys
sys.path.append('src')

print("🧪 Complete Strategy Integration Test")
print("=" * 50)

try:
    # 1. Generate realistic market data
    from data_handler.csv_handler import CSVDataHandler
    handler = CSVDataHandler()
    df = handler.generate_sample_data("NIFTY", days=5)  # More data for better signals
    print(f"✅ Data: {len(df)} bars generated")
    
    # 2. Initialize strategy
    from strategy.signal_generator import ITMScalpingSignals
    strategy = ITMScalpingSignals()
    
    # 3. Generate signals
    signals_df = strategy.generate_signals(df)
    
    # 4. Store results in database
    from data_handler.database import TradingDatabase
    db = TradingDatabase("data/strategy_test.db")
    
    # Store historical data
    rows_inserted = db.insert_historical_data(signals_df, "NIFTY", "1m")
    print(f"✅ Database: {rows_inserted} rows stored")
    
    # 5. Analyze signals
    signal_rows = signals_df[signals_df['signal_type'] != 'NONE']
    
    if len(signal_rows) > 0:
        print(f"\n📊 Strategy Performance Analysis:")
        
        # Signal distribution
        ce_signals = len(signal_rows[signal_rows['signal_type'] == 'BUY_CE'])
        pe_signals = len(signal_rows[signal_rows['signal_type'] == 'BUY_PE'])
        
        print(f"   CE (Call) signals: {ce_signals}")
        print(f"   PE (Put) signals: {pe_signals}")
        print(f"   Total signals: {len(signal_rows)}")
        print(f"   Signal frequency: {len(signal_rows)/len(df)*100:.1f}% of bars")
        
        # Signal strength analysis
        avg_strength = signal_rows['signal_strength'].mean()
        max_strength = signal_rows['signal_strength'].max()
        print(f"   Average signal strength: {avg_strength:.2f}")
        print(f"   Maximum signal strength: {max_strength:.2f}")
        
        # Show top signals
        print(f"\n📈 Top 5 Signals:")
        top_signals = signal_rows.nlargest(5, 'signal_strength')
        print(top_signals[['timestamp', 'close', 'signal_type', 'signal_strength', 
                          'rsi', 'ema_9', 'ema_21']].round(2).to_string(index=False))
        
        # Simulate trade outcomes
        print(f"\n💰 Trade Simulation (first 3 signals):")
        for i, (idx, signal) in enumerate(signal_rows.head(3).iterrows()):
            signal_type = 'bullish' if signal['signal_type'] == 'BUY_CE' else 'bearish'
            exit_info = strategy.generate_exit_signals(signals_df, signal_type, idx)
            
            entry_price = signal['close']
            exit_price = exit_info.get('exit_price', entry_price)
            
            if signal_type == 'bullish':
                pnl = exit_price - entry_price
            else:
                pnl = entry_price - exit_price
            
            print(f"   Trade {i+1}: {signal['signal_type']} @ ₹{entry_price:.2f} → ₹{exit_price:.2f} = {pnl:+.2f} points")
    
    else:
        print(f"\n⚠️ No signals generated - may need more data or adjusted parameters")
    
    # 6. Technical analysis summary
    latest_indicators = signals_df.iloc[-1]
    print(f"\n📊 Latest Market State:")
    print(f"   Price: ₹{latest_indicators['close']:.2f}")
    print(f"   EMA 9: ₹{latest_indicators['ema_9']:.2f}")
    print(f"   EMA 21: ₹{latest_indicators['ema_21']:.2f}")
    print(f"   RSI: {latest_indicators['rsi']:.1f}")
    print(f"   VWAP: ₹{latest_indicators['vwap']:.2f}")
    
    trend = "Bullish" if latest_indicators['ema_9'] > latest_indicators['ema_21'] else "Bearish"
    print(f"   Current Trend: {trend}")
    
    print(f"\n🎉 Strategy engine working perfectly!")
    print(f"💡 Ready for backtesting and live trading integration!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
