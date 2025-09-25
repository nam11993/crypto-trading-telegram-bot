#!/usr/bin/env python3
"""
💼 Advanced Portfolio Manager
- Multi-symbol portfolio tracking
- Risk distribution
- Dynamic position sizing
- Portfolio-level risk management
- Performance analytics
"""
import logging
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from config.config import Config

@dataclass
class Position:
    """Đại diện cho 1 position"""
    symbol: str
    side: str  # 'LONG' or 'SHORT'
    entry_price: float
    quantity: float
    entry_time: datetime
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    unrealized_pnl: float = 0.0
    unrealized_pnl_percent: float = 0.0

@dataclass
class PortfolioMetrics:
    """Portfolio performance metrics"""
    total_value: float
    total_pnl: float
    total_pnl_percent: float
    win_rate: float
    max_drawdown: float
    sharpe_ratio: float
    num_positions: int
    active_positions: int

class AdvancedPortfolioManager:
    """Quản lý portfolio multi-symbol với risk management"""
    
    def __init__(self, symbols: List[str] = None, initial_balance: float = 10000):
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.symbols = symbols or ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'BNBUSDT', 'SOLUSDT']
        self.initial_balance = initial_balance
        
        # Portfolio state
        self.positions: Dict[str, Position] = {}
        self.closed_positions: List[Position] = []
        self.balance = initial_balance
        self.reserved_balance = 0.0  # For open orders
        
        # Risk management settings
        self.max_position_size_percent = 20  # Max 20% per position
        self.max_portfolio_risk = 10  # Max 10% portfolio risk
        self.max_correlation_exposure = 30  # Max 30% in correlated assets
        self.max_drawdown_limit = 15  # Stop if drawdown > 15%
        
        # Performance tracking
        self.daily_pnl: List[float] = []
        self.equity_curve: List[Tuple[datetime, float]] = []
        self.trade_history: List[Dict] = []
        
        # Symbol allocations (dynamic)
        self.symbol_weights = self._calculate_initial_weights()
        
        self.logger.info(f"Portfolio Manager initialized with {len(self.symbols)} symbols")
        self.logger.info(f"Initial balance: ${initial_balance:,.2f}")
    
    def _calculate_initial_weights(self) -> Dict[str, float]:
        """Tính trọng số ban đầu cho các symbols"""
        # Phân bổ đều ban đầu, sau sẽ dynamic dựa trên performance
        equal_weight = 1.0 / len(self.symbols)
        return {symbol: equal_weight for symbol in self.symbols}
    
    def calculate_position_size(self, symbol: str, current_price: float, 
                              volatility: float = None) -> float:
        """Tính kích thước position dựa trên risk management"""
        try:
            # Available balance for this position
            available_balance = self.balance - self.reserved_balance
            
            # Base position size from symbol weight
            symbol_weight = self.symbol_weights.get(symbol, 0.2)  # Default 20%
            base_size = available_balance * symbol_weight
            
            # Adjust for volatility (if available)
            if volatility:
                # Higher volatility = smaller position
                volatility_multiplier = min(1.0, 0.1 / volatility)  # Cap at 10% volatility
                base_size *= volatility_multiplier
            
            # Apply maximum position size limit
            max_position_value = self.balance * (self.max_position_size_percent / 100)
            position_value = min(base_size, max_position_value)
            
            # Convert to quantity
            quantity = position_value / current_price
            
            self.logger.debug(f"Position size for {symbol}: ${position_value:.2f} ({quantity:.6f})")
            return quantity
            
        except Exception as e:
            self.logger.error(f"Error calculating position size for {symbol}: {e}")
            return 0.0
    
    def open_position(self, symbol: str, side: str, current_price: float,
                     stop_loss: float = None, take_profit: float = None) -> bool:
        """Mở position mới"""
        try:
            # Check if position already exists
            if symbol in self.positions:
                self.logger.warning(f"Position already exists for {symbol}")
                return False
            
            # Calculate position size
            quantity = self.calculate_position_size(symbol, current_price)
            
            if quantity <= 0:
                self.logger.warning(f"Invalid quantity for {symbol}: {quantity}")
                return False
            
            # Calculate position value
            position_value = quantity * current_price
            
            # Check if we have enough balance
            if position_value > (self.balance - self.reserved_balance):
                self.logger.warning(f"Insufficient balance for {symbol} position")
                return False
            
            # Create position
            position = Position(
                symbol=symbol,
                side=side,
                entry_price=current_price,
                quantity=quantity,
                entry_time=datetime.now(),
                stop_loss=stop_loss,
                take_profit=take_profit
            )
            
            self.positions[symbol] = position
            self.reserved_balance += position_value
            
            self.logger.info(f"✅ Opened {side} position: {symbol} @ ${current_price:.4f} (Qty: {quantity:.6f})")
            
            # Record trade
            self.trade_history.append({
                'timestamp': datetime.now(),
                'action': 'OPEN',
                'symbol': symbol,
                'side': side,
                'price': current_price,
                'quantity': quantity,
                'value': position_value
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error opening position for {symbol}: {e}")
            return False
    
    def close_position(self, symbol: str, current_price: float, reason: str = "Manual") -> Optional[float]:
        """Đóng position"""
        try:
            if symbol not in self.positions:
                self.logger.warning(f"No position found for {symbol}")
                return None
            
            position = self.positions[symbol]
            
            # Calculate P&L
            if position.side == 'LONG':
                pnl = (current_price - position.entry_price) * position.quantity
            else:  # SHORT
                pnl = (position.entry_price - current_price) * position.quantity
            
            pnl_percent = (pnl / (position.entry_price * position.quantity)) * 100
            
            # Update balance
            position_value = position.quantity * current_price
            self.balance = self.balance - self.reserved_balance + position_value + pnl
            
            # Update reserved balance
            entry_value = position.quantity * position.entry_price
            self.reserved_balance -= entry_value
            
            # Update position with final P&L
            position.unrealized_pnl = pnl
            position.unrealized_pnl_percent = pnl_percent
            
            # Move to closed positions
            self.closed_positions.append(position)
            del self.positions[symbol]
            
            self.logger.info(f"✅ Closed {position.side} position: {symbol} @ ${current_price:.4f}")
            self.logger.info(f"💰 P&L: ${pnl:.2f} ({pnl_percent:+.2f}%) - Reason: {reason}")
            
            # Record trade
            self.trade_history.append({
                'timestamp': datetime.now(),
                'action': 'CLOSE',
                'symbol': symbol,
                'side': position.side,
                'price': current_price,
                'quantity': position.quantity,
                'pnl': pnl,
                'pnl_percent': pnl_percent,
                'reason': reason
            })
            
            return pnl
            
        except Exception as e:
            self.logger.error(f"Error closing position for {symbol}: {e}")
            return None
    
    def update_positions(self, price_data: Dict[str, float]):
        """Cập nhật tất cả positions với giá mới"""
        try:
            total_unrealized_pnl = 0.0
            
            for symbol, position in self.positions.items():
                if symbol in price_data:
                    current_price = price_data[symbol]
                    
                    # Calculate unrealized P&L
                    if position.side == 'LONG':
                        pnl = (current_price - position.entry_price) * position.quantity
                    else:  # SHORT
                        pnl = (position.entry_price - current_price) * position.quantity
                    
                    pnl_percent = (pnl / (position.entry_price * position.quantity)) * 100
                    
                    position.unrealized_pnl = pnl
                    position.unrealized_pnl_percent = pnl_percent
                    total_unrealized_pnl += pnl
            
            # Update equity curve
            current_equity = self.balance + total_unrealized_pnl
            self.equity_curve.append((datetime.now(), current_equity))
            
            # Keep only last 1000 equity points
            if len(self.equity_curve) > 1000:
                self.equity_curve.pop(0)
                
        except Exception as e:
            self.logger.error(f"Error updating positions: {e}")
    
    def check_risk_management(self, price_data: Dict[str, float]) -> List[str]:
        """Kiểm tra risk management và trả về list symbols cần đóng"""
        positions_to_close = []
        
        try:
            for symbol, position in self.positions.items():
                if symbol not in price_data:
                    continue
                
                current_price = price_data[symbol]
                
                # Check stop loss
                if position.stop_loss:
                    if position.side == 'LONG' and current_price <= position.stop_loss:
                        positions_to_close.append((symbol, "Stop Loss"))
                    elif position.side == 'SHORT' and current_price >= position.stop_loss:
                        positions_to_close.append((symbol, "Stop Loss"))
                
                # Check take profit
                if position.take_profit:
                    if position.side == 'LONG' and current_price >= position.take_profit:
                        positions_to_close.append((symbol, "Take Profit"))
                    elif position.side == 'SHORT' and current_price <= position.take_profit:
                        positions_to_close.append((symbol, "Take Profit"))
                
                # Check maximum loss per position (20% loss)
                if position.unrealized_pnl_percent < -20:
                    positions_to_close.append((symbol, "Max Loss Exceeded"))
            
            # Check portfolio-level drawdown
            current_equity = self.get_current_equity()
            if current_equity > 0:
                total_drawdown = ((self.initial_balance - current_equity) / self.initial_balance) * 100
                
                if total_drawdown > self.max_drawdown_limit:
                    self.logger.warning(f"🚨 Portfolio drawdown {total_drawdown:.2f}% exceeds limit!")
                    # Close all positions if drawdown too high
                    for symbol in self.positions:
                        if (symbol, "Portfolio Drawdown") not in positions_to_close:
                            positions_to_close.append((symbol, "Portfolio Drawdown"))
            
            return positions_to_close
            
        except Exception as e:
            self.logger.error(f"Error in risk management check: {e}")
            return []
    
    def get_current_equity(self) -> float:
        """Lấy equity hiện tại (balance + unrealized P&L)"""
        total_unrealized = sum(pos.unrealized_pnl for pos in self.positions.values())
        return self.balance + total_unrealized
    
    def get_portfolio_metrics(self) -> PortfolioMetrics:
        """Tính toán portfolio metrics"""
        try:
            current_equity = self.get_current_equity()
            total_pnl = current_equity - self.initial_balance
            total_pnl_percent = (total_pnl / self.initial_balance) * 100
            
            # Calculate win rate
            if self.closed_positions:
                winning_trades = len([pos for pos in self.closed_positions if pos.unrealized_pnl > 0])
                win_rate = (winning_trades / len(self.closed_positions)) * 100
            else:
                win_rate = 0.0
            
            # Calculate max drawdown
            if len(self.equity_curve) > 1:
                equity_values = [eq[1] for eq in self.equity_curve]
                peak = max(equity_values)
                trough = min(equity_values[equity_values.index(peak):]) if peak in equity_values else min(equity_values)
                max_drawdown = ((peak - trough) / peak) * 100 if peak > 0 else 0
            else:
                max_drawdown = 0.0
            
            # Calculate Sharpe ratio (simplified)
            if len(self.equity_curve) > 30:  # Need at least 30 data points
                returns = []
                for i in range(1, len(self.equity_curve)):
                    prev_equity = self.equity_curve[i-1][1]
                    curr_equity = self.equity_curve[i][1]
                    if prev_equity > 0:
                        returns.append((curr_equity - prev_equity) / prev_equity)
                
                if returns:
                    avg_return = np.mean(returns)
                    std_return = np.std(returns)
                    sharpe_ratio = avg_return / std_return if std_return > 0 else 0
                else:
                    sharpe_ratio = 0
            else:
                sharpe_ratio = 0
            
            return PortfolioMetrics(
                total_value=current_equity,
                total_pnl=total_pnl,
                total_pnl_percent=total_pnl_percent,
                win_rate=win_rate,
                max_drawdown=max_drawdown,
                sharpe_ratio=sharpe_ratio,
                num_positions=len(self.positions),
                active_positions=len(self.positions)
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating portfolio metrics: {e}")
            return PortfolioMetrics(0, 0, 0, 0, 0, 0, 0, 0)
    
    def get_portfolio_summary(self) -> str:
        """Tạo summary text của portfolio"""
        metrics = self.get_portfolio_metrics()
        
        summary = f"""
💼 PORTFOLIO SUMMARY

💰 EQUITY: ${metrics.total_value:,.2f}
📊 P&L: ${metrics.total_pnl:+,.2f} ({metrics.total_pnl_percent:+.2f}%)
🎯 WIN RATE: {metrics.win_rate:.1f}%
📉 MAX DRAWDOWN: {metrics.max_drawdown:.2f}%
📈 SHARPE RATIO: {metrics.sharpe_ratio:.2f}

🔢 POSITIONS: {metrics.active_positions} active
💵 AVAILABLE: ${self.balance - self.reserved_balance:,.2f}
🔒 RESERVED: ${self.reserved_balance:,.2f}

📋 ACTIVE POSITIONS:"""
        
        if self.positions:
            for symbol, pos in self.positions.items():
                summary += f"""
• {pos.side} {symbol}: ${pos.entry_price:.4f}
  P&L: ${pos.unrealized_pnl:+.2f} ({pos.unrealized_pnl_percent:+.2f}%)"""
        else:
            summary += "\nNo active positions"
        
        return summary
    
    def rebalance_weights(self, performance_data: Dict[str, float]):
        """Rebalance symbol weights dựa trên performance"""
        try:
            if not performance_data:
                return
            
            # Normalize performance scores
            total_score = sum(max(score, 0.1) for score in performance_data.values())  # Minimum 0.1
            
            for symbol in self.symbols:
                if symbol in performance_data:
                    # Better performance = higher weight
                    self.symbol_weights[symbol] = max(performance_data[symbol], 0.1) / total_score
                else:
                    self.symbol_weights[symbol] = 0.1 / len(self.symbols)  # Default weight
            
            self.logger.info("✅ Portfolio weights rebalanced")
            
        except Exception as e:
            self.logger.error(f"Error rebalancing weights: {e}")

# Test function
if __name__ == "__main__":
    # Test Portfolio Manager
    symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
    portfolio = AdvancedPortfolioManager(symbols, 10000)
    
    # Simulate opening positions
    portfolio.open_position('BTCUSDT', 'LONG', 45000.0, stop_loss=43000.0, take_profit=50000.0)
    portfolio.open_position('ETHUSDT', 'LONG', 3000.0, stop_loss=2800.0, take_profit=3500.0)
    
    # Simulate price updates
    price_updates = {
        'BTCUSDT': 46000.0,  # +2.22% 
        'ETHUSDT': 2950.0,   # -1.67%
        'ADAUSDT': 0.45      # No position
    }
    
    portfolio.update_positions(price_updates)
    
    # Check risk management
    positions_to_close = portfolio.check_risk_management(price_updates)
    print("Positions to close:", positions_to_close)
    
    # Print summary
    print(portfolio.get_portfolio_summary())