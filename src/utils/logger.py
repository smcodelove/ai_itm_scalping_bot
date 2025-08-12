"""
Logging utility for AI ITM Scalping Bot
Provides structured logging with file rotation and console output
"""

import logging
import logging.handlers
import os
from datetime import datetime
import json

class TradingLogger:
    """Enhanced logger for trading applications"""
    
    def __init__(self, name="TradingBot", config_path="config/settings.json"):
        self.name = name
        self.logger = logging.getLogger(name)
        self.config = self._load_config(config_path)
        self._setup_logger()
    
    def _load_config(self, config_path):
        """Load logging configuration from settings"""
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                return config.get('logging', {})
        except Exception as e:
            print(f"Config load error: {e}")
        
        # Default config if file not found
        return {
            "level": "INFO",
            "file_path": "logs/trading_bot.log",
            "max_size_mb": 100,
            "backup_count": 5
        }
    
    def _setup_logger(self):
        """Setup logger with file and console handlers"""
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Set logging level
        level = getattr(logging, self.config.get('level', 'INFO').upper())
        self.logger.setLevel(level)
        
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(self.config.get('file_path', 'logs/trading_bot.log'))
        os.makedirs(log_dir, exist_ok=True)
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            self.config.get('file_path', 'logs/trading_bot.log'),
            maxBytes=self.config.get('max_size_mb', 100) * 1024 * 1024,
            backupCount=self.config.get('backup_count', 5)
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message, **kwargs):
        """Log info message"""
        self.logger.info(self._format_message(message, **kwargs))
    
    def warning(self, message, **kwargs):
        """Log warning message"""
        self.logger.warning(self._format_message(message, **kwargs))
    
    def error(self, message, **kwargs):
        """Log error message"""
        self.logger.error(self._format_message(message, **kwargs))
    
    def debug(self, message, **kwargs):
        """Log debug message"""
        self.logger.debug(self._format_message(message, **kwargs))
    
    def critical(self, message, **kwargs):
        """Log critical message"""
        self.logger.critical(self._format_message(message, **kwargs))
    
    def trade_signal(self, signal_type, symbol, price, confidence, **kwargs):
        """Log trading signals with structured format"""
        message = f"SIGNAL | {signal_type} | {symbol} | Price: ₹{price} | Confidence: {confidence:.2%}"
        self.info(message, signal_type=signal_type, symbol=symbol, price=price, confidence=confidence, **kwargs)
    
    def trade_execution(self, action, symbol, quantity, price, order_id=None, **kwargs):
        """Log trade executions"""
        message = f"TRADE | {action} | {symbol} | Qty: {quantity} | Price: ₹{price}"
        if order_id:
            message += f" | Order: {order_id}"
        self.info(message, action=action, symbol=symbol, quantity=quantity, price=price, order_id=order_id, **kwargs)
    
    def performance_update(self, total_pnl, daily_pnl, win_rate, trades_today, **kwargs):
        """Log performance metrics"""
        message = f"PERFORMANCE | Total P&L: ₹{total_pnl:.2f} | Today: ₹{daily_pnl:.2f} | Win Rate: {win_rate:.1%} | Trades: {trades_today}"
        self.info(message, total_pnl=total_pnl, daily_pnl=daily_pnl, win_rate=win_rate, trades_today=trades_today, **kwargs)
    
    def system_health(self, cpu_percent, memory_mb, latency_ms, **kwargs):
        """Log system health metrics"""
        message = f"SYSTEM | CPU: {cpu_percent:.1f}% | Memory: {memory_mb:.0f}MB | Latency: {latency_ms:.1f}ms"
        self.info(message, cpu_percent=cpu_percent, memory_mb=memory_mb, latency_ms=latency_ms, **kwargs)
    
    def _format_message(self, message, **kwargs):
        """Format message with additional context"""
        if kwargs:
            context = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
            return f"{message} | {context}"
        return message

# Global logger instance
logger = TradingLogger()

# Convenience functions
def info(message, **kwargs):
    logger.info(message, **kwargs)

def warning(message, **kwargs):
    logger.warning(message, **kwargs)

def error(message, **kwargs):
    logger.error(message, **kwargs)

def debug(message, **kwargs):
    logger.debug(message, **kwargs)

def critical(message, **kwargs):
    logger.critical(message, **kwargs)

# Test the logger
if __name__ == "__main__":
    logger.info("Trading bot logger initialized successfully!")
    logger.trade_signal("BUY", "NIFTY22000CE", 45.5, 0.85)
    logger.trade_execution("BUY", "NIFTY22000CE", 100, 45.5, "ORD123456")
    logger.performance_update(2500.75, 450.25, 0.68, 12)
    logger.system_health(45.2, 512, 85.5)