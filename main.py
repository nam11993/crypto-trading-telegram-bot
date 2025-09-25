import logging
import time
import schedule
from datetime import datetime
from typing import Optional
import sys
import os

# Add src directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.api_client import BinanceClient
from src.strategy import TradingStrategy
from src.database import Database
from src.telegram_bot import TelegramNotifier
from config.config import Config

class TradingBot:
    """
    Main Trading Bot class that orchestrates all components
    """
    
    def __init__(self, symbol: str = None):
        # Initialize logging
        self._setup_logging()
        
        # Configuration
        self.symbol = symbol or Config.DEFAULT_SYMBOL
        self.trade_amount = Config.TRADE_AMOUNT
        
        # Components
        self.api_client = None
        self.strategy = None
        self.database = None
        self.telegram_notifier = None
        
        # State
        self.price_history = []
        self.last_signal = 'HOLD'
        self.last_trade_time = None
        self.is_running = False
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"TradingBot initialized for {self.symbol}")
    
    def _setup_logging(self):
        """Setup logging configuration"""
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, Config.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(Config.LOG_FILE),
                logging.StreamHandler()
            ]
        )
    
    def initialize(self):
        """Initialize all bot components"""
        try:
            self.logger.info("Initializing trading bot components...")
            
            # Validate configuration
            Config.validate_config()
            
            # Initialize components
            self.api_client = BinanceClient()
            self.strategy = TradingStrategy(self.symbol)
            self.database = Database()
            self.telegram_notifier = TelegramNotifier(self)
            
            # Test API connection
            if not self.api_client.check_connection():
                raise Exception("Failed to connect to Binance API")
            
            # Load initial price history
            self._load_initial_data()
            
            self.logger.info("Bot initialization completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Bot initialization failed: {e}")
            return False
    
    def _load_initial_data(self):
        """Load initial price data"""
        try:
            # First try to load from database
            db_prices = self.database.get_recent_prices(self.symbol, limit=100)
            
            if len(db_prices) >= 50:
                self.price_history = db_prices[-100:]  # Keep last 100 prices
                self.logger.info(f"Loaded {len(self.price_history)} prices from database")
            else:
                # Load from API if insufficient data in database
                self.logger.info("Insufficient data in database, loading from API...")
                api_prices = self.api_client.get_historical_klines(self.symbol, '1m', 100)
                self.price_history = api_prices
                
                # Save to database
                for price in api_prices:
                    self.database.save_price(self.symbol, price)
                
                self.logger.info(f"Loaded {len(self.price_history)} prices from API")
                
        except Exception as e:
            self.logger.error(f"Error loading initial data: {e}")
            self.price_history = []
    
    def collect_market_data(self):
        """Collect current market data"""
        try:
            current_price = self.api_client.get_current_price(self.symbol)
            self.price_history.append(current_price)
            
            # Keep only last 200 prices in memory
            if len(self.price_history) > 200:
                self.price_history.pop(0)
            
            # Save to database
            self.database.save_price(self.symbol, current_price)
            
            self.logger.debug(f"Current price for {self.symbol}: {current_price}")
            
        except Exception as e:
            self.logger.error(f"Error collecting market data: {e}")
    
    def analyze_market(self):
        """Analyze market and generate trading signals"""
        try:
            if len(self.price_history) < 30:
                self.logger.warning("Insufficient price data for analysis")
                return
            
            current_price = self.price_history[-1]
            
            # Check risk management first
            risk_signal = self.strategy.check_risk_management(current_price)
            if risk_signal:
                signal = risk_signal
                self.logger.info(f"Risk management signal: {signal}")
            else:
                # Get strategy signal
                signal = self.strategy.get_signal(self.price_history)
            
            # Save signal to database
            if signal != 'HOLD':
                self.database.save_signal(self.symbol, signal, current_price, Config.STRATEGY)
                
                # Send Telegram signal notification
                if self.telegram_notifier:
                    self.telegram_notifier.notify_signal(signal, self.symbol, current_price, Config.STRATEGY)
            
            # Execute trades based on signal
            if signal != self.last_signal:
                self._execute_trade(signal, current_price)
                self.last_signal = signal
            
        except Exception as e:
            self.logger.error(f"Error analyzing market: {e}")
    
    def _execute_trade(self, signal: str, price: float):
        """Execute trade based on signal"""
        try:
            if signal == 'BUY' and self.strategy.position != 'LONG':
                self._execute_buy_order(price)
            elif signal == 'SELL' and self.strategy.position == 'LONG':
                self._execute_sell_order(price)
                
        except Exception as e:
            self.logger.error(f"Error executing trade: {e}")
    
    def _execute_buy_order(self, price: float):
        """Execute buy order"""
        try:
            # Check available balance
            balance = self.api_client.get_account_balance('USDT')
            required_balance = self.trade_amount * price
            
            if balance < required_balance:
                self.logger.warning(f"Insufficient balance: {balance} USDT, need {required_balance}")
                return
            
            # Place buy order
            order = self.api_client.place_market_order(self.symbol, 'BUY', self.trade_amount)
            
            if order:
                # Update strategy position
                self.strategy.update_position('BUY', price)
                
                # Save order to database
                self.database.save_order(order)
                
                # Send Telegram notification
                if self.telegram_notifier:
                    self.telegram_notifier.notify_trade('BUY', self.symbol, self.trade_amount, price)
                
                self.last_trade_time = datetime.now()
                self.logger.info(f"BUY order executed: {self.trade_amount} {self.symbol} at {price}")
            
        except Exception as e:
            self.logger.error(f"Error executing buy order: {e}")
    
    def _execute_sell_order(self, price: float):
        """Execute sell order"""
        try:
            # Place sell order
            order = self.api_client.place_market_order(self.symbol, 'SELL', self.trade_amount)
            
            if order:
                # Calculate and save trade performance
                if self.strategy.entry_price > 0:
                    hold_time = int((datetime.now() - self.last_trade_time).total_seconds() / 60) if self.last_trade_time else 0
                    profit_loss_percent = ((price - self.strategy.entry_price) / self.strategy.entry_price) * 100
                    
                    self.database.save_trade_performance(
                        self.symbol, 
                        self.strategy.entry_price, 
                        price, 
                        self.trade_amount,
                        Config.STRATEGY,
                        hold_time
                    )
                    
                    # Send Telegram notification with P&L
                    if self.telegram_notifier:
                        self.telegram_notifier.notify_trade('SELL', self.symbol, self.trade_amount, price, profit_loss_percent)
                else:
                    # Send Telegram notification without P&L
                    if self.telegram_notifier:
                        self.telegram_notifier.notify_trade('SELL', self.symbol, self.trade_amount, price)
                
                # Update strategy position
                self.strategy.update_position('SELL', price)
                
                # Save order to database
                self.database.save_order(order)
                
                self.logger.info(f"SELL order executed: {self.trade_amount} {self.symbol} at {price}")
            
        except Exception as e:
            self.logger.error(f"Error executing sell order: {e}")
    
    def print_status(self):
        """Print current bot status"""
        try:
            current_price = self.price_history[-1] if self.price_history else 0
            stats = self.database.get_trading_statistics()
            
            print("="*50)
            print(f"Trading Bot Status - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*50)
            print(f"Symbol: {self.symbol}")
            print(f"Current Price: ${current_price:.4f}")
            print(f"Position: {self.strategy.position or 'None'}")
            if self.strategy.entry_price > 0:
                pnl = ((current_price - self.strategy.entry_price) / self.strategy.entry_price) * 100
                print(f"Entry Price: ${self.strategy.entry_price:.4f}")
                print(f"Unrealized P&L: {pnl:.2f}%")
            print(f"Last Signal: {self.last_signal}")
            print(f"Strategy: {Config.STRATEGY}")
            print("-"*30)
            print(f"Total Trades: {stats.get('total_trades', 0)}")
            print(f"Win Rate: {stats.get('win_rate', 0):.1f}%")
            print(f"Total P&L: ${stats.get('total_pnl', 0):.4f}")
            print("="*50)
            
        except Exception as e:
            self.logger.error(f"Error printing status: {e}")
    
    def run_backtest(self, days: int = 7):
        """Run backtest on historical data"""
        try:
            self.logger.info(f"Running backtest for {days} days...")
            
            # Get more historical data for backtesting
            historical_prices = self.api_client.get_historical_klines(self.symbol, '1h', days * 24)
            
            if len(historical_prices) < 50:
                self.logger.error("Insufficient historical data for backtesting")
                return
            
            # Reset strategy for backtest
            test_strategy = TradingStrategy(self.symbol)
            trades = []
            
            for i in range(50, len(historical_prices)):
                price_slice = historical_prices[:i+1]
                current_price = price_slice[-1]
                
                signal = test_strategy.get_signal(price_slice)
                
                if signal == 'BUY' and test_strategy.position != 'LONG':
                    test_strategy.update_position('BUY', current_price)
                    trades.append({'type': 'BUY', 'price': current_price, 'time': i})
                    
                elif signal == 'SELL' and test_strategy.position == 'LONG':
                    if trades and trades[-1]['type'] == 'BUY':
                        entry_price = trades[-1]['price']
                        profit = ((current_price - entry_price) / entry_price) * 100
                        trades.append({
                            'type': 'SELL', 
                            'price': current_price, 
                            'profit': profit,
                            'time': i
                        })
                    test_strategy.update_position('SELL', current_price)
            
            # Calculate backtest results
            profitable_trades = [t for t in trades if t.get('profit', 0) > 0]
            total_trades = len([t for t in trades if 'profit' in t])
            
            if total_trades > 0:
                total_profit = sum(t.get('profit', 0) for t in trades)
                win_rate = len(profitable_trades) / total_trades * 100
                
                print("="*40)
                print(f"BACKTEST RESULTS ({days} days)")
                print("="*40)
                print(f"Total Trades: {total_trades}")
                print(f"Profitable Trades: {len(profitable_trades)}")
                print(f"Win Rate: {win_rate:.1f}%")
                print(f"Total Return: {total_profit:.2f}%")
                print(f"Average Return per Trade: {total_profit/total_trades:.2f}%")
                print("="*40)
            
        except Exception as e:
            self.logger.error(f"Error running backtest: {e}")
    
    def start(self):
        """Start the trading bot"""
        if not self.initialize():
            self.logger.error("Bot initialization failed. Cannot start.")
            return
        
        self.is_running = True
        self.logger.info("Starting trading bot...")
        
        # Start Telegram bot
        if self.telegram_notifier:
            self.telegram_notifier.start_bot()
        
        # Schedule tasks
        schedule.every(1).minutes.do(self.collect_market_data)
        schedule.every(5).minutes.do(self.analyze_market)
        schedule.every(1).hours.do(self.print_status)
        schedule.every(1).days.do(lambda: self.database.cleanup_old_data(30))
        
        # Initial status print
        self.print_status()
        
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("Received shutdown signal")
            self.stop()
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            if self.telegram_notifier:
                self.telegram_notifier.notify_error(f"Bot crashed: {str(e)}")
            self.stop()
    
    def stop(self):
        """Stop the trading bot"""
        self.is_running = False
        
        # Stop Telegram bot
        if self.telegram_notifier:
            self.telegram_notifier.stop_bot()
            
        self.logger.info("Trading bot stopped")
        
        # Print final statistics
        self.print_status()
    
    def run_demo_mode(self):
        """Run bot in demo mode (paper trading)"""
        self.logger.info("Running in DEMO mode (paper trading)")
        
        if not self.initialize():
            return
        
        print("Demo mode - simulating trades without real money")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                self.collect_market_data()
                self.analyze_market()
                self.print_status()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            self.stop()

if __name__ == "__main__":
    # Create and run the trading bot
    bot = TradingBot()
    
    # For testing, run in demo mode first
    print("Choose mode:")
    print("1. Demo Mode (Paper Trading)")
    print("2. Live Trading (Real Money)")
    print("3. Backtest")
    
    try:
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == '1':
            bot.run_demo_mode()
        elif choice == '2':
            print("WARNING: This will use real money!")
            confirm = input("Type 'YES' to confirm: ").strip()
            if confirm == 'YES':
                bot.start()
            else:
                print("Live trading cancelled.")
        elif choice == '3':
            days = input("Enter number of days for backtest (default 7): ").strip()
            days = int(days) if days.isdigit() else 7
            bot.run_backtest(days)
        else:
            print("Invalid choice")
            
    except Exception as e:
        logging.error(f"Error: {e}")
        print(f"An error occurred: {e}")