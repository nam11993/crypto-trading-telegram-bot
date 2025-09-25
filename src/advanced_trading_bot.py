#!/usr/bin/env python3
"""
🚀 Advanced Trading Bot - Professional Version
Tích hợp tất cả components:
- Real-time WebSocket streaming
- Advanced technical analysis
- Portfolio management
- Enhanced risk management
- Telegram interface
- Binance API integration
"""
import logging
import asyncio
import threading
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json
import os
from dataclasses import dataclass, asdict
import numpy as np

# Import all our components
from websocket_client import BinanceWebSocketClient
from portfolio_manager import AdvancedPortfolioManager
from advanced_analyzer import AdvancedAnalyzer
from risk_manager import EnhancedRiskManager
from binance_account import BinanceAccount

@dataclass
class TradingSignal:
    """Trading signal structure"""
    symbol: str
    signal_type: str  # 'BUY', 'SELL', 'HOLD'
    strength: float  # 0.0 - 1.0
    confidence: float  # 0.0 - 1.0
    price: float
    timestamp: datetime
    analysis: Dict
    risk_metrics: Dict
    
@dataclass
class TradeExecution:
    """Trade execution result"""
    symbol: str
    side: str
    quantity: float
    price: float
    status: str
    order_id: str
    timestamp: datetime
    pnl: float = 0.0

class AdvancedTradingBot:
    """Advanced Trading Bot with all professional features"""
    
    def __init__(self):
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('advanced_trading_bot.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Trading symbols (major pairs)
        self.symbols = [
            'BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'DOTUSDT', 'LINKUSDT',
            'BNBUSDT', 'SOLUSDT', 'MATICUSDT', 'AVAXUSDT', 'ATOMUSDT'
        ]
        
        # Initialize components
        self.binance = BinanceAccount()
        self.websocket_client = None
        self.portfolio_manager = None
        self.analyzer = None
        self.risk_manager = None
        
        # Trading state
        self.is_running = False
        self.auto_trading_enabled = False
        self.current_prices: Dict[str, float] = {}
        self.price_history: Dict[str, List[Dict]] = {symbol: [] for symbol in self.symbols}
        self.active_positions: Dict[str, Dict] = {}
        self.trading_signals: Dict[str, TradingSignal] = {}
        self.trade_history: List[TradeExecution] = []
        
        # Performance tracking
        self.total_trades = 0
        self.winning_trades = 0
        self.total_pnl = 0.0
        self.start_balance = 0.0
        self.current_balance = 0.0
        
        # Threading
        self.websocket_thread = None
        self.analysis_thread = None
        self.main_loop = None
        
        self.logger.info("🚀 Advanced Trading Bot initialized")
    
    async def initialize(self):
        """Initialize tất cả components"""
        try:
            self.logger.info("Initializing trading bot components...")
            
            # Get initial balance
            account_info = self.binance.get_account_info()
            if account_info:
                usdt_balance = float(account_info.get('totalWalletBalance', 0))
                self.start_balance = usdt_balance
                self.current_balance = usdt_balance
                self.logger.info(f"Initial balance: ${usdt_balance:.2f}")
            else:
                self.start_balance = 10000  # Default for testing
                self.current_balance = 10000
                self.logger.warning("Using default balance for testing")
            
            # Initialize WebSocket client
            self.websocket_client = BinanceWebSocketClient(self.symbols)
            
            # Initialize Portfolio Manager
            self.portfolio_manager = AdvancedPortfolioManager(
                symbols=self.symbols, 
                initial_balance=self.start_balance
            )
            
            # Initialize Advanced Analyzer
            self.analyzer = AdvancedAnalyzer(symbols=self.symbols)
            
            # Initialize Risk Manager
            self.risk_manager = EnhancedRiskManager(
                symbols=self.symbols, 
                initial_balance=self.start_balance
            )
            
            self.logger.info("✅ All components initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            return False
    
    async def start_streaming(self):
        """Start WebSocket streaming trong separate thread"""
        try:
            self.logger.info("Starting WebSocket streaming...")
            
            def run_websocket():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self._websocket_handler())
            
            self.websocket_thread = threading.Thread(target=run_websocket)
            self.websocket_thread.daemon = True
            self.websocket_thread.start()
            
            # Wait for first data
            await asyncio.sleep(2)
            self.logger.info("✅ WebSocket streaming started")
            
        except Exception as e:
            self.logger.error(f"Failed to start streaming: {e}")
    
    async def _websocket_handler(self):
        """Handle WebSocket messages"""
        try:
            def on_message(data):
                try:
                    if isinstance(data, dict):
                        symbol = data.get('s', '')
                        price = float(data.get('c', 0))
                        volume = float(data.get('v', 0))
                        
                        if symbol and price > 0:
                            self.current_prices[symbol] = price
                            
                            # Store OHLCV data
                            ohlcv_data = {
                                'timestamp': datetime.now(),
                                'open': float(data.get('o', price)),
                                'high': float(data.get('h', price)),
                                'low': float(data.get('l', price)),
                                'close': price,
                                'volume': volume
                            }
                            
                            self.price_history[symbol].append(ohlcv_data)
                            
                            # Keep only recent data (1000 points)
                            if len(self.price_history[symbol]) > 1000:
                                self.price_history[symbol].pop(0)
                            
                            # Update components with new data
                            self._update_components_with_price(symbol, ohlcv_data)
                            
                except Exception as e:
                    self.logger.error(f"Error processing websocket data: {e}")
            
            # Start WebSocket client
            await self.websocket_client.start(on_message)
            
        except Exception as e:
            self.logger.error(f"WebSocket handler error: {e}")
    
    def _update_components_with_price(self, symbol: str, ohlcv_data: Dict):
        """Update tất cả components với price data mới"""
        try:
            # Update Portfolio Manager
            if self.portfolio_manager:
                self.portfolio_manager.update_price(symbol, ohlcv_data['close'])
            
            # Update Risk Manager
            if self.risk_manager:
                price_data = {symbol: ohlcv_data['close']}
                self.risk_manager.update_price_data(price_data)
            
            # Update Analyzer (in background)
            if self.analyzer and len(self.price_history[symbol]) >= 50:
                # Convert to DataFrame format for analyzer
                recent_data = self.price_history[symbol][-100:]  # Last 100 points
                
                # Run analysis in background thread
                def analyze():
                    try:
                        self.analyzer.update_ohlcv_data(symbol, recent_data)
                    except Exception as e:
                        self.logger.error(f"Error updating analyzer: {e}")
                
                # Don't block main thread
                threading.Thread(target=analyze, daemon=True).start()
                
        except Exception as e:
            self.logger.error(f"Error updating components: {e}")
    
    async def start_analysis_loop(self):
        """Start analysis loop trong separate thread"""
        try:
            def run_analysis():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self._analysis_loop())
            
            self.analysis_thread = threading.Thread(target=run_analysis)
            self.analysis_thread.daemon = True
            self.analysis_thread.start()
            
            self.logger.info("✅ Analysis loop started")
            
        except Exception as e:
            self.logger.error(f"Failed to start analysis loop: {e}")
    
    async def _analysis_loop(self):
        """Main analysis loop"""
        while self.is_running:
            try:
                await self._run_analysis_cycle()
                await asyncio.sleep(30)  # Analyze every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Analysis loop error: {e}")
                await asyncio.sleep(5)
    
    async def _run_analysis_cycle(self):
        """Chạy 1 cycle analysis cho tất cả symbols"""
        try:
            if not all([self.analyzer, self.risk_manager, self.portfolio_manager]):
                return
            
            for symbol in self.symbols:
                if (symbol in self.current_prices and 
                    len(self.price_history.get(symbol, [])) >= 50):
                    
                    # Generate trading signal
                    signal = await self._generate_trading_signal(symbol)
                    if signal:
                        self.trading_signals[symbol] = signal
                        
                        # Execute trade if auto trading enabled
                        if self.auto_trading_enabled and signal.strength > 0.7:
                            await self._execute_signal(signal)
            
            # Update portfolio performance
            await self._update_portfolio_performance()
            
        except Exception as e:
            self.logger.error(f"Analysis cycle error: {e}")
    
    async def _generate_trading_signal(self, symbol: str) -> Optional[TradingSignal]:
        """Generate trading signal cho 1 symbol"""
        try:
            current_price = self.current_prices.get(symbol, 0)
            if not current_price:
                return None
            
            # Get technical analysis
            analysis = self.analyzer.get_comprehensive_analysis(symbol)
            if not analysis or 'technical_score' not in analysis:
                return None
            
            # Get risk metrics
            risk_metrics = {}
            if symbol in self.risk_manager.risk_metrics:
                risk = self.risk_manager.risk_metrics[symbol]
                risk_metrics = {
                    'volatility': risk.volatility,
                    'max_position_size': risk.max_position_size,
                    'recommended_stop_loss': risk.recommended_stop_loss,
                    'recommended_take_profit': risk.recommended_take_profit
                }
            
            # Generate signal
            technical_score = analysis['technical_score']
            momentum_score = analysis.get('momentum_score', 0.5)
            volume_score = analysis.get('volume_analysis', {}).get('volume_trend', 0.5)
            
            # Combined score
            combined_score = (technical_score * 0.5 + momentum_score * 0.3 + volume_score * 0.2)
            
            # Determine signal type
            if combined_score > 0.65:
                signal_type = 'BUY'
                strength = min(combined_score, 1.0)
            elif combined_score < 0.35:
                signal_type = 'SELL'
                strength = min(1.0 - combined_score, 1.0)
            else:
                signal_type = 'HOLD'
                strength = 0.5
            
            # Confidence based on multiple factors
            confidence = min(
                technical_score,
                analysis.get('pattern_confidence', 0.5),
                1.0 - risk_metrics.get('volatility', 0.5)
            ) if signal_type != 'HOLD' else 0.3
            
            return TradingSignal(
                symbol=symbol,
                signal_type=signal_type,
                strength=strength,
                confidence=confidence,
                price=current_price,
                timestamp=datetime.now(),
                analysis=analysis,
                risk_metrics=risk_metrics
            )
            
        except Exception as e:
            self.logger.error(f"Error generating signal for {symbol}: {e}")
            return None
    
    async def _execute_signal(self, signal: TradingSignal):
        """Execute trading signal"""
        try:
            if not self.binance or signal.signal_type == 'HOLD':
                return
            
            symbol = signal.symbol
            current_price = signal.price
            
            # Check if already have position
            if symbol in self.active_positions:
                # Consider closing position if signal is opposite
                existing_side = self.active_positions[symbol].get('side', '')
                if ((existing_side == 'LONG' and signal.signal_type == 'SELL') or
                    (existing_side == 'SHORT' and signal.signal_type == 'BUY')):
                    await self._close_position(symbol)
                return
            
            # Calculate position size using risk management
            quantity = self.risk_manager.calculate_position_size(
                symbol, current_price, signal.strength
            )
            
            if quantity <= 0:
                return
            
            # Determine order side
            side = 'BUY' if signal.signal_type == 'BUY' else 'SELL'
            
            # Calculate stop loss and take profit
            stop_loss = self.risk_manager.get_dynamic_stop_loss(
                symbol, current_price, 'LONG' if side == 'BUY' else 'SHORT'
            )
            take_profit = self.risk_manager.get_dynamic_take_profit(
                symbol, current_price, 'LONG' if side == 'BUY' else 'SHORT'
            )
            
            self.logger.info(f"🎯 Executing {side} signal for {symbol}: {quantity:.6f} @ ${current_price:.4f}")
            
            # For demo purposes, simulate the trade
            # In production, uncomment the real order placement
            """
            result = self.binance.place_market_order(
                symbol=symbol,
                side=side,
                quantity=quantity
            )
            """
            
            # Simulate successful trade
            result = {
                'orderId': f"SIM_{int(time.time())}",
                'status': 'FILLED',
                'executedQty': quantity,
                'cummulativeQuoteQty': quantity * current_price
            }
            
            if result and result.get('status') == 'FILLED':
                # Record position
                self.active_positions[symbol] = {
                    'side': 'LONG' if side == 'BUY' else 'SHORT',
                    'quantity': quantity,
                    'entry_price': current_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'timestamp': datetime.now(),
                    'order_id': result['orderId']
                }
                
                # Record trade
                trade = TradeExecution(
                    symbol=symbol,
                    side=side,
                    quantity=quantity,
                    price=current_price,
                    status='FILLED',
                    order_id=result['orderId'],
                    timestamp=datetime.now()
                )
                self.trade_history.append(trade)
                self.total_trades += 1
                
                self.logger.info(f"✅ {side} order executed for {symbol}")
                
        except Exception as e:
            self.logger.error(f"Error executing signal for {signal.symbol}: {e}")
    
    async def _close_position(self, symbol: str):
        """Close existing position"""
        try:
            if symbol not in self.active_positions:
                return
            
            position = self.active_positions[symbol]
            current_price = self.current_prices.get(symbol, 0)
            
            if not current_price:
                return
            
            # Calculate PnL
            entry_price = position['entry_price']
            quantity = position['quantity']
            side = position['side']
            
            if side == 'LONG':
                pnl = (current_price - entry_price) * quantity
                order_side = 'SELL'
            else:  # SHORT
                pnl = (entry_price - current_price) * quantity
                order_side = 'BUY'
            
            self.logger.info(f"🔄 Closing {side} position for {symbol}: PnL ${pnl:.2f}")
            
            # Simulate closing order
            self.total_pnl += pnl
            if pnl > 0:
                self.winning_trades += 1
            
            # Remove from active positions
            del self.active_positions[symbol]
            
            self.logger.info(f"✅ Position closed for {symbol}")
            
        except Exception as e:
            self.logger.error(f"Error closing position for {symbol}: {e}")
    
    async def _update_portfolio_performance(self):
        """Update portfolio performance metrics"""
        try:
            if self.portfolio_manager:
                # Update current balance estimate
                estimated_balance = self.start_balance + self.total_pnl
                self.current_balance = estimated_balance
                
                # Update portfolio manager
                self.portfolio_manager.current_balance = estimated_balance
                
        except Exception as e:
            self.logger.error(f"Error updating portfolio performance: {e}")
    
    def get_status_summary(self) -> str:
        """Get comprehensive status summary"""
        try:
            # Basic stats
            if self.total_trades > 0:
                win_rate = (self.winning_trades / self.total_trades) * 100
            else:
                win_rate = 0
                
            roi = ((self.current_balance - self.start_balance) / self.start_balance) * 100 if self.start_balance > 0 else 0
            
            summary = f"""
🚀 ADVANCED TRADING BOT STATUS

💰 PERFORMANCE:
• Balance: ${self.current_balance:.2f}
• Total PnL: ${self.total_pnl:.2f}
• ROI: {roi:.2f}%
• Total Trades: {self.total_trades}
• Win Rate: {win_rate:.1f}%

📊 ACTIVE POSITIONS: {len(self.active_positions)}"""
            
            # Active positions
            for symbol, position in self.active_positions.items():
                current_price = self.current_prices.get(symbol, 0)
                entry_price = position['entry_price']
                unrealized_pnl = 0
                
                if current_price > 0:
                    if position['side'] == 'LONG':
                        unrealized_pnl = (current_price - entry_price) * position['quantity']
                    else:
                        unrealized_pnl = (entry_price - current_price) * position['quantity']
                
                summary += f"""
• {symbol}: {position['side']} | PnL: ${unrealized_pnl:.2f}"""
            
            # Trading signals
            recent_signals = [s for s in self.trading_signals.values() if s.signal_type != 'HOLD']
            if recent_signals:
                summary += f"""

🎯 ACTIVE SIGNALS: {len(recent_signals)}"""
                for signal in recent_signals[-3:]:  # Last 3 signals
                    summary += f"""
• {signal.symbol}: {signal.signal_type} | Strength: {signal.strength:.2f}"""
            
            # Risk status
            if self.risk_manager:
                portfolio_risk = self.risk_manager.check_portfolio_risk(self.active_positions)
                should_reduce, risk_msg = self.risk_manager.should_reduce_risk(portfolio_risk)
                
                summary += f"""

🛡️ RISK STATUS: {'⚠️ HIGH' if should_reduce else '✅ OK'}
• Risk Score: {portfolio_risk.risk_score:.1f}/10
• Portfolio VaR: ${portfolio_risk.total_var:.2f}"""
            
            # System status
            summary += f"""

🔧 SYSTEM STATUS:
• WebSocket: {'🟢 Active' if self.websocket_thread and self.websocket_thread.is_alive() else '🔴 Inactive'}
• Analysis: {'🟢 Running' if self.analysis_thread and self.analysis_thread.is_alive() else '🔴 Stopped'}
• Auto Trading: {'🟢 ON' if self.auto_trading_enabled else '🔴 OFF'}
• Symbols Tracked: {len([s for s in self.symbols if s in self.current_prices])}"""
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error creating status summary: {e}")
            return "❌ Error generating status summary"
    
    async def start(self):
        """Start the advanced trading bot"""
        try:
            self.logger.info("🚀 Starting Advanced Trading Bot...")
            self.is_running = True
            
            # Initialize components
            if not await self.initialize():
                return False
            
            # Start WebSocket streaming
            await self.start_streaming()
            
            # Start analysis loop
            await self.start_analysis_loop()
            
            self.logger.info("✅ Advanced Trading Bot started successfully!")
            self.logger.info("📊 Monitoring markets and ready for signals...")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start trading bot: {e}")
            return False
    
    async def stop(self):
        """Stop the trading bot"""
        try:
            self.logger.info("🛑 Stopping Advanced Trading Bot...")
            self.is_running = False
            
            # Close all positions if auto trading was enabled
            if self.auto_trading_enabled:
                for symbol in list(self.active_positions.keys()):
                    await self._close_position(symbol)
            
            # Stop WebSocket client
            if self.websocket_client:
                await self.websocket_client.stop()
            
            # Wait for threads to finish
            if self.websocket_thread and self.websocket_thread.is_alive():
                self.websocket_thread.join(timeout=5)
            
            if self.analysis_thread and self.analysis_thread.is_alive():
                self.analysis_thread.join(timeout=5)
            
            self.logger.info("✅ Trading bot stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping trading bot: {e}")
    
    def enable_auto_trading(self):
        """Enable automatic trading"""
        self.auto_trading_enabled = True
        self.logger.info("✅ Automatic trading ENABLED")
    
    def disable_auto_trading(self):
        """Disable automatic trading"""
        self.auto_trading_enabled = False
        self.logger.info("🛑 Automatic trading DISABLED")

# Test function
if __name__ == "__main__":
    import asyncio
    
    async def test_bot():
        bot = AdvancedTradingBot()
        
        try:
            # Start the bot
            success = await bot.start()
            if not success:
                print("Failed to start bot")
                return
            
            print("Bot started successfully!")
            print("Waiting for market data...")
            
            # Let it run for testing
            await asyncio.sleep(60)  # Run for 1 minute
            
            # Print status
            print(bot.get_status_summary())
            
        except KeyboardInterrupt:
            print("\nStopping bot...")
        finally:
            await bot.stop()
    
    # Run the test
    asyncio.run(test_bot())