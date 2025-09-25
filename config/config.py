import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for trading bot"""
    
    # Binance API Configuration
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
    BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY', '')
    USE_TESTNET = os.getenv('USE_TESTNET', 'true').lower() == 'true'
    
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
    
    # Trading Configuration
    DEFAULT_SYMBOL = os.getenv('DEFAULT_SYMBOL', 'BTCUSDT')
    TRADE_AMOUNT = float(os.getenv('TRADE_AMOUNT', '0.001'))
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/trading.db')
    
    # Strategy Configuration
    STRATEGY = os.getenv('STRATEGY', 'moving_average')
    MA_SHORT_PERIOD = int(os.getenv('MA_SHORT_PERIOD', '10'))
    MA_LONG_PERIOD = int(os.getenv('MA_LONG_PERIOD', '30'))
    RSI_PERIOD = int(os.getenv('RSI_PERIOD', '14'))
    RSI_OVERSOLD = float(os.getenv('RSI_OVERSOLD', '30'))
    RSI_OVERBOUGHT = float(os.getenv('RSI_OVERBOUGHT', '70'))
    
    # Risk Management
    STOP_LOSS_PERCENT = float(os.getenv('STOP_LOSS_PERCENT', '5.0'))
    TAKE_PROFIT_PERCENT = float(os.getenv('TAKE_PROFIT_PERCENT', '10.0'))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/trading_bot.log')
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration"""
        if not cls.BINANCE_API_KEY:
            raise ValueError("BINANCE_API_KEY is required")
        if not cls.BINANCE_SECRET_KEY:
            raise ValueError("BINANCE_SECRET_KEY is required")
        
        print(f"Configuration loaded:")
        print(f"  - Symbol: {cls.DEFAULT_SYMBOL}")
        print(f"  - Trade Amount: {cls.TRADE_AMOUNT}")
        print(f"  - Strategy: {cls.STRATEGY}")
        print(f"  - Testnet: {cls.USE_TESTNET}")
        return True