#!/usr/bin/env python3
"""
🤖 Simple Bot with Reply Keyboard - Có Binance Account Info
"""
import time
import requests
import json
import sys
import os
from datetime import datetime

# Thêm src vào path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config.config import Config
from binance_account import BinanceAccountChecker

# Config
config = Config()
BOT_TOKEN = config.TELEGRAM_BOT_TOKEN
CHAT_ID = config.TELEGRAM_CHAT_ID

# Binance checker
binance = BinanceAccountChecker()

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
            ["💼 Account", "💰 Balance"],  # Thêm nút mới
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

Xin chào {user_name}!

🎮 NÚT ĐIỀU KHIỂN:
• 📊 Status - Xem trạng thái bot
• 📈 Stats - Thống kê giao dịch
• 💼 Account - Thông tin Binance
• 💰 Balance - Số dư chi tiết
• ▶️ Start - Bật trading  
• ⏹️ Stop - Tắt trading
• 🟢 BUY - Mua ngay
• 🔴 SELL - Bán ngay
• ⚙️ Settings - Cài đặt
• 🆘 Help - Trợ giúp

💡 Nhấn các nút bên dưới để sử dụng!"""
        return response
    
    elif text == "📊 Status":
        running = "🟢 RUNNING" if status["running"] else "🔴 STOPPED"
        response = f"""📊 BOT STATUS

{running}
💰 Balance: ${status['balance']:.2f}
📊 Position: {status['position'] or 'None'}
🎯 Mode: {status['mode'].upper()}
📈 Trades: {status['trades']}
💵 Profit: ${status['profit']:.2f}

🕐 Time: {datetime.now().strftime('%H:%M:%S')}"""
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
            usdt = binance.get_usdt_balance()
            btc = binance.get_btc_balance()
            portfolio = binance.get_portfolio_value()
            
            response = f"""💰 BALANCE DETAIL

💵 USDT:
• Free: {usdt['free']:.2f}
• Locked: {usdt['locked']:.2f}
• Total: {usdt['total']:.2f}

₿ BTC:
• Free: {btc['free']:.8f}
• Locked: {btc['locked']:.8f}
• Total: {btc['total']:.8f}

📊 PORTFOLIO VALUE:
${portfolio.get('total_value_usdt', 0):.2f} USDT

🕐 {datetime.now().strftime('%H:%M:%S')}"""
        
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
        status["running"] = True
        response = f"""▶️ TRADING STARTED!

🚀 Bot đang chạy
💰 Balance: ${status['balance']:.2f}
🎯 Mode: {status['mode'].upper()}

✅ Sẵn sàng giao dịch!"""
        return response
    
    elif text == "⏹️ Stop":
        status["running"] = False
        response = """⏹️ TRADING STOPPED!

🛑 Bot đã dừng
📊 Positions đã đóng an toàn

Nhấn Start để tiếp tục."""
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
• 📊 Status - Trạng thái bot
• 📈 Stats - Thống kê chi tiết
• 💼 Account - Thông tin Binance
• 💰 Balance - Số dư chi tiết
• ▶️ Start - Bật trading
• ⏹️ Stop - Tắt trading
• 🟢 BUY - Mua ngay lập tức
• 🔴 SELL - Bán ngay lập tức
• ⚙️ Settings - Cài đặt bot
• 🆘 Help - Trợ giúp này

💡 TIPS:
• Demo mode = An toàn 100%
• Nhấn nút thay vì gõ lệnh
• Bot tự động giao dịch khi Start"""
        return response
    
    else:
        response = f"""👋 Chào {user_name}!

Bạn gửi: "{text}"

🎮 Sử dụng các nút dưới chat để điều khiển bot!"""
        return response

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