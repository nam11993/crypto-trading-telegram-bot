#!/usr/bin/env python3
"""
🛡️ Enhanced Risk Management System
- Dynamic stop-loss and take-profit
- Position sizing based on volatility
- Portfolio-level risk limits
- Correlation analysis
- Drawdown protection
- VaR (Value at Risk) calculations
"""
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import math

@dataclass
class RiskMetrics:
    """Risk metrics cho một symbol"""
    volatility: float  # Daily volatility
    var_95: float  # 95% Value at Risk
    var_99: float  # 99% Value at Risk
    beta: float  # Beta vs market
    correlation_btc: float  # Correlation với BTC
    max_position_size: float  # Max position size
    recommended_stop_loss: float
    recommended_take_profit: float

@dataclass
class PortfolioRisk:
    """Portfolio-level risk metrics"""
    total_var: float
    portfolio_beta: float
    concentration_risk: float  # 0-1
    correlation_risk: float  # 0-1
    leverage_ratio: float
    margin_utilization: float
    max_drawdown_current: float
    risk_score: float  # Overall 0-10

class EnhancedRiskManager:
    """Advanced Risk Management System"""
    
    def __init__(self, symbols: List[str], initial_balance: float = 10000):
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.symbols = symbols
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        
        # Risk limits
        self.max_portfolio_var = 0.05  # Max 5% daily VaR
        self.max_single_position = 0.20  # Max 20% per position
        self.max_correlation_exposure = 0.50  # Max 50% in correlated assets
        self.max_drawdown_limit = 0.15  # Stop at 15% drawdown
        self.min_sharpe_ratio = 0.5  # Minimum acceptable Sharpe
        
        # Volatility calculation periods
        self.volatility_period = 20  # 20 days
        self.beta_period = 60  # 60 days for beta calculation
        
        # Risk data storage
        self.price_history: Dict[str, List[float]] = {symbol: [] for symbol in symbols}
        self.returns_history: Dict[str, List[float]] = {symbol: [] for symbol in symbols}
        self.risk_metrics: Dict[str, RiskMetrics] = {}
        
        # Portfolio tracking
        self.equity_history: List[Tuple[datetime, float]] = []
        self.drawdown_history: List[float] = []
        
        self.logger.info(f"Enhanced Risk Manager initialized for {len(symbols)} symbols")
    
    def update_price_data(self, price_data: Dict[str, float]):
        """Update price data và calculate risk metrics"""
        try:
            for symbol, price in price_data.items():
                if symbol in self.price_history:
                    self.price_history[symbol].append(price)
                    
                    # Keep only recent data
                    if len(self.price_history[symbol]) > 252:  # 1 year of daily data
                        self.price_history[symbol].pop(0)
                    
                    # Calculate returns
                    if len(self.price_history[symbol]) >= 2:
                        prev_price = self.price_history[symbol][-2]
                        return_pct = (price - prev_price) / prev_price
                        
                        if symbol not in self.returns_history:
                            self.returns_history[symbol] = []
                        
                        self.returns_history[symbol].append(return_pct)
                        
                        # Keep only recent returns
                        if len(self.returns_history[symbol]) > 252:
                            self.returns_history[symbol].pop(0)
            
            # Update risk metrics
            self._update_risk_metrics()
            
        except Exception as e:
            self.logger.error(f"Error updating price data: {e}")
    
    def _update_risk_metrics(self):
        """Update risk metrics cho tất cả symbols"""
        try:
            for symbol in self.symbols:
                if len(self.returns_history.get(symbol, [])) >= self.volatility_period:
                    self.risk_metrics[symbol] = self._calculate_symbol_risk(symbol)
                    
        except Exception as e:
            self.logger.error(f"Error updating risk metrics: {e}")
    
    def _calculate_symbol_risk(self, symbol: str) -> RiskMetrics:
        """Calculate risk metrics cho 1 symbol"""
        try:
            returns = self.returns_history[symbol]
            prices = self.price_history[symbol]
            
            if len(returns) < self.volatility_period:
                return self._default_risk_metrics(symbol)
            
            # Volatility calculation
            recent_returns = returns[-self.volatility_period:]
            volatility = np.std(recent_returns) * math.sqrt(252)  # Annualized
            
            # VaR calculations (95% and 99%)
            var_95 = np.percentile(recent_returns, 5)  # 5th percentile
            var_99 = np.percentile(recent_returns, 1)  # 1st percentile
            
            # Beta calculation (vs BTC if available)
            beta = self._calculate_beta(symbol, 'BTCUSDT')
            
            # Correlation with BTC
            correlation_btc = self._calculate_correlation(symbol, 'BTCUSDT')
            
            # Position sizing based on volatility
            # Higher volatility = smaller max position
            volatility_adj = min(1.0, 0.20 / volatility) if volatility > 0 else 1.0
            max_position_size = self.max_single_position * volatility_adj
            
            # Dynamic stop loss based on volatility
            # Use 2x daily volatility as stop loss
            daily_volatility = volatility / math.sqrt(252)
            recommended_stop_loss = 2 * daily_volatility
            
            # Take profit (risk-reward ratio 1:2)
            recommended_take_profit = recommended_stop_loss * 2
            
            return RiskMetrics(
                volatility=volatility,
                var_95=var_95,
                var_99=var_99,
                beta=beta,
                correlation_btc=correlation_btc,
                max_position_size=max_position_size,
                recommended_stop_loss=recommended_stop_loss,
                recommended_take_profit=recommended_take_profit
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating risk metrics for {symbol}: {e}")
            return self._default_risk_metrics(symbol)
    
    def _calculate_beta(self, symbol: str, market_symbol: str) -> float:
        """Calculate beta vs market (BTC)"""
        try:
            if (symbol == market_symbol or 
                len(self.returns_history.get(symbol, [])) < self.beta_period or
                len(self.returns_history.get(market_symbol, [])) < self.beta_period):
                return 1.0
            
            symbol_returns = self.returns_history[symbol][-self.beta_period:]
            market_returns = self.returns_history[market_symbol][-self.beta_period:]
            
            if len(symbol_returns) != len(market_returns):
                min_len = min(len(symbol_returns), len(market_returns))
                symbol_returns = symbol_returns[-min_len:]
                market_returns = market_returns[-min_len:]
            
            covariance = np.cov(symbol_returns, market_returns)[0][1]
            market_variance = np.var(market_returns)
            
            if market_variance > 0:
                return covariance / market_variance
            else:
                return 1.0
                
        except Exception as e:
            self.logger.error(f"Error calculating beta for {symbol}: {e}")
            return 1.0
    
    def _calculate_correlation(self, symbol1: str, symbol2: str) -> float:
        """Calculate correlation giữa 2 symbols"""
        try:
            if (symbol1 == symbol2 or 
                len(self.returns_history.get(symbol1, [])) < 20 or
                len(self.returns_history.get(symbol2, [])) < 20):
                return 1.0 if symbol1 == symbol2 else 0.0
            
            returns1 = self.returns_history[symbol1][-50:]  # Last 50 days
            returns2 = self.returns_history[symbol2][-50:]
            
            if len(returns1) != len(returns2):
                min_len = min(len(returns1), len(returns2))
                returns1 = returns1[-min_len:]
                returns2 = returns2[-min_len:]
            
            correlation = np.corrcoef(returns1, returns2)[0][1]
            return correlation if not np.isnan(correlation) else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating correlation: {e}")
            return 0.0
    
    def _default_risk_metrics(self, symbol: str) -> RiskMetrics:
        """Default risk metrics khi không đủ dữ liệu"""
        return RiskMetrics(
            volatility=0.50,  # Default 50% annual volatility
            var_95=-0.05,     # Default 5% daily VaR
            var_99=-0.10,     # Default 10% daily VaR
            beta=1.0,
            correlation_btc=0.0,
            max_position_size=0.15,  # Conservative 15%
            recommended_stop_loss=0.05,  # 5% stop loss
            recommended_take_profit=0.10  # 10% take profit
        )
    
    def calculate_position_size(self, symbol: str, current_price: float, 
                              signal_strength: float = 1.0) -> float:
        """Tính position size với risk management"""
        try:
            if symbol not in self.risk_metrics:
                self.logger.warning(f"No risk metrics for {symbol}, using conservative sizing")
                return self.current_balance * 0.05 / current_price
            
            risk_metrics = self.risk_metrics[symbol]
            
            # Base position size từ risk metrics
            max_position_value = self.current_balance * risk_metrics.max_position_size
            
            # Adjust theo signal strength
            adjusted_position_value = max_position_value * signal_strength
            
            # VaR-based adjustment
            # Ensure position VaR không vượt quá portfolio VaR limit
            position_var = abs(risk_metrics.var_95) * adjusted_position_value
            max_allowed_var = self.current_balance * self.max_portfolio_var
            
            if position_var > max_allowed_var:
                adjusted_position_value = max_allowed_var / abs(risk_metrics.var_95)
            
            # Convert to quantity
            quantity = adjusted_position_value / current_price
            
            self.logger.debug(f"Position size for {symbol}: ${adjusted_position_value:.2f} ({quantity:.6f})")
            return quantity
            
        except Exception as e:
            self.logger.error(f"Error calculating position size for {symbol}: {e}")
            return 0.0
    
    def get_dynamic_stop_loss(self, symbol: str, entry_price: float, side: str) -> float:
        """Tính dynamic stop loss"""
        try:
            if symbol not in self.risk_metrics:
                # Default 5% stop loss
                multiplier = 0.95 if side == 'LONG' else 1.05
                return entry_price * multiplier
            
            risk_metrics = self.risk_metrics[symbol]
            stop_loss_pct = risk_metrics.recommended_stop_loss
            
            if side == 'LONG':
                return entry_price * (1 - stop_loss_pct)
            else:  # SHORT
                return entry_price * (1 + stop_loss_pct)
                
        except Exception as e:
            self.logger.error(f"Error calculating stop loss for {symbol}: {e}")
            multiplier = 0.95 if side == 'LONG' else 1.05
            return entry_price * multiplier
    
    def get_dynamic_take_profit(self, symbol: str, entry_price: float, side: str) -> float:
        """Tính dynamic take profit"""
        try:
            if symbol not in self.risk_metrics:
                # Default 10% take profit
                multiplier = 1.10 if side == 'LONG' else 0.90
                return entry_price * multiplier
            
            risk_metrics = self.risk_metrics[symbol]
            take_profit_pct = risk_metrics.recommended_take_profit
            
            if side == 'LONG':
                return entry_price * (1 + take_profit_pct)
            else:  # SHORT
                return entry_price * (1 - take_profit_pct)
                
        except Exception as e:
            self.logger.error(f"Error calculating take profit for {symbol}: {e}")
            multiplier = 1.10 if side == 'LONG' else 0.90
            return entry_price * multiplier
    
    def check_portfolio_risk(self, positions: Dict[str, Dict]) -> PortfolioRisk:
        """Đánh giá portfolio-level risk"""
        try:
            if not positions:
                return self._default_portfolio_risk()
            
            total_exposure = 0
            position_vars = []
            betas = []
            correlations = []
            
            for symbol, position in positions.items():
                position_value = position.get('value', 0)
                total_exposure += position_value
                
                if symbol in self.risk_metrics:
                    risk = self.risk_metrics[symbol]
                    position_var = abs(risk.var_95) * position_value
                    position_vars.append(position_var)
                    betas.append(risk.beta)
                    correlations.append(risk.correlation_btc)
            
            # Portfolio VaR (simplified - assumes some correlation)
            if position_vars:
                # Simple sum (worst case)
                total_var = sum(position_vars)
                
                # Adjust for correlation (rough approximation)
                avg_correlation = np.mean(correlations) if correlations else 0
                correlation_adjustment = 0.5 + 0.5 * avg_correlation
                total_var *= correlation_adjustment
            else:
                total_var = 0
            
            # Portfolio beta
            portfolio_beta = np.mean(betas) if betas else 1.0
            
            # Concentration risk (Herfindahl index)
            if total_exposure > 0:
                weights = [pos.get('value', 0) / total_exposure for pos in positions.values()]
                concentration_risk = sum(w**2 for w in weights)
            else:
                concentration_risk = 0
            
            # Correlation risk
            correlation_risk = np.mean([abs(c) for c in correlations]) if correlations else 0
            
            # Leverage ratio
            leverage_ratio = total_exposure / self.current_balance if self.current_balance > 0 else 0
            
            # Margin utilization
            margin_utilization = total_exposure / self.current_balance if self.current_balance > 0 else 0
            
            # Current drawdown
            if self.equity_history:
                peak_equity = max(eq[1] for eq in self.equity_history)
                current_equity = self.equity_history[-1][1] if self.equity_history else self.current_balance
                max_drawdown_current = (peak_equity - current_equity) / peak_equity if peak_equity > 0 else 0
            else:
                max_drawdown_current = 0
            
            # Overall risk score (0-10)
            risk_factors = [
                min(total_var / (self.current_balance * 0.05), 1) * 2,  # VaR risk
                min(concentration_risk, 1) * 2,  # Concentration risk
                min(correlation_risk, 1) * 2,  # Correlation risk
                min(max_drawdown_current / 0.15, 1) * 2,  # Drawdown risk
                min(leverage_ratio / 2, 1) * 2  # Leverage risk
            ]
            risk_score = sum(risk_factors)
            
            return PortfolioRisk(
                total_var=total_var,
                portfolio_beta=portfolio_beta,
                concentration_risk=concentration_risk,
                correlation_risk=correlation_risk,
                leverage_ratio=leverage_ratio,
                margin_utilization=margin_utilization,
                max_drawdown_current=max_drawdown_current,
                risk_score=risk_score
            )
            
        except Exception as e:
            self.logger.error(f"Error checking portfolio risk: {e}")
            return self._default_portfolio_risk()
    
    def _default_portfolio_risk(self) -> PortfolioRisk:
        """Default portfolio risk khi không có dữ liệu"""
        return PortfolioRisk(
            total_var=0,
            portfolio_beta=1.0,
            concentration_risk=0,
            correlation_risk=0,
            leverage_ratio=0,
            margin_utilization=0,
            max_drawdown_current=0,
            risk_score=0
        )
    
    def should_reduce_risk(self, portfolio_risk: PortfolioRisk) -> Tuple[bool, str]:
        """Kiểm tra có nên giảm risk không"""
        try:
            warnings = []
            
            # Check VaR limit
            var_limit = self.current_balance * self.max_portfolio_var
            if portfolio_risk.total_var > var_limit:
                warnings.append(f"Portfolio VaR ${portfolio_risk.total_var:.2f} exceeds limit ${var_limit:.2f}")
            
            # Check concentration
            if portfolio_risk.concentration_risk > 0.5:
                warnings.append(f"High concentration risk: {portfolio_risk.concentration_risk:.2f}")
            
            # Check correlation
            if portfolio_risk.correlation_risk > 0.8:
                warnings.append(f"High correlation risk: {portfolio_risk.correlation_risk:.2f}")
            
            # Check drawdown
            if portfolio_risk.max_drawdown_current > self.max_drawdown_limit:
                warnings.append(f"Drawdown {portfolio_risk.max_drawdown_current:.2%} exceeds limit {self.max_drawdown_limit:.2%}")
            
            # Check overall risk score
            if portfolio_risk.risk_score > 7:
                warnings.append(f"High risk score: {portfolio_risk.risk_score:.1f}/10")
            
            if warnings:
                return True, "; ".join(warnings)
            else:
                return False, "Risk levels acceptable"
                
        except Exception as e:
            self.logger.error(f"Error checking risk reduction: {e}")
            return False, "Error checking risk"
    
    def get_risk_summary(self, positions: Dict[str, Dict]) -> str:
        """Tạo risk summary report"""
        try:
            portfolio_risk = self.check_portfolio_risk(positions)
            should_reduce, warning = self.should_reduce_risk(portfolio_risk)
            
            summary = f"""
🛡️ RISK MANAGEMENT REPORT

📊 PORTFOLIO RISK:
• Total VaR: ${portfolio_risk.total_var:.2f}
• Risk Score: {portfolio_risk.risk_score:.1f}/10
• Concentration: {portfolio_risk.concentration_risk:.2f}
• Correlation: {portfolio_risk.correlation_risk:.2f}
• Drawdown: {portfolio_risk.max_drawdown_current:.2%}

⚖️ POSITION SIZING:"""
            
            for symbol in self.symbols[:5]:  # Top 5 symbols
                if symbol in self.risk_metrics:
                    risk = self.risk_metrics[symbol]
                    summary += f"""
• {symbol}: Max {risk.max_position_size:.1%}
  Volatility: {risk.volatility:.1%}
  Stop: {risk.recommended_stop_loss:.1%}"""
            
            if should_reduce:
                summary += f"""

⚠️ RISK WARNING:
{warning}

🔧 RECOMMENDATIONS:
• Reduce position sizes
• Close high-risk positions
• Wait for better opportunities"""
            else:
                summary += f"""

✅ RISK STATUS: OK
Portfolio within acceptable risk limits"""
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error creating risk summary: {e}")
            return "❌ Error generating risk summary"

# Test function
if __name__ == "__main__":
    # Test Risk Manager
    symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
    risk_manager = EnhancedRiskManager(symbols, 10000)
    
    # Simulate price data
    import random
    for _ in range(50):
        price_data = {
            'BTCUSDT': 45000 + random.uniform(-1000, 1000),
            'ETHUSDT': 3000 + random.uniform(-200, 200),
            'ADAUSDT': 0.5 + random.uniform(-0.05, 0.05)
        }
        risk_manager.update_price_data(price_data)
    
    # Test position sizing
    position_size = risk_manager.calculate_position_size('BTCUSDT', 45000, 0.8)
    print(f"Recommended position size for BTCUSDT: {position_size:.6f}")
    
    # Test risk summary
    test_positions = {
        'BTCUSDT': {'value': 2000},
        'ETHUSDT': {'value': 1500}
    }
    print(risk_manager.get_risk_summary(test_positions))