import logging
import numpy as np
from typing import List, Tuple, Optional
from config.config import Config

class TradingStrategy:
    """
    Trading strategy engine with multiple strategies
    """
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.position = None  # None, 'LONG', 'SHORT'
        self.entry_price = 0.0
        self.logger = logging.getLogger(__name__)
    
    def moving_average_crossover(self, prices: List[float]) -> str:
        """
        Moving Average Crossover Strategy
        
        Args:
            prices (List[float]): List of historical prices
            
        Returns:
            str: Signal - 'BUY', 'SELL', or 'HOLD'
        """
        if len(prices) < Config.MA_LONG_PERIOD:
            return 'HOLD'
        
        # Calculate moving averages
        short_ma = np.mean(prices[-Config.MA_SHORT_PERIOD:])
        long_ma = np.mean(prices[-Config.MA_LONG_PERIOD:])
        
        # Previous MAs for crossover detection
        prev_short_ma = np.mean(prices[-Config.MA_SHORT_PERIOD-1:-1])
        prev_long_ma = np.mean(prices[-Config.MA_LONG_PERIOD-1:-1])
        
        # Golden Cross (bullish signal)
        if (short_ma > long_ma and prev_short_ma <= prev_long_ma and 
            self.position != 'LONG'):
            self.logger.info(f"MA Golden Cross detected: Short MA {short_ma:.4f} > Long MA {long_ma:.4f}")
            return 'BUY'
        
        # Death Cross (bearish signal)
        elif (short_ma < long_ma and prev_short_ma >= prev_long_ma and 
              self.position == 'LONG'):
            self.logger.info(f"MA Death Cross detected: Short MA {short_ma:.4f} < Long MA {long_ma:.4f}")
            return 'SELL'
        
        return 'HOLD'
    
    def rsi_strategy(self, prices: List[float]) -> str:
        """
        RSI (Relative Strength Index) Strategy
        
        Args:
            prices (List[float]): List of historical prices
            
        Returns:
            str: Signal - 'BUY', 'SELL', or 'HOLD'
        """
        if len(prices) < Config.RSI_PERIOD + 1:
            return 'HOLD'
        
        # Calculate RSI
        rsi = self._calculate_rsi(prices, Config.RSI_PERIOD)
        
        # RSI oversold (bullish signal)
        if rsi < Config.RSI_OVERSOLD and self.position != 'LONG':
            self.logger.info(f"RSI Oversold signal: RSI = {rsi:.2f}")
            return 'BUY'
        
        # RSI overbought (bearish signal)
        elif rsi > Config.RSI_OVERBOUGHT and self.position == 'LONG':
            self.logger.info(f"RSI Overbought signal: RSI = {rsi:.2f}")
            return 'SELL'
        
        return 'HOLD'
    
    def bollinger_bands_strategy(self, prices: List[float], period: int = 20, std_dev: float = 2) -> str:
        """
        Bollinger Bands Strategy
        
        Args:
            prices (List[float]): List of historical prices
            period (int): Period for moving average
            std_dev (float): Standard deviation multiplier
            
        Returns:
            str: Signal - 'BUY', 'SELL', or 'HOLD'
        """
        if len(prices) < period:
            return 'HOLD'
        
        # Calculate Bollinger Bands
        middle_band = np.mean(prices[-period:])
        std = np.std(prices[-period:])
        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)
        
        current_price = prices[-1]
        
        # Price touches lower band (bullish signal)
        if current_price <= lower_band and self.position != 'LONG':
            self.logger.info(f"Bollinger Bands oversold: Price {current_price:.4f} <= Lower Band {lower_band:.4f}")
            return 'BUY'
        
        # Price touches upper band (bearish signal)
        elif current_price >= upper_band and self.position == 'LONG':
            self.logger.info(f"Bollinger Bands overbought: Price {current_price:.4f} >= Upper Band {upper_band:.4f}")
            return 'SELL'
        
        return 'HOLD'
    
    def macd_strategy(self, prices: List[float]) -> str:
        """
        MACD (Moving Average Convergence Divergence) Strategy
        
        Args:
            prices (List[float]): List of historical prices
            
        Returns:
            str: Signal - 'BUY', 'SELL', or 'HOLD'
        """
        if len(prices) < 35:  # Need enough data for MACD calculation
            return 'HOLD'
        
        # Calculate MACD
        macd_line, signal_line = self._calculate_macd(prices)
        
        if len(macd_line) < 2:
            return 'HOLD'
        
        # MACD bullish crossover
        if (macd_line[-1] > signal_line[-1] and 
            macd_line[-2] <= signal_line[-2] and 
            self.position != 'LONG'):
            self.logger.info(f"MACD Bullish crossover: MACD {macd_line[-1]:.6f} > Signal {signal_line[-1]:.6f}")
            return 'BUY'
        
        # MACD bearish crossover
        elif (macd_line[-1] < signal_line[-1] and 
              macd_line[-2] >= signal_line[-2] and 
              self.position == 'LONG'):
            self.logger.info(f"MACD Bearish crossover: MACD {macd_line[-1]:.6f} < Signal {signal_line[-1]:.6f}")
            return 'SELL'
        
        return 'HOLD'
    
    def combined_strategy(self, prices: List[float]) -> str:
        """
        Combined strategy using multiple indicators
        
        Args:
            prices (List[float]): List of historical prices
            
        Returns:
            str: Signal - 'BUY', 'SELL', or 'HOLD'
        """
        signals = []
        
        # Collect signals from different strategies
        ma_signal = self.moving_average_crossover(prices)
        rsi_signal = self.rsi_strategy(prices)
        bb_signal = self.bollinger_bands_strategy(prices)
        
        signals.extend([ma_signal, rsi_signal, bb_signal])
        
        # Count buy/sell signals
        buy_count = signals.count('BUY')
        sell_count = signals.count('SELL')
        
        # Majority vote
        if buy_count >= 2:
            self.logger.info(f"Combined BUY signal: {buy_count}/3 indicators agree")
            return 'BUY'
        elif sell_count >= 2:
            self.logger.info(f"Combined SELL signal: {sell_count}/3 indicators agree")
            return 'SELL'
        
        return 'HOLD'
    
    def get_signal(self, prices: List[float]) -> str:
        """
        Get trading signal based on configured strategy
        
        Args:
            prices (List[float]): List of historical prices
            
        Returns:
            str: Trading signal
        """
        if Config.STRATEGY == 'moving_average':
            return self.moving_average_crossover(prices)
        elif Config.STRATEGY == 'rsi':
            return self.rsi_strategy(prices)
        elif Config.STRATEGY == 'bollinger_bands':
            return self.bollinger_bands_strategy(prices)
        elif Config.STRATEGY == 'macd':
            return self.macd_strategy(prices)
        elif Config.STRATEGY == 'combined':
            return self.combined_strategy(prices)
        else:
            self.logger.warning(f"Unknown strategy: {Config.STRATEGY}")
            return 'HOLD'
    
    def update_position(self, signal: str, price: float):
        """
        Update position based on signal
        
        Args:
            signal (str): Trading signal
            price (float): Current price
        """
        if signal == 'BUY' and self.position != 'LONG':
            self.position = 'LONG'
            self.entry_price = price
            self.logger.info(f"Position updated: LONG at {price}")
        elif signal == 'SELL' and self.position == 'LONG':
            self.position = None
            profit_loss = ((price - self.entry_price) / self.entry_price) * 100
            self.logger.info(f"Position closed: Profit/Loss = {profit_loss:.2f}%")
            self.entry_price = 0.0
    
    def check_risk_management(self, current_price: float) -> Optional[str]:
        """
        Check for stop loss and take profit
        
        Args:
            current_price (float): Current market price
            
        Returns:
            Optional[str]: 'SELL' if risk management triggered, None otherwise
        """
        if self.position != 'LONG' or self.entry_price == 0:
            return None
        
        profit_loss_percent = ((current_price - self.entry_price) / self.entry_price) * 100
        
        # Stop loss
        if profit_loss_percent <= -Config.STOP_LOSS_PERCENT:
            self.logger.warning(f"Stop loss triggered: {profit_loss_percent:.2f}%")
            return 'SELL'
        
        # Take profit
        if profit_loss_percent >= Config.TAKE_PROFIT_PERCENT:
            self.logger.info(f"Take profit triggered: {profit_loss_percent:.2f}%")
            return 'SELL'
        
        return None
    
    def _calculate_rsi(self, prices: List[float], period: int) -> float:
        """Calculate RSI indicator"""
        if len(prices) < period + 1:
            return 50.0  # Neutral RSI
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(-change)
        
        if len(gains) < period:
            return 50.0
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_macd(self, prices: List[float], fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Tuple[List[float], List[float]]:
        """Calculate MACD indicator"""
        if len(prices) < slow_period:
            return [], []
        
        # Calculate EMAs
        fast_ema = self._calculate_ema(prices, fast_period)
        slow_ema = self._calculate_ema(prices, slow_period)
        
        # MACD line
        macd_line = [fast - slow for fast, slow in zip(fast_ema, slow_ema)]
        
        # Signal line
        signal_line = self._calculate_ema(macd_line, signal_period)
        
        return macd_line, signal_line
    
    def _calculate_ema(self, prices: List[float], period: int) -> List[float]:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return []
        
        multiplier = 2 / (period + 1)
        ema = [prices[0]]  # Start with first price
        
        for price in prices[1:]:
            ema.append((price * multiplier) + (ema[-1] * (1 - multiplier)))
        
        return ema