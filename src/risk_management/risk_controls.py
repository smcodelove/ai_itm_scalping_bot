"""
Risk Management System for AI ITM Scalping Bot - FIXED VERSION
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import sys
import os

class RiskManager:
    """Comprehensive risk management system for ITM scalping"""
    
    def __init__(self, config: Dict = None):
        self.config = config or self._default_config()
        self.current_positions = []
        self.daily_stats = {
            'trades_today': 0,
            'pnl_today': 0,
            'max_drawdown_today': 0,
            'start_capital': 0
        }
        
    def _default_config(self) -> Dict:
        """Default risk management configuration from PRD"""
        return {
            'max_risk_per_trade': 0.02,
            'max_position_size': 50000,
            'min_position_size': 5000,
            'max_daily_loss': 0.05,
            'max_concurrent_positions': 3,
            'max_exposure': 1.0,
            'max_correlation': 0.8,
            'max_drawdown': 0.15,
            'circuit_breaker': 0.20,
            'max_trades_per_day': 50,
            'cooling_period_minutes': 5,
            'avoid_news_minutes': 30,
            'max_vix_level': 35,
            'min_volume': 1000,
            'max_spread': 2.0,
            'emergency_exit_loss': 0.10,
            'profit_protection': 0.50,
            'step_down_after_loss': True,
        }
    
    def check_pre_trade_risk(self, trade_signal: Dict, current_capital: float, 
                           market_data: pd.Series) -> Tuple[bool, str, float]:
        """Comprehensive pre-trade risk assessment"""
        
        # 1. Capital adequacy check
        if current_capital <= self.config['min_position_size']:
            return False, "Insufficient capital for minimum position", 0
        
        # 2. Daily loss limit check
        daily_loss_pct = abs(self.daily_stats['pnl_today']) / self.daily_stats['start_capital'] if self.daily_stats['start_capital'] > 0 else 0
        if self.daily_stats['pnl_today'] < 0 and daily_loss_pct >= self.config['max_daily_loss']:
            return False, f"Daily loss limit reached: {daily_loss_pct:.2%}", 0
        
        # 3. Maximum positions check
        if len(self.current_positions) >= self.config['max_concurrent_positions']:
            return False, f"Maximum positions limit reached: {len(self.current_positions)}", 0
        
        # 4. Daily trades limit
        if self.daily_stats['trades_today'] >= self.config['max_trades_per_day']:
            return False, f"Daily trades limit reached: {self.daily_stats['trades_today']}", 0
        
        # 5. Calculate optimal position size
        suggested_size = self.calculate_position_size(trade_signal, current_capital, market_data)
        
        # 6. Position size validation
        if suggested_size > self.config['max_position_size']:
            suggested_size = self.config['max_position_size']
        elif suggested_size < self.config['min_position_size']:
            return False, f"Calculated position size too small: ₹{suggested_size:.0f}", 0
        
        return True, "Risk check passed", suggested_size
    
    def calculate_position_size(self, trade_signal: Dict, current_capital: float, 
                              market_data: pd.Series) -> float:
        """Calculate optimal position size using Kelly Criterion + safety factors"""
        
        # Base position size (% of capital)
        base_size_pct = self.config['max_risk_per_trade']
        
        # Adjust based on signal strength
        signal_strength = trade_signal.get('signal_strength', 0.5)
        strength_multiplier = min(signal_strength * 2, 1.0)
        
        # Adjust based on recent performance
        if self.daily_stats['pnl_today'] < 0 and self.config['step_down_after_loss']:
            performance_multiplier = 0.5
        elif self.daily_stats['pnl_today'] > 0:
            performance_multiplier = 1.2
        else:
            performance_multiplier = 1.0
        
        # Calculate final position size
        final_size_pct = base_size_pct * strength_multiplier * performance_multiplier
        final_size_pct = min(final_size_pct, self.config['max_risk_per_trade'] * 1.5)
        
        position_size = current_capital * final_size_pct
        return max(position_size, self.config['min_position_size'])
    
    def monitor_position_risk(self, position: Dict, current_market_data: pd.Series) -> Dict:
        """Monitor existing position for risk violations"""
        
        risk_assessment = {
            'status': 'OK',
            'alerts': [],
            'recommendations': [],
            'emergency_exit': False
        }
        
        # Calculate current P&L
        current_price = current_market_data.get('close', position['entry_price'])
        
        if position['side'] == 'BUY':
            pnl_points = current_price - position['entry_price']
        else:
            pnl_points = position['entry_price'] - current_price
        
        pnl_amount = pnl_points * position['quantity']
        pnl_pct = pnl_amount / position['position_value']
        
        # Stop loss check
        if pnl_pct <= -self.config['max_risk_per_trade']:
            risk_assessment['status'] = 'STOP_LOSS'
            risk_assessment['recommendations'].append('Execute stop loss immediately')
            risk_assessment['emergency_exit'] = True
        
        # Time-based risk
        hold_time = (datetime.now() - position['entry_time']).total_seconds() / 60
        if hold_time > 10:
            risk_assessment['alerts'].append(f'Position held for {hold_time:.1f} minutes')
            risk_assessment['recommendations'].append('Consider profit taking or exit')
        
        return risk_assessment
    
    def update_daily_stats(self, trade_pnl: float = 0, new_trade: bool = False):
        """Update daily trading statistics"""
        if new_trade:
            self.daily_stats['trades_today'] += 1
        
        if trade_pnl != 0:
            self.daily_stats['pnl_today'] += trade_pnl
            if self.daily_stats['pnl_today'] < self.daily_stats['max_drawdown_today']:
                self.daily_stats['max_drawdown_today'] = self.daily_stats['pnl_today']
    
    def check_emergency_conditions(self, current_capital: float) -> Tuple[bool, str]:
        """Check for emergency stop conditions"""
        
        # Circuit breaker - total capital loss
        if self.daily_stats['start_capital'] > 0:
            total_loss_pct = (self.daily_stats['start_capital'] - current_capital) / self.daily_stats['start_capital']
            if total_loss_pct >= self.config['circuit_breaker']:
                return True, f"CIRCUIT BREAKER: {total_loss_pct:.2%} capital loss"
        
        # Daily loss limit
        if self.daily_stats['start_capital'] > 0:
            daily_loss_pct = abs(self.daily_stats['pnl_today']) / self.daily_stats['start_capital']
            if (self.daily_stats['pnl_today'] < 0 and 
                daily_loss_pct >= self.config['emergency_exit_loss']):
                return True, f"EMERGENCY: {daily_loss_pct:.2%} daily loss"
        
        return False, ""
    
    def add_position(self, position: Dict):
        """Add new position to monitoring"""
        self.current_positions.append(position)
        self.update_daily_stats(new_trade=True)
    
    def remove_position(self, position_id: str, pnl: float = 0):
        """Remove position from monitoring"""
        self.current_positions = [
            pos for pos in self.current_positions 
            if pos.get('id') != position_id
        ]
        self.update_daily_stats(trade_pnl=pnl)
    
    def reset_daily_stats(self, starting_capital: float):
        """Reset daily statistics (call at market open)"""
        self.daily_stats = {
            'trades_today': 0,
            'pnl_today': 0,
            'max_drawdown_today': 0,
            'start_capital': starting_capital
        }
        self.current_positions = []
    
    def get_risk_report(self) -> Dict:
        """Generate comprehensive risk report"""
        return {
            'daily_stats': self.daily_stats.copy(),
            'current_positions': len(self.current_positions),
            'risk_limits': {
                'daily_loss_used': abs(self.daily_stats['pnl_today']) / self.daily_stats['start_capital'] 
                                 if self.daily_stats['start_capital'] > 0 else 0,
                'daily_loss_limit': self.config['max_daily_loss'],
                'trades_used': self.daily_stats['trades_today'],
                'trades_limit': self.config['max_trades_per_day'],
                'positions_used': len(self.current_positions),
                'positions_limit': self.config['max_concurrent_positions']
            },
            'alerts': [],
            'recommendations': []
        }

# Test the risk manager
if __name__ == "__main__":
    print("🧪 Testing Risk Management System")
    print("=" * 50)
    
    # Initialize risk manager
    risk_manager = RiskManager()
    risk_manager.reset_daily_stats(100000)
    
    print(f"💰 Starting capital: ₹{risk_manager.daily_stats['start_capital']:,.0f}")
    
    # Test pre-trade risk check
    test_signal = {
        'signal_type': 'BUY_CE',
        'signal_strength': 0.75,
        'symbol': 'NIFTY22000CE'
    }
    
    test_market_data = pd.Series({
        'close': 22000,
        'volume': 50000,
        'volatility': 0.015
    })
    
    can_trade, message, size = risk_manager.check_pre_trade_risk(
        test_signal, 100000, test_market_data
    )
    
    print(f"\n🎯 Pre-trade Risk Check:")
    print(f"   Can trade: {can_trade}")
    print(f"   Message: {message}")
    print(f"   Suggested size: ₹{size:,.0f}")
    
    # Test position monitoring
    if can_trade:
        position = {
            'id': 'TEST_001',
            'signal_type': 'BUY_CE',
            'entry_price': 22000,
            'entry_time': datetime.now(),
            'quantity': 100,
            'position_value': size,
            'side': 'BUY'
        }
        
        risk_manager.add_position(position)
        print(f"✅ Position added. Current positions: {len(risk_manager.current_positions)}")
        
        # Monitor position
        risk_assessment = risk_manager.monitor_position_risk(position, test_market_data)
        print(f"\n📊 Position Risk Assessment:")
        print(f"   Status: {risk_assessment['status']}")
        print(f"   Emergency exit: {risk_assessment['emergency_exit']}")
    
    # Test emergency conditions
    risk_manager.update_daily_stats(trade_pnl=-2000)
    emergency, emergency_msg = risk_manager.check_emergency_conditions(98000)
    
    print(f"\n🚨 Emergency Check:")
    print(f"   Emergency stop: {emergency}")
    if emergency:
        print(f"   Reason: {emergency_msg}")
    
    # Risk report
    risk_report = risk_manager.get_risk_report()
    print(f"\n📋 Risk Report:")
    print(f"   Daily P&L: ₹{risk_report['daily_stats']['pnl_today']:,.0f}")
    print(f"   Trades today: {risk_report['daily_stats']['trades_today']}")
    print(f"   Daily loss used: {risk_report['risk_limits']['daily_loss_used']:.2%}")
    print(f"   Trades used: {risk_report['risk_limits']['trades_used']}/{risk_report['risk_limits']['trades_limit']}")
    print(f"   Positions: {risk_report['risk_limits']['positions_used']}/{risk_report['risk_limits']['positions_limit']}")
    
    print(f"\n🎉 Risk management system test completed!")
