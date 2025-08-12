"""
GUI Components Package for AI ITM Scalping Bot
Modular components for professional trading interface
"""

# Import all component classes for easy access
from .market_overview import MarketOverviewPanel
from .order_management import OrderManagementPanel  
from .quick_trade_panel import QuickTradePanel
from .charts_panel import ChartsPanel
from .performance_dashboard import PerformanceDashboard

__all__ = [
    'MarketOverviewPanel',
    'OrderManagementPanel', 
    'QuickTradePanel',
    'ChartsPanel',
    'PerformanceDashboard'
]

__version__ = "2.0.0"
__author__ = "AI ITM Scalping Bot Team"