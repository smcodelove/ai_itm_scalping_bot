"""
Database handler for AI ITM Scalping Bot - FIXED VERSION
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import os
import json

class TradingDatabase:
    def __init__(self, db_path: str = "data/trading_data.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()
        
    def init_database(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                self._create_tables(cursor)
                conn.commit()
                print(f"✅ Database initialized: {self.db_path}")
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
    
    def _create_tables(self, cursor):
        # Historical data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historical_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume INTEGER NOT NULL,
                vwap REAL,
                trades INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, timeframe, timestamp)
            )
        ''')
        
        # Trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id TEXT UNIQUE NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                entry_price REAL NOT NULL,
                exit_price REAL,
                entry_time TEXT NOT NULL,
                exit_time TEXT,
                pnl REAL DEFAULT 0,
                status TEXT DEFAULT 'OPEN',
                strategy TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Signals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_id TEXT UNIQUE NOT NULL,
                symbol TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                price REAL NOT NULL,
                confidence REAL NOT NULL,
                strategy TEXT NOT NULL,
                executed BOOLEAN DEFAULT FALSE,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    def insert_historical_data(self, df: pd.DataFrame, symbol: str, timeframe: str) -> int:
        if df.empty:
            return 0
        
        try:
            data_to_insert = []
            for _, row in df.iterrows():
                # Convert timestamp to string for SQLite compatibility
                timestamp_str = str(row['timestamp'])
                if hasattr(row['timestamp'], 'strftime'):
                    timestamp_str = row['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                
                data_to_insert.append((
                    symbol,
                    timeframe,
                    timestamp_str,
                    float(row['open']),
                    float(row['high']),
                    float(row['low']),
                    float(row['close']),
                    int(row['volume']),
                    float(row.get('vwap', 0)),
                    int(row.get('trades', 0))
                ))
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.executemany('''
                    INSERT OR REPLACE INTO historical_data 
                    (symbol, timeframe, timestamp, open, high, low, close, volume, vwap, trades)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', data_to_insert)
                
                conn.commit()
                rows_inserted = len(data_to_insert)
                print(f"✅ Inserted {rows_inserted} rows of {symbol} {timeframe} data")
                return rows_inserted
                
        except Exception as e:
            print(f"❌ Error inserting historical data: {e}")
            return 0
    
    def get_historical_data(self, symbol: str, timeframe: str, limit: int = None) -> pd.DataFrame:
        try:
            query = '''
                SELECT timestamp, open, high, low, close, volume, vwap, trades
                FROM historical_data
                WHERE symbol = ? AND timeframe = ?
                ORDER BY timestamp
            '''
            params = [symbol, timeframe]
            
            if limit:
                query += f' LIMIT {limit}'
            
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(query, conn, params=params)
                
                if not df.empty:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                print(f"✅ Retrieved {len(df)} rows of {symbol} {timeframe} data")
                return df
                
        except Exception as e:
            print(f"❌ Error retrieving historical data: {e}")
            return pd.DataFrame()
    
    def insert_trade(self, trade_data: Dict[str, Any]) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Convert datetime to string
                entry_time_str = str(trade_data['entry_time'])
                if hasattr(trade_data['entry_time'], 'strftime'):
                    entry_time_str = trade_data['entry_time'].strftime('%Y-%m-%d %H:%M:%S')
                
                cursor.execute('''
                    INSERT INTO trades 
                    (trade_id, symbol, side, quantity, entry_price, entry_time, strategy, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    trade_data['trade_id'],
                    trade_data['symbol'],
                    trade_data['side'],
                    trade_data['quantity'],
                    trade_data['entry_price'],
                    entry_time_str,
                    trade_data.get('strategy'),
                    trade_data.get('notes')
                ))
                
                conn.commit()
                print(f"✅ Trade inserted: {trade_data['trade_id']}")
                return True
                
        except Exception as e:
            print(f"❌ Error inserting trade: {e}")
            return False
    
    def update_trade(self, trade_id: str, update_data: Dict[str, Any]) -> bool:
        try:
            if not update_data:
                return False
            
            # Convert datetime fields to strings
            processed_data = {}
            for key, value in update_data.items():
                if hasattr(value, 'strftime'):
                    processed_data[key] = value.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    processed_data[key] = value
            
            set_clause = ', '.join([f"{key} = ?" for key in processed_data.keys()])
            query = f"UPDATE trades SET {set_clause} WHERE trade_id = ?"
            params = list(processed_data.values()) + [trade_id]
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                
                if cursor.rowcount > 0:
                    print(f"✅ Trade updated: {trade_id}")
                    return True
                else:
                    print(f"⚠️ Trade not found: {trade_id}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error updating trade: {e}")
            return False
    
    def get_trade_history(self, limit: int = None) -> pd.DataFrame:
        try:
            query = 'SELECT * FROM trades ORDER BY entry_time DESC'
            if limit:
                query += f' LIMIT {limit}'
            
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(query, conn)
                print(f"✅ Retrieved {len(df)} trade records")
                return df
                
        except Exception as e:
            print(f"❌ Error retrieving trades: {e}")
            return pd.DataFrame()
    
    def get_database_stats(self) -> Dict[str, Any]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                stats = {}
                
                tables = ['historical_data', 'trades', 'signals']
                for table in tables:
                    cursor.execute(f'SELECT COUNT(*) FROM {table}')
                    stats[f'{table}_count'] = cursor.fetchone()[0]
                
                if os.path.exists(self.db_path):
                    file_size = os.path.getsize(self.db_path)
                    stats['file_size_mb'] = round(file_size / 1024 / 1024, 2)
                
                return stats
                
        except Exception as e:
            print(f"❌ Error getting database stats: {e}")
            return {}

# Test
if __name__ == "__main__":
    print("🧪 Testing Fixed Trading Database")
    print("=" * 50)
    
    # Test with CSV data
    try:
        import sys, os
        sys.path.append(os.path.dirname(__file__))
        from csv_handler import CSVDataHandler
        
        db = TradingDatabase("data/test_fixed.db")
        handler = CSVDataHandler()
        sample_df = handler.generate_sample_data("NIFTY", days=2)
        
        # Insert data
        rows_inserted = db.insert_historical_data(sample_df, "NIFTY", "1m")
        
        # Retrieve data
        retrieved_df = db.get_historical_data("NIFTY", "1m", limit=5)
        print(f"\n�� Retrieved data sample:")
        print(retrieved_df.head())
        
        # Test trade
        trade_data = {
            'trade_id': 'FIXED_TEST_001',
            'symbol': 'NIFTY22000CE',
            'side': 'BUY',
            'quantity': 100,
            'entry_price': 45.5,
            'entry_time': datetime.now(),
            'strategy': 'ITM_Scalping'
        }
        
        db.insert_trade(trade_data)
        db.update_trade('FIXED_TEST_001', {'exit_price': 47.2, 'pnl': 170, 'status': 'CLOSED'})
        
        # Stats
        stats = db.get_database_stats()
        print(f"\n�� Database Stats:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        print(f"\n🎉 Fixed database test successful!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
