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
"""
import logging
import asyncio
impor        # Parse coin and timeframe (e.g., "BTC 4h" or just "BTC")
        parts = coin_input.split()
        coin = parts[0]
        timeframe = parts[1] if len(parts) > 1 else '1h'
        
        # Validate timeframe
        valid_timeframes = ['1m', '5m', '15m', '1h', '4h', '1d']
        if timeframe not in valid_timeframes:
            timeframe = '1h'
        
        if coin in supported_coins:
            try:
                # Generate professional chart image
                chart_path = chart_generator.generate_professional_chart(coin + 'USDT', timeframe, 200)
                
                if chart_path.startswith('❌'):
                    response = chart_path
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
                        caption += "💡 Sử dụng: BTC 4h, ETH 15m, ADA 1d"
                    else:
                        caption = f"📈 {coin}/USDT Chart ({timeframe})"
                    
                    await send_chart_image(chat_id, chart_path, caption)
                    return
                    
            except Exception as e:
                logger.error(f"Error generating chart for {coin}: {e}")
                response = f"❌ Lỗi tạo chart cho {coin}, thử lại sau"
        
        elif coin_input.startswith('COMPARE'):
            # Handle comparison charts
            try:
                symbols = coin_input.replace('COMPARE', '').strip().split()
                if len(symbols) >= 2:
                    chart_path = chart_generator.generate_comparison_chart(
                        [s + 'USDT' for s in symbols if s in supported_coins], '1h'
                    )
                    
                    if chart_path.startswith('❌'):
                        response = chart_path
                    else:
                        caption = f"📊 Price Comparison: {' vs '.join(symbols)}\n\n"
                        caption += "🔍 Normalized percentage changes\n"
                        caption += "💡 Usage: compare BTC ETH ADA"
                        await send_chart_image(chat_id, chart_path, caption)
                        return
                else:
                    response = "❌ Cần ít nhất 2 coins để so sánh\n💡 VD: compare BTC ETH"
            except Exception as e:
                logger.error(f"Error generating comparison chart: {e}")
                response = "❌ Lỗi tạo comparison chart"
        else:ests
import json
import sys
import os
import threading
from datetime import datetime

# Thêm src vào path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

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

# Global instances
binance_checker = BinanceAccountChecker()
advanced_bot = None  # Will be initialized when needed

# Trading status
status = {
    "running": False,
    "mode": "demo",
    "balance": 1000.0,
    "position": None,
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
            ["💹 Prices", "📈 Chart"],  # Nút mới cho giá và chart
            ["▶️ Start", "⏹️ Stop"],
            ["🟢 BUY", "🔴 SELL"],
            ["⚙️ Settings", "🆘 Help"]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }

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
        await send_message(chat_id, f"❌ Lỗi gửi chart image: {e}")

def handle_message(text, user_name):
    """Xử lý tin nhắn"""
    
    if text == "/start":
        response = f"""🤖 CRYPTO TRADING BOT

Xin chào {user_name}!

🎮 NÚT ĐIỀU KHIỂN:
• 📊 Status - Xem trạng thái bot
• 📈 Stats - Thống kê giao dịch
• 💼 Account - Thông tin Binance
• 💰 Balance - Số dư chi tiết
• 💹 Prices - Giá thị trường real-time
• 📈 Chart - Biểu đồ và phân tích
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
    
    elif text == "� Account":
        # Lấy thông tin tài khoản Binance
        response = binance.format_account_summary()
        return response
    
    elif text == "💰 Balance":
        # Lấy balance chi tiết
        account = binance.get_account_info()
        
        if "error" in account:
            response = f"""❌ KHÔNG THỂ LẤY BALANCE

{account['error']}

💡 Cần setup Binance API keys trong .env"""
        else:
            portfolio = binance.get_portfolio_value()
            
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
                        response += f"� {asset}: {total:.2f}\n"
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
        try:
            # Generate professional chart image
            chart_path = chart_generator.generate_professional_chart('BTCUSDT', '1h', 200)
            
            if chart_path.startswith('❌'):
                response = chart_path
            else:
                # Send image instead of text
                await send_chart_image(chat_id, chart_path, 
                    "📈 BTC/USDT Chart (1H - 200 Candles)\n\n💡 CÁCH SỬ DỤNG:\n" +
                    "• Gửi tên coin: BTC, ETH, ADA...\n" +
                    "• Với timeframe: BTC 4h, ETH 15m\n" +
                    "• So sánh: compare BTC ETH ADA")
                return
        except Exception as e:
            logger.error(f"Error generating chart: {e}")
            response = "❌ Lỗi tạo chart, thử lại sau"
• Gửi tên coin để xem chart (VD: ETH, BTC, ADA)
• Chart tự động cập nhật theo giá real-time
• Hỗ trợ {len(price_tracker.symbols)} cặp coin chính

📊 Coins có sẵn: BTC, ETH, ADA, DOT, LINK, BNB, SOL, MATIC, AVAX, ATOM, XRP, LTC, UNI, SUSHI, AAVE"""
        return response
    
    elif text == "📈 Stats":
        response = f"""📈 TRADING STATISTICS

🎯 PERFORMANCE:
• Total Trades: {status['trades']}
• Win Rate: 65%
• Total P&L: ${status['profit']:.2f}
• Balance: ${status['balance']:.2f}

📊 TODAY:
• Mode: {status['mode'].upper()}
• Status: {'Active' if status['running'] else 'Inactive'}
• Last Update: {datetime.now().strftime('%H:%M:%S')}"""
        return response
    
    elif text == "▶️ Start":
        # Start Advanced Trading Bot asynchronously
        def start_bot():
            try:
                asyncio.run(start_advanced_trading())
                status["running"] = True
                send_message("✅ Advanced Trading Bot started successfully!")
            except Exception as e:
                logger.error(f"Failed to start bot: {e}")
                send_message(f"❌ Failed to start Advanced Trading Bot: {e}")
        
        # Run in thread to avoid blocking
        threading.Thread(target=start_bot, daemon=True).start()
        
        response = f"""▶️ STARTING ADVANCED TRADING BOT!

🚀 Initializing components...
💰 Balance: ${status['balance']:.2f}
🎯 Mode: PROFESSIONAL

⏳ Đang khởi tạo system... Vui lòng đợi!"""
        return response
    
    elif text == "⏹️ Stop":
        # Stop Advanced Trading Bot asynchronously
        def stop_bot():
            try:
                asyncio.run(stop_advanced_trading())
                status["running"] = False
                send_message("✅ Advanced Trading Bot stopped safely!")
            except Exception as e:
                logger.error(f"Failed to stop bot: {e}")
                send_message(f"❌ Failed to stop Advanced Trading Bot: {e}")
        
        # Run in thread to avoid blocking
        threading.Thread(target=stop_bot, daemon=True).start()
        
        response = """⏹️ STOPPING ADVANCED TRADING BOT!

🛑 Closing all positions safely...
📊 Saving trading data...
💾 Shutting down components...

⏳ Vui lòng đợi..."""
        return response
    
    elif text == "🟢 BUY":
        if status["running"]:
            import random
            price = random.uniform(58000, 62000)
            status["position"] = "LONG"
            status["trades"] += 1
            
            response = f"""🟢 BUY ORDER EXECUTED

💰 Symbol: BTCUSDT
📊 Amount: 0.001 BTC
💵 Price: ${price:,.2f}
📈 Position: LONG opened

✅ Giao dịch thành công!"""
        else:
            response = "❌ Hãy START bot trước khi giao dịch!"
        return response
    
    elif text == "🔴 SELL":
        if status["running"]:
            if status["position"]:
                import random
                price = random.uniform(58000, 62000)
                profit = random.uniform(-50, 100)
                status["profit"] += profit
                status["balance"] += profit
                status["position"] = None
                status["trades"] += 1
                
                response = f"""🔴 SELL ORDER EXECUTED

💰 Symbol: BTCUSDT  
📊 Amount: 0.001 BTC
💵 Price: ${price:,.2f}
💰 Profit: ${profit:.2f}

📉 Position closed!"""
            else:
                response = "❌ Không có position để SELL!"
        else:
            response = "❌ Hãy START bot trước!"
        return response
    
    elif text == "⚙️ Settings":
        response = f"""⚙️ BOT SETTINGS

🎯 Current Strategy: Moving Average
🔄 Mode: {status['mode'].upper()}
💰 Balance: ${status['balance']:.2f}

📊 Available Strategies:
• Moving Average (Current)
• RSI Strategy  
• MACD Strategy
• Combined Strategy

💡 Gửi tên strategy để thay đổi."""
        return response
    
    elif text == "🆘 Help":
        response = """🆘 HELP & COMMANDS

🎮 NÚT ĐIỀU KHIỂN:
• 📊 Status - Trạng thái bot advanced
• 📈 Stats - Thống kê giao dịch
• 💼 Account - Thông tin Binance
• 💰 Balance - Số dư chi tiết tất cả coins
• 💹 Prices - Giá thị trường real-time (15 coins)
• 📈 Chart - Biểu đồ ASCII + phân tích
• ▶️ Start - Bật Advanced Trading Bot
• ⏹️ Stop - Tắt trading an toàn
• 🟢 BUY - Mua ngay lập tức
• 🔴 SELL - Bán ngay lập tức
• ⚙️ Settings - Cài đặt bot
• 🆘 Help - Trợ giúp này

� PRICE & CHART FEATURES:
• Gửi tên coin để xem chart chi tiết (VD: BTC, ETH)
• Real-time price tracking cho 15 cặp chính
• ASCII chart với 24h data
• Top gainers/losers
• Market sentiment analysis

�💡 TIPS:
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
        
        if coin_input in supported_coins:
            # Generate chart for requested coin
            chart = price_tracker.generate_ascii_chart(coin_input + 'USDT', '1h', 24)
            price_data = price_tracker.get_price_by_symbol(coin_input + 'USDT')
            
            if price_data:
                response = f"""📈 {coin_input} ANALYSIS

{chart}

� CURRENT PRICE: ${price_data['price']:.4f}
📊 24h Change: {price_data['change_percent']:+.2f}% {price_data['emoji']}
📈 24h High: ${price_data['high_24h']:.4f}
📉 24h Low: ${price_data['low_24h']:.4f}
📦 Volume: {price_tracker._format_volume(price_data['volume'])}

💡 Gửi tên coin khác để xem chart (VD: ETH, BTC, ADA)"""
            else:
                response = f"""❌ Không thể lấy dữ liệu cho {coin_input}

💡 Thử các coin: {', '.join(supported_coins[:10])}"""
                
            return response
        
        else:
            response = f"""�👋 Chào {user_name}!

Bạn gửi: "{text}"

💡 TIPS:
• Gửi tên coin để xem chart (VD: BTC, ETH, ADA)
• Hoặc sử dụng các nút dưới chat để điều khiển bot!

📈 Coins hỗ trợ: {', '.join(supported_coins[:8])}..."""
            return response

async def initialize_advanced_bot():
    """Initialize Advanced Trading Bot"""
    global advanced_bot
    try:
        if advanced_bot is None:
            advanced_bot = AdvancedTradingBot()
            await advanced_bot.initialize()
            logger.info("✅ Advanced Trading Bot initialized")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Advanced Trading Bot: {e}")
        return False

async def start_advanced_trading():
    """Start Advanced Trading Bot"""
    global advanced_bot
    try:
        if advanced_bot is None:
            success = await initialize_advanced_bot()
            if not success:
                return False
        
        await advanced_bot.start()
        advanced_bot.enable_auto_trading()
        return True
    except Exception as e:
        logger.error(f"Failed to start advanced trading: {e}")
        return False

async def stop_advanced_trading():
    """Stop Advanced Trading Bot"""
    global advanced_bot
    try:
        if advanced_bot:
            advanced_bot.disable_auto_trading()
            await advanced_bot.stop()
        return True
    except Exception as e:
        logger.error(f"Failed to stop advanced trading: {e}")
        return False

def get_advanced_status():
    """Get Advanced Trading Bot status"""
    global advanced_bot
    try:
        if advanced_bot:
            return advanced_bot.get_status_summary()
        else:
            return """🚀 ADVANCED TRADING BOT

❌ Bot chưa được khởi tạo
💡 Nhấn '▶️ Start' để bắt đầu

Features sẵn sàng:
• Real-time WebSocket streaming
• Advanced technical analysis  
• Portfolio management
• Enhanced risk management
• Dynamic position sizing
• Multi-symbol trading
• Professional signals"""
    except Exception as e:
        logger.error(f"Error getting advanced status: {e}")
        return "❌ Error getting advanced bot status"

def main():
    """Main function"""
    print("🚀 Starting Simple Reply Keyboard Bot...")
    print("📱 Bot với nút bấm cố định dưới chat!")
    print("⏹️  Nhấn Ctrl+C để dừng")
    print("-" * 50)
    
    # Gửi thông báo khởi động
    startup = """🤖 BOT STARTED!

✅ Simple Trading Bot với nút bấm đã sẵn sàng!

💡 Các nút điều khiển đã hiển thị dưới chat.
Gửi /start để xem hướng dẫn chi tiết!"""
    
    send_message(startup, create_keyboard())
    
    offset = 0
    
    try:
        while True:
            updates = get_updates(offset)
            
            if updates and updates.get("ok"):
                for update in updates.get("result", []):
                    offset = update["update_id"] + 1
                    
                    if "message" in update:
                        message = update["message"]
                        if "text" in message:
                            text = message["text"]
                            user = message.get("from", {})
                            user_name = user.get("first_name", "User")
                            
                            print(f"📨 {user_name}: {text}")
                            
                            # Xử lý tin nhắn
                            response = handle_message(text, user_name)
                            
                            # Gửi phản hồi với keyboard
                            result = send_message(response, create_keyboard())
                            if result and result.get("ok"):
                                print(f"✅ Đã trả lời {user_name}")
                            else:
                                print(f"❌ Lỗi: {result}")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Bot đã dừng!")
        send_message("🤖 Bot tạm dừng!\n\nGửi /start để khởi động lại.")
    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("❌ Cần TELEGRAM_BOT_TOKEN!")
        exit(1)
    main()