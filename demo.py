"""
Demo mode cho Trading Bot - Chạy mà không cần API keys
"""

import sys
import os
import logging
import time
import random
from datetime import datetime, timedelta

# Add src directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.strategy import TradingStrategy
from src.database import Database
from src.telegram_bot import TelegramNotifier
from config.config import Config

class DemoTradingBot:
    """
    Demo Trading Bot - Simulation mode
    """
    
    def __init__(self, symbol='BTCUSDT'):
        self.symbol = symbol
        self.current_price = 45000.0  # Starting BTC price
        self.price_history = []
        self.strategy = TradingStrategy(symbol)
        self.database = Database()
        self.telegram_notifier = TelegramNotifier(self)
        
        # Portfolio
        self.balance_usdt = 1000.0  # Starting balance
        self.balance_crypto = 0.0
        self.total_trades = 0
        self.profitable_trades = 0
        
        # Setup logging
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
        
        print("🤖 Demo Trading Bot initialized!")
        print(f"Symbol: {symbol}")
        print(f"Starting Balance: ${self.balance_usdt:.2f}")
    
    def _setup_logging(self):
        """Setup logging configuration"""
        os.makedirs('logs', exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/demo_bot.log'),
                logging.StreamHandler()
            ]
        )
    
    def simulate_price_movement(self):
        """Simulate realistic price movement"""
        # Random walk with slight upward bias
        change_percent = random.uniform(-2, 2.5)  # -2% to +2.5%
        price_change = self.current_price * (change_percent / 100)
        self.current_price += price_change
        
        # Keep price reasonable
        self.current_price = max(30000, min(80000, self.current_price))
        
        # Add to history
        self.price_history.append(self.current_price)
        
        # Keep last 200 prices
        if len(self.price_history) > 200:
            self.price_history.pop(0)
        
        # Save to database
        self.database.save_price(self.symbol, self.current_price)
        
        return self.current_price
    
    def execute_trade(self, signal, price):
        """Execute simulated trade"""
        trade_amount = 0.01  # Trade 0.01 BTC worth
        
        if signal == 'BUY' and self.strategy.position != 'LONG':
            # Buy crypto with USDT
            cost = trade_amount * price
            if self.balance_usdt >= cost:
                self.balance_usdt -= cost
                self.balance_crypto += trade_amount
                self.strategy.update_position('BUY', price)
                
                print(f"🔵 BUY: {trade_amount} {self.symbol.replace('USDT', '')} at ${price:.2f}")
                self.logger.info(f"BUY order: {trade_amount} at {price}")
                
                # Send Telegram notification
                if self.telegram_notifier:
                    self.telegram_notifier.notify_trade('BUY', self.symbol, trade_amount, price)
                
                # Save signal
                self.database.save_signal(self.symbol, 'BUY', price, Config.STRATEGY)
        
        elif signal == 'SELL' and self.strategy.position == 'LONG':
            # Sell crypto for USDT
            revenue = self.balance_crypto * price
            self.balance_usdt += revenue
            
            # Calculate profit
            if self.strategy.entry_price > 0:
                profit_percent = ((price - self.strategy.entry_price) / self.strategy.entry_price) * 100
                profit_amount = (price - self.strategy.entry_price) * self.balance_crypto
                
                print(f"🔴 SELL: {self.balance_crypto:.6f} {self.symbol.replace('USDT', '')} at ${price:.2f}")
                print(f"💰 Profit: ${profit_amount:.2f} ({profit_percent:.2f}%)")
                
                # Send Telegram notification
                if self.telegram_notifier:
                    self.telegram_notifier.notify_trade('SELL', self.symbol, self.balance_crypto, price, profit_percent)
                
                self.total_trades += 1
                if profit_percent > 0:
                    self.profitable_trades += 1
                
                # Save performance
                self.database.save_trade_performance(
                    self.symbol, self.strategy.entry_price, price, 
                    self.balance_crypto, Config.STRATEGY, 5  # 5 min hold time
                )
            
            self.balance_crypto = 0.0
            self.strategy.update_position('SELL', price)
            
            self.logger.info(f"SELL order: profit = {profit_percent:.2f}%")
            
            # Save signal
            self.database.save_signal(self.symbol, 'SELL', price, Config.STRATEGY)
    
    def print_status(self):
        """Print current status"""
        total_value = self.balance_usdt + (self.balance_crypto * self.current_price)
        profit_loss = total_value - 1000  # Starting balance was 1000
        
        print("\n" + "="*50)
        print(f"📊 Trading Status - {datetime.now().strftime('%H:%M:%S')}")
        print("="*50)
        print(f"Current Price: ${self.current_price:.2f}")
        print(f"Position: {self.strategy.position or 'None'}")
        if self.strategy.entry_price > 0:
            unrealized_pnl = ((self.current_price - self.strategy.entry_price) / self.strategy.entry_price) * 100
            print(f"Entry Price: ${self.strategy.entry_price:.2f}")
            print(f"Unrealized P&L: {unrealized_pnl:.2f}%")
        print("-"*30)
        print(f"USDT Balance: ${self.balance_usdt:.2f}")
        print(f"Crypto Balance: {self.balance_crypto:.6f}")
        print(f"Total Value: ${total_value:.2f}")
        print(f"Total P&L: ${profit_loss:.2f}")
        if self.total_trades > 0:
            win_rate = (self.profitable_trades / self.total_trades) * 100
            print(f"Trades: {self.total_trades} (Win rate: {win_rate:.1f}%)")
        print("="*50)
    
    def run_simulation(self, duration_minutes=60):
        """Run demo simulation"""
        print(f"\n🚀 Starting demo simulation for {duration_minutes} minutes...")
        print("Press Ctrl+C to stop\n")
        
        # Start Telegram bot if configured
        if self.telegram_notifier and Config.TELEGRAM_BOT_TOKEN:
            self.telegram_notifier.start_bot()
            self.telegram_notifier.send_notification_sync("""
🎮 **Demo Mode Started!**

Bot đang chạy demo mode với dữ liệu mô phỏng.

Gửi `/status` để xem trạng thái!
            """)
        
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Generate initial price history
        for i in range(50):
            self.simulate_price_movement()
        
        try:
            iteration = 0
            while datetime.now() < end_time:
                iteration += 1
                
                # Simulate price movement
                price = self.simulate_price_movement()
                
                # Get trading signal if we have enough data
                if len(self.price_history) >= 30:
                    # Check risk management first
                    risk_signal = self.strategy.check_risk_management(price)
                    if risk_signal:
                        signal = risk_signal
                    else:
                        signal = self.strategy.get_signal(self.price_history)
                    
                    # Execute trades
                    if signal != 'HOLD':
                        self.execute_trade(signal, price)
                
                # Print status every 10 iterations
                if iteration % 10 == 0:
                    self.print_status()
                
                # Wait a bit
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n⏹️ Simulation stopped by user")
        
        # Final status
        print("\n🏁 Simulation completed!")
        self.print_status()
        
        # Show statistics
        stats = self.database.get_trading_statistics()
        if stats.get('total_trades', 0) > 0:
            print(f"\n📈 Final Statistics:")
            print(f"Total Trades: {stats['total_trades']}")
            print(f"Win Rate: {stats['win_rate']:.1f}%")
            print(f"Total P&L: ${stats['total_pnl']:.2f}")
    
    def quick_backtest(self):
        """Quick backtest with simulated data"""
        print("🔍 Running quick backtest...")
        
        # Generate simulated historical data
        base_price = 45000
        prices = []
        
        for i in range(500):  # 500 data points
            change = random.uniform(-1.5, 1.5)  # -1.5% to +1.5%
            base_price *= (1 + change/100)
            base_price = max(30000, min(80000, base_price))
            prices.append(base_price)
        
        # Run backtest
        test_strategy = TradingStrategy(self.symbol)
        balance = 1000.0
        crypto_amount = 0.0
        trades = []
        
        for i in range(50, len(prices)):
            price_slice = prices[:i+1]
            current_price = price_slice[-1]
            
            signal = test_strategy.get_signal(price_slice)
            
            if signal == 'BUY' and test_strategy.position != 'LONG':
                # Buy
                trade_amount = 0.01
                cost = trade_amount * current_price
                if balance >= cost:
                    balance -= cost
                    crypto_amount += trade_amount
                    test_strategy.update_position('BUY', current_price)
                    trades.append({'type': 'BUY', 'price': current_price})
            
            elif signal == 'SELL' and test_strategy.position == 'LONG':
                # Sell
                if crypto_amount > 0 and trades and trades[-1]['type'] == 'BUY':
                    revenue = crypto_amount * current_price
                    balance += revenue
                    
                    entry_price = trades[-1]['price']
                    profit_percent = ((current_price - entry_price) / entry_price) * 100
                    
                    trades.append({
                        'type': 'SELL', 
                        'price': current_price, 
                        'profit': profit_percent
                    })
                    
                    crypto_amount = 0.0
                    test_strategy.update_position('SELL', current_price)
        
        # Calculate results
        total_value = balance + (crypto_amount * prices[-1])
        total_return = ((total_value - 1000) / 1000) * 100
        
        sell_trades = [t for t in trades if t.get('profit') is not None]
        profitable_trades = [t for t in sell_trades if t['profit'] > 0]
        
        print("\n📊 Backtest Results:")
        print("="*40)
        print(f"Total Trades: {len(sell_trades)}")
        if len(sell_trades) > 0:
            print(f"Profitable Trades: {len(profitable_trades)}")
            print(f"Win Rate: {len(profitable_trades)/len(sell_trades)*100:.1f}%")
            avg_return = sum(t['profit'] for t in sell_trades) / len(sell_trades)
            print(f"Average Return per Trade: {avg_return:.2f}%")
        print(f"Total Portfolio Return: {total_return:.2f}%")
        print("="*40)

def main():
    """Main demo function"""
    bot = DemoTradingBot('BTCUSDT')
    
    print("🎮 Demo Trading Bot")
    print("="*30)
    print("1. Quick Simulation (5 minutes)")
    print("2. Extended Simulation (30 minutes)")
    print("3. Quick Backtest")
    print("4. View Current Config")
    
    try:
        choice = input("\nChoose option (1-4): ").strip()
        
        if choice == '1':
            bot.run_simulation(5)
        elif choice == '2':
            bot.run_simulation(30)
        elif choice == '3':
            bot.quick_backtest()
        elif choice == '4':
            print(f"\nCurrent Configuration:")
            print(f"Strategy: {Config.STRATEGY}")
            print(f"MA Short: {Config.MA_SHORT_PERIOD}")
            print(f"MA Long: {Config.MA_LONG_PERIOD}")
            print(f"RSI Period: {Config.RSI_PERIOD}")
            print(f"Stop Loss: {Config.STOP_LOSS_PERCENT}%")
            print(f"Take Profit: {Config.TAKE_PROFIT_PERCENT}%")
        else:
            print("Invalid choice")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()