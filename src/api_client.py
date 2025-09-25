import logging
from binance.client import Client
from binance.exceptions import BinanceAPIException
from config.config import Config

class BinanceClient:
    """
    Binance API client wrapper with error handling and logging
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        try:
            self.client = Client(
                Config.BINANCE_API_KEY,
                Config.BINANCE_SECRET_KEY,
                testnet=Config.USE_TESTNET
            )
            self.logger.info(f"Binance client initialized (Testnet: {Config.USE_TESTNET})")
        except Exception as e:
            self.logger.error(f"Failed to initialize Binance client: {e}")
            raise
    
    def get_current_price(self, symbol):
        """
        Get current price for a symbol
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
            
        Returns:
            float: Current price
        """
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            price = float(ticker['price'])
            self.logger.debug(f"Current price for {symbol}: {price}")
            return price
        except BinanceAPIException as e:
            self.logger.error(f"Binance API error getting price for {symbol}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error getting price for {symbol}: {e}")
            raise
    
    def get_historical_klines(self, symbol, interval='1m', limit=100):
        """
        Get historical kline/candlestick data
        
        Args:
            symbol (str): Trading pair symbol
            interval (str): Kline interval (1m, 5m, 1h, 1d, etc.)
            limit (int): Number of klines to retrieve
            
        Returns:
            list: List of kline data
        """
        try:
            klines = self.client.get_historical_klines(symbol, interval, limit=limit)
            prices = [float(kline[4]) for kline in klines]  # Close prices
            self.logger.debug(f"Retrieved {len(prices)} historical prices for {symbol}")
            return prices
        except BinanceAPIException as e:
            self.logger.error(f"Binance API error getting historical data: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error getting historical data: {e}")
            raise
    
    def place_market_order(self, symbol, side, quantity):
        """
        Place a market order
        
        Args:
            symbol (str): Trading pair symbol
            side (str): 'BUY' or 'SELL'
            quantity (float): Quantity to trade
            
        Returns:
            dict: Order response
        """
        try:
            order = self.client.create_order(
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=quantity
            )
            self.logger.info(f"Market {side} order placed: {symbol} - {quantity}")
            return order
        except BinanceAPIException as e:
            self.logger.error(f"Binance API error placing order: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error placing order: {e}")
            raise
    
    def get_account_balance(self, asset='USDT'):
        """
        Get account balance for specific asset
        
        Args:
            asset (str): Asset symbol (e.g., 'USDT', 'BTC')
            
        Returns:
            float: Available balance
        """
        try:
            account = self.client.get_account()
            for balance in account['balances']:
                if balance['asset'] == asset:
                    free_balance = float(balance['free'])
                    self.logger.debug(f"Available {asset} balance: {free_balance}")
                    return free_balance
            return 0.0
        except BinanceAPIException as e:
            self.logger.error(f"Binance API error getting balance: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error getting balance: {e}")
            raise
    
    def check_connection(self):
        """
        Check if connection to Binance API is working
        
        Returns:
            bool: True if connection is working
        """
        try:
            self.client.ping()
            server_time = self.client.get_server_time()
            self.logger.info(f"Connected to Binance. Server time: {server_time}")
            return True
        except Exception as e:
            self.logger.error(f"Connection check failed: {e}")
            return False
    
    def get_symbol_info(self, symbol):
        """
        Get trading rules and info for a symbol
        
        Args:
            symbol (str): Trading pair symbol
            
        Returns:
            dict: Symbol information
        """
        try:
            exchange_info = self.client.get_exchange_info()
            for symbol_info in exchange_info['symbols']:
                if symbol_info['symbol'] == symbol:
                    self.logger.debug(f"Symbol info for {symbol}: {symbol_info['status']}")
                    return symbol_info
            return None
        except Exception as e:
            self.logger.error(f"Error getting symbol info: {e}")
            raise