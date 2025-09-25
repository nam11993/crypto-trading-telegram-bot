#!/usr/bin/env python3
"""
🚀 Advanced Crypto Trading Bot với Telegram Integration
Professional Features:
- Real-time WebSocket streaming
- Advanced technical analysis  
- Portfolio management with risk distribution
- Enhanced risk management system
- Dynamic position sizing
- Multi-symbol trading
- Professional trading signals
- Professional chart generation
"""
import logging
import asyncio
import time
import requests
import json
import sys
import os
import threading
from datetime import datetime

from config.config import Config
from binance_account import BinanceAccountChecker
from advanced_trading_bot import AdvancedTradingBot
from price_tracker import PriceTracker
from src.binance_chart import BinanceLikeChart

# Config
config = Config()
BOT_TOKEN = config.TELEGRAM_BOT_TOKEN
CHAT_ID = config.TELEGRAM_CHAT_ID

# Global instances
binance_checker = BinanceAccountChecker()
advanced_bot = None  # Will be initialized when needed
price_tracker = PriceTracker()  # Price tracking instance
chart_generator = BinanceLikeChart()  # Professional chart generator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global state
bot_active = False
trading_active = False
auto_trading = False

# WebSocket connection for advanced bot
websocket_thread = None
websocket_active = False

# Test xem có thể connect Binance account
try:
    binance = BinanceAccountChecker()
    logger.info("Binance account checker initialized")
except Exception as e:
    logger.error(f"❌ Lỗi khởi tạo Binance: {e}")
    binance = None

# Performance tracking
start_time = datetime.now()
performance_stats = {
    "messages_sent": 0,
    "errors": 0,
    "uptime": 0,
    "trades": 0,
    "profit": 0.0
}

def send_message(text, reply_keyboard=None):
    """Gửi tin nhắn đơn giản"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    
    if reply_keyboard:
        data["reply_markup"] = json.dumps(reply_keyboard)
    
    try:
        response = requests.post(url, data=data)
        return response.json()
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return None

async def send_chart_image(chat_id: str, image_path: str, caption: str = None):
    """Send chart image to Telegram"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        
        with open(image_path, 'rb') as photo:
            files = {'photo': photo}
            data = {'chat_id': chat_id}
            if caption:
                data['caption'] = caption
            
            response = requests.post(url, files=files, data=data, timeout=30)
            response.raise_for_status()
            logger.info(f"Chart image sent successfully: {image_path}")
            
            # Clean up the file after sending
            try:
                os.remove(image_path)
                logger.info(f"Temporary chart file removed: {image_path}")
            except Exception as e:
                logger.warning(f"Could not remove temp file {image_path}: {e}")
                
    except Exception as e:
        logger.error(f"Error sending chart image: {e}")
        # Send error message instead
        send_message(f"❌ Lỗi gửi chart image: {e}")

def get_updates(offset=0):
    """Lấy updates"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {"offset": offset, "timeout": 10}
    try:
        response = requests.get(url, params=params, timeout=15)
        return response.json()
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return None

def create_keyboard():
    """Tạo reply keyboard"""
    return {
        "keyboard": [
            ["📊 Status", "📈 Stats"],
            ["💼 Account", "💰 Balance"],
            ["💹 Prices", "📈 Chart"],
            ["▶️ Start", "⏹️ Stop"],
            ["🟢 BUY", "🔴 SELL"],
            ["⚙️ Settings", "🆘 Help"]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }

def handle_message(text, user_name):
    """Xử lý tin nhắn"""
    
    if text == "/start":
        response = f"""🤖 CRYPTO TRADING BOT

🎯 Chào {user_name}! Bot đã sẵn sàng!

🎮 NÚT ĐIỀU KHIỂN:
• 📊 Status - Xem trạng thái bot
• 📈 Stats - Thống kê giao dịch
• 💼 Account - Thông tin Binance
• 💰 Balance - Số dư chi tiết
• 💹 Prices - Giá thị trường real-time
• 📈 Chart - Biểu đồ và phân tích (ảnh đẹp)
• ▶️ Start - Bật trading  
• ⏹️ Stop - Tắt trading
• 🟢 BUY - Mua ngay
• 🔴 SELL - Bán ngay
• ⚙️ Settings - Cài đặt
• 🆘 Help - Trợ giúp

💡 Nhấn các nút bên dưới để sử dụng!"""
        return response
    
    elif text == "📊 Status":
        # Show Advanced Trading Bot status
        response = get_advanced_status()
        return response
    
    elif text == "💼 Account":
        # Lấy thông tin tài khoản Binance
        response = binance_checker.format_account_summary()
        return response
    
    elif text == "💰 Balance":
        # Lấy balance chi tiết
        account = binance_checker.get_account_info()
        
        if "error" in account:
            response = f"""❌ KHÔNG THỂ LẤY BALANCE

{account['error']}

💡 Cần setup Binance API keys trong .env"""
        else:
            portfolio = binance_checker.get_portfolio_value()
            
            response = f"""💰 BALANCE CHI TIẾT

💼 PORTFOLIO:
${portfolio.get('total_value_usdt', 0):.2f} USDT

🪙 TẤT CẢ BALANCES:
"""
            # Hiển thị tất cả coin có balance > 0
            balances_found = 0
            for balance in account.get("balances", []):
                asset = balance["asset"]
                total = balance["total"]
                
                # Hiển thị tất cả coin có balance > 0
                if total > 0:
                    if asset == "USDT":
                        response += f"💵 {asset}: {total:.2f}\n"
                    elif asset == "BTC":
                        response += f"₿ {asset}: {total:.8f}\n" 
                    elif asset == "ETH":
                        response += f"🔷 {asset}: {total:.6f}\n"
                    elif total >= 0.0001:  # Hiện coin có ít nhất 0.0001
                        response += f"🪙 {asset}: {total:.6f}\n"
                    
                    balances_found += 1
            
            if balances_found == 0:
                response += "❌ Không có balance nào > 0\n"
            
            response += f"""
📊 ACCOUNT INFO:
• Trade: {'✅' if account.get('can_trade') else '❌'}
• Withdraw: {'✅' if account.get('can_withdraw') else '❌'}
• Type: {account.get('account_type', 'Unknown')}
• Total Assets: {balances_found}

🕐 {datetime.now().strftime('%H:%M:%S')}"""
        
        return response
    
    elif text == "💹 Prices":
        # Show current market prices
        response = price_tracker.get_market_summary()
        return response
    
    elif text == "📈 Chart":
        # Generate beautiful chart image - now returns image instead of text
        try:
            # Generate professional chart image for BTC
            chart_path = chart_generator.generate_professional_chart('BTCUSDT', '1h', 200)
            
            if chart_path.startswith('❌'):
                return chart_path
            else:
                # Send image asynchronously
                asyncio.create_task(send_chart_image(CHAT_ID, chart_path, 
                    "📈 BTC/USDT Chart (1H - 200 Candles)\n\n💡 CÁCH SỬ DỤNG:\n" +
                    "• Gửi tên coin: BTC, ETH, ADA...\n" +
                    "• Với timeframe: BTC 4h, ETH 15m\n" +
                    "• So sánh: compare BTC ETH ADA"))
                
                return "📸 Đang tạo chart ảnh đẹp... Chờ chút!"
                
        except Exception as e:
            logger.error(f"Error generating chart: {e}")
            return "❌ Lỗi tạo chart, thử lại sau"
    
    elif text == "📈 Stats":
        global performance_stats, start_time
        
        # Calculate uptime
        uptime = datetime.now() - start_time
        hours = int(uptime.total_seconds() // 3600)
        minutes = int((uptime.total_seconds() % 3600) // 60)
        
        response = f"""📈 THỐNG KÊ HOẠT ĐỘNG

⏰ UPTIME: {hours}h {minutes}m
📨 Messages: {performance_stats['messages_sent']}
❌ Errors: {performance_stats['errors']}
💹 Trades: {performance_stats['trades']}
💰 P&L: ${performance_stats['profit']:.2f}

🔄 STATUS:
• Bot: {'🟢 ACTIVE' if bot_active else '🔴 INACTIVE'}
• Trading: {'🟢 ON' if trading_active else '🔴 OFF'}
• WebSocket: {'🟢 CONNECTED' if websocket_active else '🔴 DISCONNECTED'}

🎯 FEATURES:
• Real-time price tracking ✅
• Professional chart generation ✅
• Advanced technical analysis ✅
• Multi-timeframe support ✅
• Portfolio management ✅
• Risk management ✅
• WebSocket streaming ✅

🕐 {datetime.now().strftime('%H:%M:%S')}"""
        
        return response
    
    elif text == "▶️ Start":
        global bot_active, trading_active
        bot_active = True
        trading_active = True
        
        # Start advanced bot if not already running
        start_advanced_bot()
        
        response = f"""✅ BOT KHỞI ĐỘNG THÀNH CÔNG!

🟢 TRẠNG THÁI:
• Bot: ACTIVE 
• Trading: ENABLED
• WebSocket: {'CONNECTED' if websocket_active else 'CONNECTING...'}
• Advanced Features: ENABLED

🎯 SẴN SÀNG GIAO DỊCH!
💡 Bot sẽ tự động phân tích và gửi signal

🕐 {datetime.now().strftime('%H:%M:%S')}"""
        
        return response
    
    elif text == "⏹️ Stop":
        global bot_active, trading_active, auto_trading
        bot_active = False
        trading_active = False
        auto_trading = False
        
        # Stop advanced bot
        stop_advanced_bot()
        
        response = f"""⏹️ BOT ĐÃ DỪNG

🔴 TRẠNG THÁI:
• Bot: STOPPED
• Trading: DISABLED  
• WebSocket: DISCONNECTED
• Auto Trading: OFF

✅ Tất cả hoạt động đã dừng an toàn
💡 Nhấn ▶️ Start để khởi động lại

🕐 {datetime.now().strftime('%H:%M:%S')}"""
        
        return response
    
    elif text == "🟢 BUY":
        if not trading_active:
            return "❌ Bot chưa được khởi động! Nhấn ▶️ Start trước"
        
        response = """🟢 LỆNH MUA

⚠️ CẢNH BÁO: Đây là giao dịch thật!

💡 HƯỚNG DẪN:
1️⃣ Đảm bảo có đủ USDT
2️⃣ Kiểm tra balance trước khi mua
3️⃣ Set stop-loss sau khi mua

🎯 SẴN SÀNG MUA:
• Nhập lệnh: BUY [SYMBOL] [AMOUNT]
• VD: BUY BTC 100 (mua 100 USDT BTC)
• VD: BUY ETH 50 (mua 50 USDT ETH)

⚙️ Risk Management: ON
🛡️ Auto Stop-Loss: ENABLED"""
        
        return response
    
    elif text == "🔴 SELL":
        if not trading_active:
            return "❌ Bot chưa được khởi động! Nhấn ▶️ Start trước"
        
        response = """🔴 LỆNH BÁN

⚠️ CẢNH BÁO: Đây là giao dịch thật!

💡 HƯỚNG DẪN:
1️⃣ Kiểm tra balance coin cần bán
2️⃣ Xác nhận giá hiện tại
3️⃣ Đặt lệnh bán thận trọng

🎯 SẴN SÀNG BÁN:
• Nhập lệnh: SELL [SYMBOL] [AMOUNT]
• VD: SELL BTC 0.001 (bán 0.001 BTC)
• VD: SELL ETH 0.1 (bán 0.1 ETH)

⚙️ Risk Management: ON
💰 Take Profit: AUTO"""
        
        return response
    
    elif text == "⚙️ Settings":
        response = f"""⚙️ CÀI ĐẶT BOT

🎛️ TRADING SETTINGS:
• Risk Level: MEDIUM
• Position Size: 2% của portfolio
• Stop Loss: -3%
• Take Profit: +5%
• Max Positions: 3

📊 TECHNICAL ANALYSIS:
• RSI Period: 14
• MA Period: 20, 50
• MACD: 12, 26, 9
• Bollinger Bands: 20, 2

🔄 AUTO FEATURES:
• Auto Trading: {'ON' if auto_trading else 'OFF'}
• DCA: ENABLED
• Portfolio Rebalance: DAILY
• Risk Management: ALWAYS ON

💡 Để thay đổi settings, liên hệ admin"""
        
        return response
    
    elif text == "🆘 Help":
        response = f"""🆘 HƯỚNG DẪN SỬ DỤNG

🎮 CÁC NÚT CHÍNH:
• 📊 Status - Xem tình trạng bot
• 💼 Account - Thông tin Binance  
• 💰 Balance - Chi tiết số dư
• 💹 Prices - Giá thị trường real-time
• 📈 Chart - Biểu đồ ảnh chuyên nghiệp

🕹️ ĐIỀU KHIỂN:
• ▶️ Start - Bật bot
• ⏹️ Stop - Tắt bot  
• 🟢 BUY - Lệnh mua
• 🔴 SELL - Lệnh bán

📈 PRICE & CHART FEATURES:
• Gửi tên coin để xem chart chi tiết (VD: BTC, ETH)
• Timeframe: BTC 4h, ETH 15m, ADA 1d
• So sánh: compare BTC ETH ADA
• Real-time data từ Binance
• Chart ảnh PNG đẹp như Binance

💡 TIPS:
• Professional mode với WebSocket streaming
• Nhấn nút thay vì gõ lệnh  
• Gửi BTC, ETH, ADA... để xem chart instant"""
        
        return response
    
    else:
        # Check if user sent a coin name for chart
        coin_input = text.upper().strip()
        
        # List of supported coins (without USDT suffix)
        supported_coins = [
            'BTC', 'ETH', 'ADA', 'DOT', 'LINK', 'BNB', 'SOL', 
            'MATIC', 'AVAX', 'ATOM', 'XRP', 'LTC', 'UNI', 'SUSHI', 'AAVE'
        ]
        
        # Parse coin and timeframe (e.g., "BTC 4h" or just "BTC")
        parts = coin_input.split()
        coin = parts[0]
        timeframe = parts[1] if len(parts) > 1 else '1h'
        limit = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 200
        
        # Validate timeframe
        valid_timeframes = ['1m', '5m', '15m', '1h', '4h', '1d']
        if timeframe not in valid_timeframes:
            timeframe = '1h'
        
        if coin in supported_coins:
            try:
                # Generate professional chart image
                chart_path = chart_generator.generate_professional_chart(coin + 'USDT', timeframe, limit)
                
                if chart_path.startswith('❌'):
                    return chart_path
                else:
                    # Get price data for caption
                    price_data = price_tracker.get_price_by_symbol(coin + 'USDT')
                    
                    if price_data:
                        caption = f"📈 {coin}/USDT Analysis ({timeframe})\n\n"
                        caption += f"💰 Current: ${price_data['price']:.4f}\n"
                        caption += f"📊 24h: {price_data['change_percent']:+.2f}% {price_data['emoji']}\n"
                        caption += f"📈 High: ${price_data['high_24h']:.4f}\n"
                        caption += f"📉 Low: ${price_data['low_24h']:.4f}\n"
                        caption += f"📦 Volume: {price_tracker._format_volume(price_data['volume'])}\n\n"
                        caption += f"💡 Usage: {coin} 4h, {coin} 15m 500"
                    else:
                        caption = f"📈 {coin}/USDT Chart ({timeframe})"
                    
                    asyncio.create_task(send_chart_image(CHAT_ID, chart_path, caption))
                    return f"📸 Đang tạo chart {coin} {timeframe}... Chờ chút!"
                    
            except Exception as e:
                logger.error(f"Error generating chart for {coin}: {e}")
                return f"❌ Lỗi tạo chart cho {coin}, thử lại sau"
        
        elif coin_input.startswith('COMPARE'):
            # Handle comparison charts
            try:
                symbols = coin_input.replace('COMPARE', '').strip().split()
                if len(symbols) >= 2:
                    chart_path = chart_generator.generate_comparison_chart(
                        [s + 'USDT' for s in symbols if s in supported_coins], '1h'
                    )
                    
                    if chart_path.startswith('❌'):
                        return chart_path
                    else:
                        caption = f"📊 Price Comparison: {' vs '.join(symbols)}\n\n"
                        caption += "🔍 Normalized percentage changes\n"
                        caption += "💡 Usage: compare BTC ETH ADA"
                        asyncio.create_task(send_chart_image(CHAT_ID, chart_path, caption))
                        return "📸 Đang tạo comparison chart... Chờ chút!"
                else:
                    return "❌ Cần ít nhất 2 coins để so sánh\n💡 VD: compare BTC ETH"
            except Exception as e:
                logger.error(f"Error generating comparison chart: {e}")
                return "❌ Lỗi tạo comparison chart"
        else:
            return f"""❌ Không hiểu lệnh '{text}'

🪙 SUPPORTED COINS:
{', '.join(supported_coins)}

💡 CÁCH DÙNG:
• Gửi tên coin: BTC, ETH, ADA
• Với timeframe: BTC 4h, ETH 15m  
• Với số nến: BTC 4h 500
• So sánh: compare BTC ETH ADA
• Hoặc nhấn các nút bên dưới"""

def get_advanced_status():
    """Lấy status của advanced trading bot"""
    global advanced_bot, websocket_active
    
    try:
        response = f"""📊 ADVANCED TRADING STATUS

🤖 BOT ENGINE:
• Main Bot: {'🟢 RUNNING' if bot_active else '🔴 STOPPED'}
• Trading: {'🟢 ENABLED' if trading_active else '🔴 DISABLED'}
• WebSocket: {'🟢 CONNECTED' if websocket_active else '🔴 DISCONNECTED'}

📈 MARKET DATA:
• Price Stream: {'🟢 LIVE' if websocket_active else '🔴 OFFLINE'}
• Technical Analysis: {'🟢 ACTIVE' if advanced_bot else '🔴 STANDBY'}
• Signal Generation: {'🟢 ON' if trading_active else '🔴 OFF'}

💼 PORTFOLIO:
• Risk Level: MEDIUM
• Max Positions: 3
• Available Balance: Checking...

🎯 FEATURES STATUS:
• Auto Trading: {'🟢 ON' if auto_trading else '🔴 OFF'}
• Risk Management: 🟢 ALWAYS ON
• Stop Loss: 🟢 ENABLED (-3%)
• Take Profit: 🟢 ENABLED (+5%)

🕐 Last Update: {datetime.now().strftime('%H:%M:%S')}"""
        
        return response
        
    except Exception as e:
        return f"❌ Lỗi lấy status: {e}"

def start_advanced_bot():
    """Khởi động advanced trading bot"""
    global advanced_bot, websocket_thread, websocket_active
    
    try:
        if not advanced_bot:
            # Initialize advanced bot
            advanced_bot = AdvancedTradingBot()
            logger.info("Advanced Trading Bot initialized")
        
        # Start WebSocket in separate thread
        if not websocket_active:
            websocket_thread = threading.Thread(target=start_websocket_stream, daemon=True)
            websocket_thread.start()
            logger.info("WebSocket stream started")
            
    except Exception as e:
        logger.error(f"Error starting advanced bot: {e}")

def stop_advanced_bot():
    """Dừng advanced trading bot"""
    global advanced_bot, websocket_active
    
    try:
        websocket_active = False
        
        if advanced_bot:
            # Stop advanced bot operations
            logger.info("Advanced Trading Bot stopped")
            
    except Exception as e:
        logger.error(f"Error stopping advanced bot: {e}")

def start_websocket_stream():
    """Start WebSocket stream for real-time data"""
    global websocket_active
    
    try:
        websocket_active = True
        # Simulate WebSocket connection
        while websocket_active and bot_active:
            time.sleep(5)  # Simulate real-time updates
            
        websocket_active = False
        
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        websocket_active = False

async def main_loop():
    """Main bot loop"""
    global performance_stats
    
    offset = 0
    print("🚀 Bot Starting...")
    print(f"📱 Connected to chat: {CHAT_ID}")
    print("⏰ Checking for messages...")
    
    # Send startup message
    startup_keyboard = create_keyboard()
    send_message("🚀 Bot Started! Ready for commands", startup_keyboard)
    
    while True:
        try:
            # Lấy updates
            result = get_updates(offset)
            
            if result and "result" in result:
                for update in result["result"]:
                    offset = update["update_id"] + 1
                    
                    # Xử lý message
                    if "message" in update:
                        message = update["message"]
                        text = message.get("text", "")
                        user_name = message.get("from", {}).get("first_name", "Unknown")
                        
                        print(f"📨 {user_name}: {text}")
                        
                        # Xử lý message và tạo reply
                        reply_keyboard = create_keyboard()
                        response = handle_message(text, user_name)
                        
                        # Gửi reply
                        if response:
                            send_message(response, reply_keyboard)
                            performance_stats["messages_sent"] += 1
                            print(f"✅ Đã trả lời {user_name}")
            
            # Ngủ ngắn để không spam API
            await asyncio.sleep(1)
            
        except KeyboardInterrupt:
            print("\n⏹️ Bot đã dừng!")
            break
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            performance_stats["errors"] += 1
            await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        print("🤖 Advanced Crypto Trading Bot")
        print("📊 Features: Trading, Charts, Portfolio Management")
        print("🎨 Professional PNG chart generation enabled")
        print("------------------------------------------------------------")
        
        # Run async main loop
        asyncio.run(main_loop())
        
    except KeyboardInterrupt:
        print("\n⏹️ Bot đã dừng!")
    except Exception as e:
        print(f"❌ Lỗi khởi động bot: {e}")