#!/usr/bin/env python3
"""
🕯️ Candlestick Chart Generator - Binance Style
Features:
- Beautiful ASCII candlestick charts
- OHLC data visualization
- Volume bars
- Trend indicators
- Support/Resistance levels
- Binance-like appearance
"""
import logging
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time
import math

class CandlestickChart:
    """Generate beautiful candlestick charts like Binance"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Chart settings
        self.chart_width = 50
        self.chart_height = 12
        self.volume_height = 3
        
        # Candlestick characters
        self.candle_body_green = "█"  # Green/up candle body
        self.candle_body_red = "█"    # Red/down candle body  
        self.candle_wick = "│"        # Wick/shadow
        self.candle_top = "┬"         # Top wick connector
        self.candle_bottom = "┴"      # Bottom wick connector
        
        # Colors (using emoji for Telegram)
        self.green_emoji = "🟢"
        self.red_emoji = "🔴"
        self.neutral_emoji = "⚪"
        
        self.logger.info("Candlestick Chart Generator initialized")
    
    def get_klines_data(self, symbol: str, interval: str = '1h', limit: int = 20) -> List[Dict]:
        """Get OHLCV data from Binance"""
        try:
            symbol = symbol.upper()
            if not symbol.endswith('USDT'):
                symbol += 'USDT'
            
            url = "https://api.binance.com/api/v3/klines"
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                klines = []
                
                for item in data:
                    klines.append({
                        'timestamp': int(item[0]),
                        'open': float(item[1]),
                        'high': float(item[2]),
                        'low': float(item[3]),
                        'close': float(item[4]),
                        'volume': float(item[5]),
                        'close_time': int(item[6])
                    })
                
                return klines[-limit:]  # Keep only requested amount
            
        except Exception as e:
            self.logger.error(f"Error fetching klines for {symbol}: {e}")
            return []
    
    def generate_candlestick_chart(self, symbol: str, interval: str = '1h', 
                                 limit: int = 20) -> str:
        """Generate beautiful candlestick chart"""
        try:
            klines = self.get_klines_data(symbol, interval, limit)
            
            if not klines or len(klines) < 2:
                return f"❌ Không thể tải dữ liệu cho {symbol}"
            
            # Calculate price range
            all_highs = [k['high'] for k in klines]
            all_lows = [k['low'] for k in klines]
            price_high = max(all_highs)
            price_low = min(all_lows)
            price_range = price_high - price_low
            
            if price_range == 0:
                return f"📊 {symbol}: Giá không đổi ${klines[0]['close']:.4f}"
            
            # Current price info
            current_candle = klines[-1]
            prev_candle = klines[-2] if len(klines) > 1 else klines[-1]
            
            current_price = current_candle['close']
            prev_close = prev_candle['close']
            price_change = current_price - prev_close
            change_percent = (price_change / prev_close) * 100 if prev_close > 0 else 0
            trend_emoji = self.green_emoji if price_change >= 0 else self.red_emoji
            
            # Build chart
            chart_lines = []
            
            # Header
            timeframe_name = {
                '1m': '1 Phút', '5m': '5 Phút', '15m': '15 Phút', 
                '1h': '1 Giờ', '4h': '4 Giờ', '1d': '1 Ngày'
            }.get(interval, interval)
            
            header = f"🕯️ {symbol} - {timeframe_name} Chart {trend_emoji}"
            chart_lines.append(header)
            chart_lines.append(f"💰 ${current_price:.4f} ({change_percent:+.2f}%)")
            chart_lines.append("═" * self.chart_width)
            
            # Price chart area
            for row in range(self.chart_height):
                line = ""
                # Calculate price level for this row
                price_level = price_high - (row / (self.chart_height - 1)) * price_range
                
                # Process each candle
                for i, candle in enumerate(klines[-self.chart_width:]):  # Show last N candles
                    if i >= self.chart_width:
                        break
                        
                    open_price = candle['open']
                    high_price = candle['high'] 
                    low_price = candle['low']
                    close_price = candle['close']
                    
                    # Determine candle type
                    is_green = close_price >= open_price
                    body_top = max(open_price, close_price)
                    body_bottom = min(open_price, close_price)
                    
                    # Check what to draw at this price level
                    char = " "
                    
                    # High wick
                    if (price_level <= high_price and price_level > body_top and 
                        abs(price_level - high_price) <= (price_range / self.chart_height)):
                        char = self.candle_wick
                    
                    # Low wick  
                    elif (price_level >= low_price and price_level < body_bottom and
                          abs(price_level - low_price) <= (price_range / self.chart_height)):
                        char = self.candle_wick
                    
                    # Candle body
                    elif body_bottom <= price_level <= body_top:
                        if abs(body_top - body_bottom) <= (price_range / self.chart_height):
                            # Doji or very small body
                            char = "─"
                        else:
                            char = self.candle_body_green if is_green else self.candle_body_red
                    
                    # Current price line (last candle)
                    elif (i == len(klines[-self.chart_width:]) - 1 and 
                          abs(price_level - close_price) <= (price_range / self.chart_height)):
                        char = "●"  # Current price marker
                    
                    line += char
                
                # Add price label
                if row == 0:
                    line += f" ${price_high:.2f} ↑"
                elif row == self.chart_height - 1:
                    line += f" ${price_low:.2f} ↓"
                elif row == self.chart_height // 2:
                    mid_price = (price_high + price_low) / 2
                    line += f" ${mid_price:.2f}"
                
                chart_lines.append(line)
            
            # Volume section
            chart_lines.append("═" * self.chart_width)
            chart_lines.append("📊 VOLUME:")
            
            # Volume bars
            volumes = [k['volume'] for k in klines[-self.chart_width:]]
            max_volume = max(volumes) if volumes else 1
            
            for vol_row in range(self.volume_height):
                vol_line = ""
                vol_threshold = max_volume * (1 - vol_row / self.volume_height)
                
                for i, volume in enumerate(volumes):
                    if volume >= vol_threshold:
                        candle = klines[-self.chart_width:][i]
                        is_green = candle['close'] >= candle['open']
                        vol_line += "█" if is_green else "█"
                    else:
                        vol_line += " "
                
                chart_lines.append(vol_line)
            
            # Statistics footer
            chart_lines.append("═" * self.chart_width)
            
            # Calculate additional stats
            volume_24h = current_candle['volume']
            
            # Support and resistance levels
            recent_highs = [k['high'] for k in klines[-5:]]
            recent_lows = [k['low'] for k in klines[-5:]]
            resistance = max(recent_highs)
            support = min(recent_lows)
            
            chart_lines.append(f"📈 High: ${price_high:.4f} | 📉 Low: ${price_low:.4f}")
            chart_lines.append(f"🔼 Resistance: ${resistance:.4f}")  
            chart_lines.append(f"🔽 Support: ${support:.4f}")
            chart_lines.append(f"📦 Volume: {self._format_volume(volume_24h)}")
            
            # Trend analysis
            if len(klines) >= 5:
                trend = self._analyze_trend(klines[-5:])
                chart_lines.append(f"📊 Trend: {trend}")
            
            chart_lines.append(f"🕒 {datetime.now().strftime('%H:%M:%S')}")
            
            return "\n".join(chart_lines)
            
        except Exception as e:
            self.logger.error(f"Error generating candlestick chart for {symbol}: {e}")
            return f"❌ Lỗi tạo chart cho {symbol}: {e}"
    
    def _analyze_trend(self, klines: List[Dict]) -> str:
        """Analyze trend from recent candles"""
        try:
            if len(klines) < 3:
                return "📊 SIDEWAYS"
            
            # Get closing prices
            closes = [k['close'] for k in klines]
            
            # Simple trend analysis
            up_count = 0
            down_count = 0
            
            for i in range(1, len(closes)):
                if closes[i] > closes[i-1]:
                    up_count += 1
                elif closes[i] < closes[i-1]:
                    down_count += 1
            
            if up_count > down_count + 1:
                return "🟢 UPTREND"
            elif down_count > up_count + 1:
                return "🔴 DOWNTREND"
            else:
                return "⚪ SIDEWAYS"
                
        except Exception as e:
            return "📊 UNKNOWN"
    
    def _format_volume(self, volume: float) -> str:
        """Format volume number"""
        if volume >= 1e9:
            return f"{volume/1e9:.1f}B"
        elif volume >= 1e6:
            return f"{volume/1e6:.1f}M"
        elif volume >= 1e3:
            return f"{volume/1e3:.1f}K"
        else:
            return f"{volume:.1f}"
    
    def get_multiple_timeframes(self, symbol: str) -> str:
        """Get charts for multiple timeframes"""
        try:
            timeframes = ['15m', '1h', '4h']
            result = f"📊 {symbol} MULTI-TIMEFRAME ANALYSIS\n\n"
            
            for tf in timeframes:
                chart = self.generate_candlestick_chart(symbol, tf, 15)
                result += f"{chart}\n" + "─" * 50 + "\n"
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating multi-timeframe chart: {e}")
            return f"❌ Lỗi tạo multi-timeframe chart: {e}"

# Test function
if __name__ == "__main__":
    chart_gen = CandlestickChart()
    
    # Test BTC chart
    print("Testing BTC Candlestick Chart...")
    chart = chart_gen.generate_candlestick_chart('BTCUSDT', '1h', 20)
    print(chart)
    
    print("\n" + "="*60 + "\n")
    
    # Test ETH chart
    print("Testing ETH Candlestick Chart...")
    eth_chart = chart_gen.generate_candlestick_chart('ETHUSDT', '1h', 20)
    print(eth_chart)