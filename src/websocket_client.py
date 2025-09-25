#!/usr/bin/env python3
"""
🚀 Advanced WebSocket Client for Real-time Binance Streaming
- Multi-symbol streaming
- Real-time price updates
- OHLCV data
- Volume analysis
- Async processing
"""
import asyncio
import json
import logging
import threading
import time
from datetime import datetime
from typing import Dict, List, Callable, Optional
import websocket
from websocket import WebSocketApp
import pandas as pd
import numpy as np

class BinanceWebSocketClient:
    """Advanced Binance WebSocket client với real-time streaming"""
    
    def __init__(self, symbols: List[str] = None, callback: Callable = None):
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.base_url = "wss://stream.binance.com:9443/ws/"
        self.symbols = symbols or ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'BNBUSDT', 'SOLUSDT']
        self.callback = callback
        
        # Data storage
        self.price_data: Dict[str, Dict] = {}
        self.kline_data: Dict[str, List] = {}
        self.volume_data: Dict[str, List] = {}
        self.trade_data: Dict[str, List] = {}
        
        # WebSocket connections
        self.ws_connections: Dict[str, WebSocketApp] = {}
        self.is_running = False
        self.reconnect_attempts = {}
        
        # Initialize data structures
        self._init_data_structures()
        
        self.logger.info(f"WebSocket client initialized for {len(self.symbols)} symbols")
    
    def _init_data_structures(self):
        """Initialize data structures for all symbols"""
        for symbol in self.symbols:
            self.price_data[symbol] = {
                'price': 0.0,
                'change': 0.0,
                'change_percent': 0.0,
                'high_24h': 0.0,
                'low_24h': 0.0,
                'volume': 0.0,
                'timestamp': 0
            }
            self.kline_data[symbol] = []
            self.volume_data[symbol] = []
            self.trade_data[symbol] = []
            self.reconnect_attempts[symbol] = 0
    
    def create_stream_url(self, symbol: str) -> str:
        """Tạo URL cho combined stream"""
        symbol_lower = symbol.lower()
        
        # Combined stream cho mỗi symbol:
        # - ticker: 24hr price statistics 
        # - kline_1m: 1-minute candlestick data
        # - trade: Individual trade data
        streams = [
            f"{symbol_lower}@ticker",      # 24hr ticker statistics  
            f"{symbol_lower}@kline_1m",    # 1-minute klines
            f"{symbol_lower}@trade"        # Individual trades
        ]
        
        stream_names = "/".join(streams)
        return f"{self.base_url}{stream_names}"
    
    def on_message(self, ws, message):
        """Xử lý tin nhắn WebSocket"""
        try:
            data = json.loads(message)
            
            # Handle ticker data
            if 'e' in data and data['e'] == '24hrTicker':
                self._handle_ticker_data(data)
            
            # Handle kline data
            elif 'e' in data and data['e'] == 'kline':
                self._handle_kline_data(data)
                
            # Handle trade data  
            elif 'e' in data and data['e'] == 'trade':
                self._handle_trade_data(data)
            
            # Call user callback if provided
            if self.callback:
                self.callback(data)
                
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
    
    def _handle_ticker_data(self, data):
        """Xử lý dữ liệu ticker 24hr"""
        try:
            symbol = data['s']
            
            self.price_data[symbol].update({
                'price': float(data['c']),          # Current price
                'change': float(data['P']),         # Price change %
                'change_percent': float(data['P']), # Price change %
                'high_24h': float(data['h']),       # 24hr high
                'low_24h': float(data['l']),        # 24hr low  
                'volume': float(data['v']),         # 24hr volume
                'timestamp': int(data['E'])         # Event time
            })
            
            self.logger.debug(f"📊 {symbol}: ${float(data['c']):.4f} ({float(data['P']):.2f}%)")
            
        except Exception as e:
            self.logger.error(f"Error handling ticker data: {e}")
    
    def _handle_kline_data(self, data):
        """Xử lý dữ liệu kline (OHLCV)"""
        try:
            symbol = data['s']
            kline = data['k']
            
            # Extract OHLCV data
            ohlcv = {
                'timestamp': int(kline['t']),
                'open': float(kline['o']),
                'high': float(kline['h']),
                'low': float(kline['l']),
                'close': float(kline['c']),
                'volume': float(kline['v']),
                'trades': int(kline['n']),
                'is_closed': kline['x']  # Kline is closed
            }
            
            # Only process closed klines for analysis
            if ohlcv['is_closed']:
                self.kline_data[symbol].append(ohlcv)
                
                # Keep only last 200 klines
                if len(self.kline_data[symbol]) > 200:
                    self.kline_data[symbol].pop(0)
                
                self.logger.debug(f"🕯️ {symbol} Kline: O:{ohlcv['open']:.4f} H:{ohlcv['high']:.4f} L:{ohlcv['low']:.4f} C:{ohlcv['close']:.4f} V:{ohlcv['volume']:.2f}")
            
        except Exception as e:
            self.logger.error(f"Error handling kline data: {e}")
    
    def _handle_trade_data(self, data):
        """Xử lý dữ liệu trade individual"""
        try:
            symbol = data['s']
            
            trade_info = {
                'timestamp': int(data['T']),
                'price': float(data['p']),
                'quantity': float(data['q']),
                'is_buyer_maker': data['m']  # True if buyer is maker
            }
            
            self.trade_data[symbol].append(trade_info)
            
            # Keep only last 100 trades
            if len(self.trade_data[symbol]) > 100:
                self.trade_data[symbol].pop(0)
            
        except Exception as e:
            self.logger.error(f"Error handling trade data: {e}")
    
    def on_error(self, ws, error):
        """Xử lý lỗi WebSocket"""
        symbol = self._get_symbol_from_ws(ws)
        self.logger.error(f"WebSocket error for {symbol}: {error}")
        
        # Tăng reconnect attempts
        if symbol:
            self.reconnect_attempts[symbol] = self.reconnect_attempts.get(symbol, 0) + 1
    
    def on_close(self, ws, close_status_code, close_msg):
        """Xử lý đóng kết nối"""
        symbol = self._get_symbol_from_ws(ws)
        self.logger.warning(f"WebSocket closed for {symbol}: {close_status_code} - {close_msg}")
        
        # Auto reconnect nếu vẫn đang chạy
        if self.is_running and symbol:
            self._reconnect_symbol(symbol)
    
    def on_open(self, ws):
        """Xử lý mở kết nối"""
        symbol = self._get_symbol_from_ws(ws)
        self.reconnect_attempts[symbol] = 0
        self.logger.info(f"✅ WebSocket connected for {symbol}")
    
    def _get_symbol_from_ws(self, ws) -> Optional[str]:
        """Lấy symbol từ WebSocket instance"""
        for symbol, connection in self.ws_connections.items():
            if connection == ws:
                return symbol
        return None
    
    def _reconnect_symbol(self, symbol: str):
        """Reconnect cho 1 symbol"""
        if self.reconnect_attempts.get(symbol, 0) < 5:
            delay = min(2 ** self.reconnect_attempts[symbol], 60)  # Exponential backoff
            self.logger.info(f"🔄 Reconnecting {symbol} in {delay}s (attempt {self.reconnect_attempts[symbol] + 1})")
            
            time.sleep(delay)
            self._start_symbol_stream(symbol)
        else:
            self.logger.error(f"❌ Max reconnect attempts reached for {symbol}")
    
    def _start_symbol_stream(self, symbol: str):
        """Bắt đầu stream cho 1 symbol"""
        try:
            if symbol in self.ws_connections:
                self.ws_connections[symbol].close()
            
            url = self.create_stream_url(symbol)
            
            self.ws_connections[symbol] = WebSocketApp(
                url,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
                on_open=self.on_open
            )
            
            # Run in separate thread
            thread = threading.Thread(
                target=self.ws_connections[symbol].run_forever,
                daemon=True
            )
            thread.start()
            
        except Exception as e:
            self.logger.error(f"Error starting stream for {symbol}: {e}")
    
    def start_streaming(self):
        """Bắt đầu streaming cho tất cả symbols"""
        if self.is_running:
            self.logger.warning("WebSocket client is already running")
            return
        
        self.is_running = True
        self.logger.info(f"🚀 Starting WebSocket streams for {len(self.symbols)} symbols...")
        
        # Start streams for all symbols
        for symbol in self.symbols:
            self._start_symbol_stream(symbol)
            time.sleep(0.1)  # Small delay between connections
        
        self.logger.info("✅ All WebSocket streams started")
    
    def stop_streaming(self):
        """Dừng tất cả streams"""
        self.is_running = False
        
        self.logger.info("🛑 Stopping WebSocket streams...")
        
        for symbol, ws in self.ws_connections.items():
            try:
                ws.close()
            except Exception as e:
                self.logger.error(f"Error closing WebSocket for {symbol}: {e}")
        
        self.ws_connections.clear()
        self.logger.info("✅ All WebSocket streams stopped")
    
    def get_current_price(self, symbol: str) -> float:
        """Lấy giá hiện tại của symbol"""
        return self.price_data.get(symbol, {}).get('price', 0.0)
    
    def get_price_change(self, symbol: str) -> float:
        """Lấy % thay đổi giá 24h"""
        return self.price_data.get(symbol, {}).get('change_percent', 0.0)
    
    def get_ohlcv_data(self, symbol: str, limit: int = 100) -> List[Dict]:
        """Lấy dữ liệu OHLCV"""
        return self.kline_data.get(symbol, [])[-limit:]
    
    def get_volume_profile(self, symbol: str) -> Dict:
        """Phân tích volume profile"""
        klines = self.get_ohlcv_data(symbol, 50)
        if not klines:
            return {}
        
        volumes = [k['volume'] for k in klines]
        return {
            'avg_volume': np.mean(volumes),
            'volume_trend': 'UP' if volumes[-1] > np.mean(volumes[-10:]) else 'DOWN',
            'volume_spike': volumes[-1] > np.mean(volumes) * 2
        }
    
    def get_price_summary(self) -> Dict:
        """Lấy tóm tắt giá tất cả symbols"""
        summary = {}
        for symbol in self.symbols:
            data = self.price_data[symbol]
            summary[symbol] = {
                'price': data['price'],
                'change%': data['change_percent'],
                'volume': data['volume'],
                'updated': datetime.fromtimestamp(data['timestamp']/1000) if data['timestamp'] else None
            }
        return summary

# Test function
if __name__ == "__main__":
    import time
    
    def price_callback(data):
        if data.get('e') == '24hrTicker':
            symbol = data['s']
            price = float(data['c'])
            change = float(data['P'])
            print(f"📊 {symbol}: ${price:.4f} ({change:+.2f}%)")
    
    # Test WebSocket client
    symbols = ['BTCUSDT', 'ETHUSDT']
    client = BinanceWebSocketClient(symbols, price_callback)
    
    try:
        client.start_streaming()
        print("🚀 WebSocket streaming started. Press Ctrl+C to stop...")
        
        # Run for 30 seconds
        time.sleep(30)
        
        # Print summary
        print("\n📊 PRICE SUMMARY:")
        summary = client.get_price_summary()
        for symbol, info in summary.items():
            print(f"{symbol}: ${info['price']:.4f} ({info['change%']:+.2f}%)")
            
    except KeyboardInterrupt:
        print("\n⏹️ Stopping...")
    finally:
        client.stop_streaming()
        print("✅ WebSocket client stopped")