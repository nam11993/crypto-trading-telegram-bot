import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Optional
import os

class Database:
    """
    Database manager for trading bot data
    """
    
    def __init__(self, db_path: str = "data/trading.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Price data table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS price_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        price REAL NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        interval TEXT DEFAULT '1m'
                    )
                ''')
                
                # Trading signals table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS trading_signals (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        signal TEXT NOT NULL,
                        price REAL NOT NULL,
                        strategy TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Orders table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS orders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        order_id TEXT UNIQUE NOT NULL,
                        symbol TEXT NOT NULL,
                        side TEXT NOT NULL,
                        quantity REAL NOT NULL,
                        price REAL NOT NULL,
                        status TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Portfolio performance table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS portfolio_performance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        entry_price REAL NOT NULL,
                        exit_price REAL NOT NULL,
                        quantity REAL NOT NULL,
                        profit_loss REAL NOT NULL,
                        profit_loss_percent REAL NOT NULL,
                        hold_time INTEGER NOT NULL,
                        strategy TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Bot statistics table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS bot_statistics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        total_trades INTEGER DEFAULT 0,
                        profitable_trades INTEGER DEFAULT 0,
                        total_profit_loss REAL DEFAULT 0.0,
                        win_rate REAL DEFAULT 0.0,
                        max_drawdown REAL DEFAULT 0.0,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                
        except sqlite3.Error as e:
            self.logger.error(f"Database initialization error: {e}")
            raise
    
    def save_price(self, symbol: str, price: float, interval: str = '1m'):
        """
        Save price data to database
        
        Args:
            symbol (str): Trading symbol
            price (float): Price value
            interval (str): Time interval
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO price_data (symbol, price, interval)
                    VALUES (?, ?, ?)
                ''', (symbol, price, interval))
                conn.commit()
                self.logger.debug(f"Saved price: {symbol} = {price}")
                
        except sqlite3.Error as e:
            self.logger.error(f"Error saving price data: {e}")
    
    def save_signal(self, symbol: str, signal: str, price: float, strategy: str):
        """
        Save trading signal to database
        
        Args:
            symbol (str): Trading symbol
            signal (str): Trading signal (BUY/SELL/HOLD)
            price (float): Price at signal
            strategy (str): Strategy name
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO trading_signals (symbol, signal, price, strategy)
                    VALUES (?, ?, ?, ?)
                ''', (symbol, signal, price, strategy))
                conn.commit()
                self.logger.info(f"Saved signal: {signal} for {symbol} at {price}")
                
        except sqlite3.Error as e:
            self.logger.error(f"Error saving signal: {e}")
    
    def save_order(self, order_data: Dict):
        """
        Save order data to database
        
        Args:
            order_data (Dict): Order information from exchange
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO orders 
                    (order_id, symbol, side, quantity, price, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    order_data.get('orderId', ''),
                    order_data.get('symbol', ''),
                    order_data.get('side', ''),
                    float(order_data.get('executedQty', 0)),
                    float(order_data.get('price', 0)),
                    order_data.get('status', '')
                ))
                conn.commit()
                self.logger.info(f"Saved order: {order_data.get('side')} {order_data.get('symbol')}")
                
        except sqlite3.Error as e:
            self.logger.error(f"Error saving order: {e}")
    
    def save_trade_performance(self, symbol: str, entry_price: float, exit_price: float, 
                             quantity: float, strategy: str, hold_time: int):
        """
        Save trade performance data
        
        Args:
            symbol (str): Trading symbol
            entry_price (float): Entry price
            exit_price (float): Exit price
            quantity (float): Trade quantity
            strategy (str): Strategy used
            hold_time (int): Hold time in minutes
        """
        try:
            profit_loss = (exit_price - entry_price) * quantity
            profit_loss_percent = ((exit_price - entry_price) / entry_price) * 100
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO portfolio_performance 
                    (symbol, entry_price, exit_price, quantity, profit_loss, 
                     profit_loss_percent, hold_time, strategy)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (symbol, entry_price, exit_price, quantity, profit_loss,
                      profit_loss_percent, hold_time, strategy))
                conn.commit()
                self.logger.info(f"Saved trade performance: {profit_loss_percent:.2f}% profit")
                
        except sqlite3.Error as e:
            self.logger.error(f"Error saving trade performance: {e}")
    
    def get_recent_prices(self, symbol: str, limit: int = 100) -> List[float]:
        """
        Get recent prices for a symbol
        
        Args:
            symbol (str): Trading symbol
            limit (int): Number of recent prices to retrieve
            
        Returns:
            List[float]: List of recent prices
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT price FROM price_data 
                    WHERE symbol = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (symbol, limit))
                
                results = cursor.fetchall()
                prices = [row[0] for row in reversed(results)]  # Reverse to get chronological order
                return prices
                
        except sqlite3.Error as e:
            self.logger.error(f"Error getting recent prices: {e}")
            return []
    
    def get_trading_statistics(self) -> Dict:
        """
        Get trading statistics
        
        Returns:
            Dict: Trading statistics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total trades
                cursor.execute('SELECT COUNT(*) FROM portfolio_performance')
                total_trades = cursor.fetchone()[0]
                
                # Profitable trades
                cursor.execute('SELECT COUNT(*) FROM portfolio_performance WHERE profit_loss > 0')
                profitable_trades = cursor.fetchone()[0]
                
                # Total profit/loss
                cursor.execute('SELECT SUM(profit_loss) FROM portfolio_performance')
                result = cursor.fetchone()[0]
                total_pnl = result if result else 0.0
                
                # Win rate
                win_rate = (profitable_trades / total_trades * 100) if total_trades > 0 else 0
                
                # Average profit per trade
                avg_profit = total_pnl / total_trades if total_trades > 0 else 0
                
                # Best and worst trades
                cursor.execute('SELECT MAX(profit_loss_percent) FROM portfolio_performance')
                best_trade = cursor.fetchone()[0] or 0
                
                cursor.execute('SELECT MIN(profit_loss_percent) FROM portfolio_performance')
                worst_trade = cursor.fetchone()[0] or 0
                
                stats = {
                    'total_trades': total_trades,
                    'profitable_trades': profitable_trades,
                    'total_pnl': total_pnl,
                    'win_rate': win_rate,
                    'avg_profit_per_trade': avg_profit,
                    'best_trade_percent': best_trade,
                    'worst_trade_percent': worst_trade
                }
                
                return stats
                
        except sqlite3.Error as e:
            self.logger.error(f"Error getting statistics: {e}")
            return {}
    
    def get_recent_signals(self, symbol: str, limit: int = 10) -> List[Dict]:
        """
        Get recent trading signals
        
        Args:
            symbol (str): Trading symbol
            limit (int): Number of signals to retrieve
            
        Returns:
            List[Dict]: Recent signals
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM trading_signals 
                    WHERE symbol = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (symbol, limit))
                
                results = cursor.fetchall()
                return [dict(row) for row in results]
                
        except sqlite3.Error as e:
            self.logger.error(f"Error getting recent signals: {e}")
            return []
    
    def cleanup_old_data(self, days: int = 30):
        """
        Clean up old data to keep database size manageable
        
        Args:
            days (int): Number of days of data to keep
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Clean old price data (keep only recent data)
                cursor.execute('''
                    DELETE FROM price_data 
                    WHERE timestamp < datetime('now', '-{} days')
                '''.format(days))
                
                # Clean old signals (keep all signals as they're important for analysis)
                # cursor.execute('''
                #     DELETE FROM trading_signals 
                #     WHERE timestamp < datetime('now', '-{} days')
                # '''.format(days))
                
                conn.commit()
                self.logger.info(f"Cleaned up data older than {days} days")
                
        except sqlite3.Error as e:
            self.logger.error(f"Error cleaning up old data: {e}")
    
    def close(self):
        """Close database connection"""
        # SQLite connections are automatically closed when using context manager
        self.logger.info("Database connections closed")