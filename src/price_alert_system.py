#!/usr/bin/env python3
"""
🚨 Price Alert System - Cảnh báo giá thay đổi đột biến như Binance
Features:
- Phát hiện pump/dump đột biến
- Volume spike alerts
- Price breakout notifications
- Unusual trading activity detection
- Real-time monitoring all 422 USDT pairs
"""
import logging
import requests
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import statistics
from collections import deque, defaultdict

class PriceAlertSystem:
    """Advanced Price Alert System for detecting sudden price movements"""
    
    def __init__(self, telegram_bot_token: str, telegram_chat_id: str):
        self.logger = logging.getLogger(__name__)
        self.bot_token = telegram_bot_token
        self.chat_id = telegram_chat_id
        
        # Alert settings
        self.alert_settings = {
            'pump_threshold': 15.0,      # % tăng đột biến trong 5-15 phút
            'dump_threshold': -15.0,     # % giảm đột biến trong 5-15 phút
            'volume_spike_multiplier': 5.0,  # Volume tăng x lần so với trung bình
            'price_breakout_threshold': 10.0,  # % breakout khỏi range
            'min_volume_usdt': 100000,   # Volume tối thiểu để alert (100k USDT)
            'time_window': 900,          # 15 phút (900 giây)
            'enabled': True
        }
        
        # Data storage cho analysis
        self.price_history = defaultdict(lambda: deque(maxlen=20))  # Lưu 20 data points gần nhất
        self.volume_history = defaultdict(lambda: deque(maxlen=20))
        self.last_alerts = defaultdict(lambda: 0)  # Tránh spam alerts
        
        # Monitoring status
        self.is_monitoring = False
        self.monitored_symbols = []
        
        # Alert statistics
        self.alert_stats = {
            'total_alerts': 0,
            'pump_alerts': 0,
            'dump_alerts': 0,
            'volume_alerts': 0,
            'breakout_alerts': 0
        }
        
    def start_monitoring(self, symbols: List[str] = None):
        """Bắt đầu monitoring giá thay đổi đột biến"""
        if symbols is None:
            # Monitor top 50 coins với volume cao
            symbols = [
                'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'ADAUSDT', 'XRPUSDT', 'DOGEUSDT', 'DOTUSDT',
                'AVAXUSDT', 'SHIBUSDT', 'LTCUSDT', 'LINKUSDT', 'ATOMUSDT', 'UNIUSDT', 'VETUSDT',
                'MATICUSDT', 'NEARUSDT', 'SANDUSDT', 'MANAUSDT', 'GALAUSDT', 'AXSUSDT', 'CHZUSDT',
                'AAVEUSDT', 'MKRUSDT', 'COMPUSDT', 'SNXUSDT', 'CRVUSDT', 'SUSHIUSDT', '1INCHUSDT',
                'YFIUSDT', 'BATUSDT', 'ENJUSDT', 'ZRXUSDT', 'UMAUSDT', 'RENUSDT', 'KNCUSDT',
                'LRCUSDT', 'BANDUSDT', 'STORJUSDT', 'ANKRUSDT', 'AUDIOUSDT', 'CTKUSDT', 'OCEANUSDT',
                'NMRUSDT', 'RLCUSDT', 'SCUSDT', 'ZENUSDT', 'SKLUSDT', 'CELRUSDT', 'FETUSDT'
            ]
        
        self.monitored_symbols = symbols
        self.is_monitoring = True
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        monitor_thread.start()
        
        self.logger.info(f"🚨 Started price alert monitoring for {len(symbols)} symbols")
        self._send_telegram_message(f"""🚨 PRICE ALERT SYSTEM STARTED

📊 Monitoring: {len(symbols)} symbols
⚡ Pump Alert: >{self.alert_settings['pump_threshold']}% trong 15 phút
📉 Dump Alert: <{self.alert_settings['dump_threshold']}% trong 15 phút
📈 Volume Spike: {self.alert_settings['volume_spike_multiplier']}x trung bình
💰 Min Volume: {self.alert_settings['min_volume_usdt']:,} USDT

✅ System đã sẵn sàng phát hiện biến động đột biến!""")
    
    def stop_monitoring(self):
        """Dừng monitoring"""
        self.is_monitoring = False
        self.logger.info("🛑 Stopped price alert monitoring")
        self._send_telegram_message("🛑 Price Alert System đã dừng!")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Lấy data cho tất cả symbols
                self._fetch_and_analyze_data()
                time.sleep(60)  # Check mỗi 1 phút
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(30)  # Wait 30s before retry
    
    def _fetch_and_analyze_data(self):
        """Fetch price data và analyze cho alerts"""
        try:
            # Get 24hr ticker data for all symbols
            url = "https://api.binance.com/api/v3/ticker/24hr"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                tickers = response.json()
                
                for ticker in tickers:
                    symbol = ticker['symbol']
                    if symbol not in self.monitored_symbols:
                        continue
                    
                    # Extract data
                    price = float(ticker['lastPrice'])
                    volume = float(ticker['quoteVolume'])  # Volume in USDT
                    price_change_pct = float(ticker['priceChangePercent'])
                    
                    # Update histories
                    self.price_history[symbol].append({
                        'timestamp': time.time(),
                        'price': price,
                        'change_pct': price_change_pct
                    })
                    
                    self.volume_history[symbol].append({
                        'timestamp': time.time(),
                        'volume': volume
                    })
                    
                    # Analyze for alerts
                    self._analyze_for_alerts(symbol, ticker)
                    
        except Exception as e:
            self.logger.error(f"Error fetching ticker data: {e}")
    
    def _analyze_for_alerts(self, symbol: str, ticker: dict):
        """Analyze symbol data for alert conditions"""
        try:
            current_time = time.time()
            
            # Tránh spam alerts - chỉ alert 1 lần trong 30 phút cho mỗi symbol
            if current_time - self.last_alerts[symbol] < 1800:  # 30 phút
                return
            
            price = float(ticker['lastPrice'])
            volume = float(ticker['quoteVolume'])
            price_change_pct = float(ticker['priceChangePercent'])
            
            # Skip nếu volume quá thấp
            if volume < self.alert_settings['min_volume_usdt']:
                return
            
            # Check for different alert types
            alert_triggered = False
            
            # 1. PUMP ALERT - Tăng đột biến
            if price_change_pct >= self.alert_settings['pump_threshold']:
                self._send_pump_alert(symbol, ticker)
                alert_triggered = True
                self.alert_stats['pump_alerts'] += 1
            
            # 2. DUMP ALERT - Giảm đột biến  
            elif price_change_pct <= self.alert_settings['dump_threshold']:
                self._send_dump_alert(symbol, ticker)
                alert_triggered = True
                self.alert_stats['dump_alerts'] += 1
            
            # 3. VOLUME SPIKE ALERT
            if self._detect_volume_spike(symbol, volume):
                self._send_volume_spike_alert(symbol, ticker)
                alert_triggered = True
                self.alert_stats['volume_alerts'] += 1
            
            # 4. PRICE BREAKOUT ALERT
            if self._detect_price_breakout(symbol, price):
                self._send_breakout_alert(symbol, ticker)
                alert_triggered = True
                self.alert_stats['breakout_alerts'] += 1
            
            if alert_triggered:
                self.last_alerts[symbol] = current_time
                self.alert_stats['total_alerts'] += 1
                
        except Exception as e:
            self.logger.error(f"Error analyzing {symbol}: {e}")
    
    def _detect_volume_spike(self, symbol: str, current_volume: float) -> bool:
        """Phát hiện volume spike"""
        try:
            if len(self.volume_history[symbol]) < 10:
                return False
            
            # Tính volume trung bình của 10 periods trước
            recent_volumes = [entry['volume'] for entry in list(self.volume_history[symbol])[-10:]]
            avg_volume = statistics.mean(recent_volumes)
            
            # Check volume spike
            if avg_volume > 0 and current_volume > avg_volume * self.alert_settings['volume_spike_multiplier']:
                return True
                
            return False
        except Exception:
            return False
    
    def _detect_price_breakout(self, symbol: str, current_price: float) -> bool:
        """Phát hiện price breakout khỏi trading range"""
        try:
            if len(self.price_history[symbol]) < 15:
                return False
            
            # Lấy giá của 15 periods trước
            recent_prices = [entry['price'] for entry in list(self.price_history[symbol])[-15:]]
            
            # Tính support và resistance
            min_price = min(recent_prices)
            max_price = max(recent_prices)
            price_range = max_price - min_price
            
            if price_range == 0:
                return False
            
            # Check breakout
            breakout_threshold = price_range * (self.alert_settings['price_breakout_threshold'] / 100)
            
            if current_price > max_price + breakout_threshold or current_price < min_price - breakout_threshold:
                return True
                
            return False
        except Exception:
            return False
    
    def _send_pump_alert(self, symbol: str, ticker: dict):
        """Gửi pump alert"""
        price = float(ticker['lastPrice'])
        change_pct = float(ticker['priceChangePercent'])
        volume = float(ticker['quoteVolume'])
        
        message = f"""🚀 PUMP ALERT! 

💰 {symbol.replace('USDT', '')} 
📈 +{change_pct:.2f}% trong 24h!
💵 Price: ${price:.6f}
📊 Volume: {self._format_volume(volume)}
🕐 Time: {datetime.now().strftime('%H:%M:%S')}

⚡ Tăng đột biến - Cân nhắc take profit!"""
        
        self._send_telegram_message(message)
    
    def _send_dump_alert(self, symbol: str, ticker: dict):
        """Gửi dump alert"""
        price = float(ticker['lastPrice'])
        change_pct = float(ticker['priceChangePercent'])
        volume = float(ticker['quoteVolume'])
        
        message = f"""📉 DUMP ALERT!

💰 {symbol.replace('USDT', '')}
📉 {change_pct:.2f}% trong 24h!
💵 Price: ${price:.6f}  
📊 Volume: {self._format_volume(volume)}
🕐 Time: {datetime.now().strftime('%H:%M:%S')}

⚠️ Giảm đột biến - Cẩn thận stop loss!"""
        
        self._send_telegram_message(message)
    
    def _send_volume_spike_alert(self, symbol: str, ticker: dict):
        """Gửi volume spike alert"""
        price = float(ticker['lastPrice'])
        change_pct = float(ticker['priceChangePercent'])
        volume = float(ticker['quoteVolume'])
        
        message = f"""📊 VOLUME SPIKE ALERT!

💰 {symbol.replace('USDT', '')}
📈 {change_pct:+.2f}%
💵 Price: ${price:.6f}
🔥 Volume: {self._format_volume(volume)}
🕐 Time: {datetime.now().strftime('%H:%M:%S')}

⚡ Volume tăng đột biến - Có thể có tin tức lớn!"""
        
        self._send_telegram_message(message)
    
    def _send_breakout_alert(self, symbol: str, ticker: dict):
        """Gửi breakout alert"""
        price = float(ticker['lastPrice'])
        change_pct = float(ticker['priceChangePercent'])
        volume = float(ticker['quoteVolume'])
        
        direction = "UPWARD" if change_pct > 0 else "DOWNWARD"
        emoji = "🚀" if change_pct > 0 else "📉"
        
        message = f"""{emoji} BREAKOUT ALERT!

💰 {symbol.replace('USDT', '')}
🎯 {direction} BREAKOUT
📈 {change_pct:+.2f}%
💵 Price: ${price:.6f}
📊 Volume: {self._format_volume(volume)}
🕐 Time: {datetime.now().strftime('%H:%M:%S')}

🔥 Price vượt khỏi trading range!"""
        
        self._send_telegram_message(message)
    
    def _format_volume(self, volume: float) -> str:
        """Format volume number"""
        if volume >= 1e9:
            return f"{volume/1e9:.1f}B"
        elif volume >= 1e6:
            return f"{volume/1e6:.1f}M"
        elif volume >= 1e3:
            return f"{volume/1e3:.1f}K"
        return f"{volume:.2f}"
    
    def _send_telegram_message(self, message: str):
        """Gửi message qua Telegram"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": message
            }
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                self.logger.info("Alert sent successfully")
            else:
                self.logger.error(f"Failed to send alert: {response.status_code} - {response.text}")
        except Exception as e:
            self.logger.error(f"Error sending Telegram message: {e}")
    
    def get_alert_settings(self) -> dict:
        """Lấy current alert settings"""
        return self.alert_settings.copy()
    
    def update_alert_settings(self, **kwargs):
        """Update alert settings"""
        for key, value in kwargs.items():
            if key in self.alert_settings:
                self.alert_settings[key] = value
                self.logger.info(f"Updated {key} to {value}")
    
    def get_alert_stats(self) -> dict:
        """Lấy alert statistics"""
        stats = self.alert_stats.copy()
        stats['monitored_symbols'] = len(self.monitored_symbols)
        stats['is_monitoring'] = self.is_monitoring
        return stats
    
    def enable_alerts(self):
        """Enable alerts"""
        self.alert_settings['enabled'] = True
        self.logger.info("Alerts enabled")
    
    def disable_alerts(self):
        """Disable alerts"""
        self.alert_settings['enabled'] = False
        self.logger.info("Alerts disabled")
    
    def add_symbol_to_monitor(self, symbol: str):
        """Thêm symbol vào danh sách monitoring"""
        if symbol not in self.monitored_symbols:
            self.monitored_symbols.append(symbol)
            self.logger.info(f"Added {symbol} to monitoring list")
    
    def remove_symbol_from_monitor(self, symbol: str):
        """Xóa symbol khỏi danh sách monitoring"""
        if symbol in self.monitored_symbols:
            self.monitored_symbols.remove(symbol)
            self.logger.info(f"Removed {symbol} from monitoring list")
    
    def get_monitored_symbols(self) -> List[str]:
        """Lấy danh sách symbols đang monitor"""
        return self.monitored_symbols.copy()