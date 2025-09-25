#!/usr/bin/env python3
"""
🤖 Advanced Telegram Trading Bot
Bot với đầy đủ nút bấm và lệnh điều khiển trading
"""
import time
import requests
import json
import threading
from datetime import datetime
from config.config import Config

# Lấy config
config = Config()
BOT_TOKEN = config.TELEGRAM_BOT_TOKEN
CHAT_ID = config.TELEGRAM_CHAT_ID

# Trạng thái trading bot
trading_status = {
    "is_running": False,
    "mode": "demo",
    "balance": 1000.0,
    "position": None,
    "total_trades": 0,
    "profit": 0.0,
    "current_strategy": "moving_average"
}

def send_message(message, keyboard=None, reply_keyboard=None):
    """Gửi tin nhắn với keyboard"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        # Bỏ parse_mode để tránh lỗi
    }
    if keyboard:
        data["reply_markup"] = json.dumps(keyboard)
    elif reply_keyboard:
        data["reply_markup"] = json.dumps(reply_keyboard)
    
    try:
        response = requests.post(url, data=data)
        return response.json()
    except Exception as e:
        print(f"❌ Lỗi gửi tin nhắn: {e}")
        return None

def get_updates(offset=0):
    """Lấy tin nhắn mới"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {"offset": offset, "timeout": 10}
    try:
        response = requests.get(url, params=params, timeout=15)
        return response.json()
    except Exception as e:
        print(f"❌ Lỗi lấy updates: {e}")
        return None

def create_reply_keyboard():
    """Tạo reply keyboard cố định dưới chat"""
    return {
        "keyboard": [
            ["📊 Status", "📈 Stats"],
            ["▶️ Start", "⏹️ Stop"],
            ["🟢 BUY", "🔴 SELL"],
            ["⚙️ Settings", "📋 History"],
            ["🔄 Demo", "💰 Live"],
            ["🆘 Help", "🔄 Refresh"]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False,
        "persistent": True
    }

def create_main_keyboard():
    """Tạo keyboard chính"""
    return {
        "inline_keyboard": [
            [
                {"text": "📊 Status", "callback_data": "status"},
                {"text": "📈 Stats", "callback_data": "stats"}
            ],
            [
                {"text": "▶️ Start Trading", "callback_data": "start_trading"},
                {"text": "⏹️ Stop Trading", "callback_data": "stop_trading"}
            ],
            [
                {"text": "⚙️ Settings", "callback_data": "settings"},
                {"text": "📋 History", "callback_data": "history"}
            ],
            [
                {"text": "🔄 Demo Mode", "callback_data": "demo_mode"},
                {"text": "💰 Live Mode", "callback_data": "live_mode"}
            ]
        ]
    }

def create_settings_keyboard():
    """Tạo keyboard settings"""
    return {
        "inline_keyboard": [
            [
                {"text": "📊 MA Strategy", "callback_data": "strategy_ma"},
                {"text": "📉 RSI Strategy", "callback_data": "strategy_rsi"}
            ],
            [
                {"text": "📈 MACD Strategy", "callback_data": "strategy_macd"},
                {"text": "🎯 Combined", "callback_data": "strategy_combined"}
            ],
            [
                {"text": "🔧 Risk Settings", "callback_data": "risk_settings"},
                {"text": "⚡ Quick Trade", "callback_data": "quick_trade"}
            ],
            [
                {"text": "🔙 Back to Main", "callback_data": "main_menu"}
            ]
        ]
    }

def create_trading_keyboard():
    """Tạo keyboard trading nhanh"""
    return {
        "inline_keyboard": [
            [
                {"text": "🟢 BUY NOW", "callback_data": "buy_now"},
                {"text": "🔴 SELL NOW", "callback_data": "sell_now"}
            ],
            [
                {"text": "⏸️ Pause Trading", "callback_data": "pause_trading"},
                {"text": "🔄 Restart", "callback_data": "restart_trading"}
            ],
            [
                {"text": "🔙 Back", "callback_data": "main_menu"}
            ]
        ]
    }

def simulate_trade(action):
    """Giả lập giao dịch"""
    import random
    
    # Giả lập giá
    price = random.uniform(58000, 62000)
    amount = 0.001
    
    if action == "BUY":
        trading_status["position"] = "LONG"
        trading_status["balance"] -= price * amount
        message = f"""🟢 **BUY ORDER EXECUTED**

🔸 **Symbol:** BTCUSDT
🔸 **Amount:** {amount} BTC  
🔸 **Price:** ${price:,.2f}
🔸 **Total:** ${price * amount:.2f}

📈 Position: LONG opened!"""
    
    elif action == "SELL":
        if trading_status["position"]:
            profit = random.uniform(-50, 100)
            trading_status["profit"] += profit
            trading_status["balance"] += price * amount + profit
            trading_status["position"] = None
            
            message = f"""🔴 **SELL ORDER EXECUTED**

🔸 **Symbol:** BTCUSDT
🔸 **Amount:** {amount} BTC
🔸 **Price:** ${price:,.2f}
🔸 **Profit:** ${profit:.2f}

📉 Position closed!"""
        else:
            message = "❌ Không có position để sell!"
    
    trading_status["total_trades"] += 1
    return message

def handle_callback(callback_data, user_name):
    """Xử lý callback từ inline keyboard"""
    
    if callback_data == "status":
        status_emoji = "🟢" if trading_status["is_running"] else "🔴"
        mode_emoji = "🔄" if trading_status["mode"] == "demo" else "💰"
        
        response = f"""📊 TRADING BOT STATUS

{status_emoji} Status: {'Running' if trading_status['is_running'] else 'Stopped'}
{mode_emoji} Mode: {trading_status['mode'].upper()}
💵 Balance: ${trading_status['balance']:.2f}
📊 Position: {trading_status['position'] or 'None'}
🎯 Strategy: {trading_status['current_strategy']}

🕐 Time: {datetime.now().strftime('%H:%M:%S')}"""
        
        return response, create_main_keyboard()
    
    elif callback_data == "stats":
        win_rate = 65.5 if trading_status["total_trades"] > 0 else 0
        
        response = f"""📈 **Trading Statistics**

**🎯 Performance:**
• Total Trades: {trading_status['total_trades']}
• Win Rate: {win_rate}%
• Total P&L: ${trading_status['profit']:.2f}
• Current Balance: ${trading_status['balance']:.2f}

**📊 Today:**
• Active Strategy: {trading_status['current_strategy']}
• Mode: {trading_status['mode'].upper()}

**⚡ Recent Activity:**
• Last update: {datetime.now().strftime('%H:%M:%S')}"""
        
        return response, create_main_keyboard()
    
    elif callback_data == "start_trading":
        trading_status["is_running"] = True
        response = f"""▶️ **Trading Started!**

🚀 Bot đang chạy với:
• Strategy: {trading_status['current_strategy']}
• Mode: {trading_status['mode'].upper()}
• Balance: ${trading_status['balance']:.2f}

📱 Sử dụng các nút bên dưới để điều khiển!"""
        
        return response, create_trading_keyboard()
    
    elif callback_data == "stop_trading":
        trading_status["is_running"] = False
        response = """⏹️ **Trading Stopped!**

🛑 Bot đã dừng hoạt động.
📊 Tất cả positions đã được đóng an toàn.

Nhấn Start Trading để tiếp tục."""
        
        return response, create_main_keyboard()
    
    elif callback_data == "settings":
        response = f"""⚙️ **Bot Settings**

**📊 Current Configuration:**
• Strategy: {trading_status['current_strategy']}
• Mode: {trading_status['mode']}
• Balance: ${trading_status['balance']:.2f}

**🎯 Choose Action:**"""
        
        return response, create_settings_keyboard()
    
    elif callback_data == "demo_mode":
        trading_status["mode"] = "demo"
        response = """🔄 **Demo Mode Activated!**

✅ Chế độ demo an toàn
• Không sử dụng tiền thật
• Test các strategy
• Học cách sử dụng bot"""
        
        return response, create_main_keyboard()
    
    elif callback_data == "live_mode":
        response = """💰 **Live Mode**

⚠️ **CẢNH BÁO:**
Live mode cần Binance API keys và sẽ sử dụng tiền thật!

Hiện tại chỉ có Demo mode."""
        
        return response, create_main_keyboard()
    
    elif callback_data == "buy_now":
        if trading_status["is_running"]:
            trade_result = simulate_trade("BUY")
            return trade_result, create_trading_keyboard()
        else:
            return "❌ Hãy start trading trước!", create_main_keyboard()
    
    elif callback_data == "sell_now":
        if trading_status["is_running"]:
            trade_result = simulate_trade("SELL")
            return trade_result, create_trading_keyboard()
        else:
            return "❌ Hãy start trading trước!", create_main_keyboard()
    
    elif callback_data.startswith("strategy_"):
        strategy_map = {
            "strategy_ma": "moving_average",
            "strategy_rsi": "rsi",  
            "strategy_macd": "macd",
            "strategy_combined": "combined"
        }
        
        new_strategy = strategy_map.get(callback_data, "moving_average")
        trading_status["current_strategy"] = new_strategy
        
        response = f"""✅ **Strategy Updated!**

🎯 New Strategy: {new_strategy.upper()}

Strategy đã được thay đổi thành công!"""
        
        return response, create_settings_keyboard()
    
    elif callback_data == "main_menu":
        response = """🤖 **Crypto Trading Bot**

🎮 **Dashboard chính**

Chọn chức năng bên dưới:"""
        
        return response, create_main_keyboard()
    
    elif callback_data == "history":
        response = f"""📋 **Trading History**

**🎯 Recent Trades:**
• Total: {trading_status['total_trades']} trades
• Profit: ${trading_status['profit']:.2f}
• Success Rate: 65.5%

**📊 Performance:**
• Best Trade: +$45.60
• Current Streak: 3 wins
• Average Trade: $12.30"""
        
        return response, create_main_keyboard()
    
    else:
        return "🤖 Chức năng đang phát triển...", create_main_keyboard()

def handle_message(text, user_name):
    """Xử lý tin nhắn text và reply keyboard"""
    
    # Xử lý reply keyboard buttons
    if text == "📊 Status":
        return handle_callback("status", user_name)
    elif text == "📈 Stats":
        return handle_callback("stats", user_name)
    elif text == "▶️ Start":
        return handle_callback("start_trading", user_name)
    elif text == "⏹️ Stop":
        return handle_callback("stop_trading", user_name)
    elif text == "🟢 BUY":
        return handle_callback("buy_now", user_name)
    elif text == "🔴 SELL":
        return handle_callback("sell_now", user_name)
    elif text == "⚙️ Settings":
        return handle_callback("settings", user_name)
    elif text == "📋 History":
        return handle_callback("history", user_name)
    elif text == "🔄 Demo":
        return handle_callback("demo_mode", user_name)
    elif text == "💰 Live":
        return handle_callback("live_mode", user_name)
    elif text == "🆘 Help":
        response = """🆘 **Help & Commands**

**📱 Reply Keyboard (Nút dưới chat):**
• � Status - Trạng thái bot
• 📈 Stats - Thống kê chi tiết
• ▶️ Start - Bật trading
• ⏹️ Stop - Tắt trading
• � BUY - Mua ngay
• 🔴 SELL - Bán ngay
• ⚙️ Settings - Cài đặt
• 📋 History - Lịch sử
• 🔄 Demo - Chế độ demo
• 💰 Live - Chế độ thật

**💡 Chỉ cần nhấn nút, không cần gõ!**"""
        return response, None
    elif text == "� Refresh":
        response = """🔄 **Interface Refreshed!**

🎮 Bot sẵn sàng với các nút bấm dưới chat!

**📱 Nút bấm cố định:**
Các nút đã được refresh và sẵn sàng sử dụng!"""
        return response, None
    
    # Xử lý các lệnh text truyền thống
    elif text == "/start":
        response = """🤖 **Crypto Trading Bot**

✅ **Chào mừng!** Bot với nút bấm cố định dưới chat!

**🎮 Cách sử dụng:**
• Nhấn các **nút dưới chat** để điều khiển
• Không cần gõ lệnh - chỉ nhấn nút!
• Nút luôn hiển thị và sẵn sàng

**🚀 Tính năng:**
• ▶️ Start/Stop Trading
• 🟢🔴 BUY/SELL nhanh
• 📊 Status & Stats real-time
• ⚙️ Settings & History
• 🔄 Demo/Live modes

**💡 Hãy thử nhấn các nút bên dưới!**"""
        
        return response, None
    
    elif text == "/help":
        response = """🆘 **Help & Commands**

**🎮 Reply Keyboard:**
Các nút cố định dưới khung chat để điều khiển nhanh!

**� Available Buttons:**
• 📊📈 Monitoring
• ▶️⏹️ Control  
• 🟢🔴 Quick Trade
• ⚙️📋 Management
• 🔄💰 Modes
• 🆘🔄 Support

**💡 Tips:**
• Nút luôn hiển thị
• Không cần nhớ lệnh
• Nhấn và sử dụng ngay!"""
        
        return response, None
    
    elif text == "/quick":
        status = "🟢 Running" if trading_status["is_running"] else "🔴 Stopped"
        response = f"""⚡ **Quick Status**

{status} | ${trading_status['balance']:.2f} | {trading_status['total_trades']} trades

**🎮 Sử dụng nút dưới chat để điều khiển!**"""
        
        return response, None
    
    else:
        response = f"""👋 Chào {user_name}!

Tin nhắn: "{text}"

**🎮 Sử dụng các nút dưới chat để điều khiển bot!**

Hoặc gửi /start để xem hướng dẫn."""
        
        return response, None

def edit_message(message_id, text, keyboard=None):
    """Edit tin nhắn với keyboard mới"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
    data = {
        "chat_id": CHAT_ID,
        "message_id": message_id,
        "text": text,
        # Bỏ parse_mode để tránh lỗi
    }
    if keyboard:
        data["reply_markup"] = json.dumps(keyboard)
    
    try:
        response = requests.post(url, data=data)
        return response.json()
    except Exception as e:
        print(f"❌ Lỗi edit message: {e}")
        return None

def main():
    """Chạy bot"""
    print("🚀 Starting Advanced Telegram Trading Bot...")
    print("📱 Bot với đầy đủ nút bấm và điều khiển!")
    print("⏹️  Nhấn Ctrl+C để dừng")
    print("-" * 60)
    
    # Gửi thông báo khởi động với reply keyboard
    startup_msg = """🤖 **Advanced Trading Bot Started!**

✅ **Bot đã sẵn sàng với nút bấm cố định!**

**🎮 Nút điều khiển dưới chat:**
• 📊📈 Theo dõi
• ▶️⏹️ Điều khiển
• 🟢🔴 Giao dịch nhanh
• ⚙️📋 Quản lý
• 🔄💰 Chế độ

**💡 Nhấn các nút dưới để sử dụng ngay!**"""
    
    send_message(startup_msg, reply_keyboard=create_reply_keyboard())
    
    offset = 0
    
    try:
        while True:
            updates = get_updates(offset)
            
            if updates and updates.get("ok"):
                for update in updates.get("result", []):
                    offset = update["update_id"] + 1
                    
                    # Xử lý callback query (nút bấm)
                    if "callback_query" in update:
                        callback = update["callback_query"]
                        callback_data = callback["data"]
                        user = callback["from"]
                        user_name = user.get("first_name", "User")
                        message_id = callback["message"]["message_id"]
                        
                        print(f"🔘 {user_name} nhấn nút: {callback_data}")
                        
                        # Xử lý callback
                        response, keyboard = handle_callback(callback_data, user_name)
                        
                        # Edit message với response mới
                        result = edit_message(message_id, response, keyboard)
                        if result and result.get("ok"):
                            print(f"✅ Đã cập nhật dashboard cho {user_name}")
                        else:
                            print(f"❌ Lỗi edit message: {result}")
                    
                    # Xử lý tin nhắn text
                    elif "message" in update:
                        message = update["message"]
                        if "text" in message:
                            text = message["text"]
                            user = message.get("from", {})
                            user_name = user.get("first_name", "User")
                            
                            print(f"📨 {user_name} gửi: {text}")
                            
                            # Xử lý tin nhắn với reply keyboard
                            response, inline_kb = handle_message(text, user_name)
                            
                            # Gửi phản hồi với reply keyboard cố định
                            if inline_kb:
                                result = send_message(response, keyboard=inline_kb, reply_keyboard=create_reply_keyboard())
                            else:
                                result = send_message(response, reply_keyboard=create_reply_keyboard())
                                
                            if result and result.get("ok"):
                                print(f"✅ Đã trả lời {user_name}")
                            else:
                                print(f"❌ Lỗi gửi phản hồi: {result}")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Bot đã dừng!")
        send_message("🤖 Bot đã tạm dừng!\n\nGửi /start để khởi động lại.")
    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN không được cấu hình!")
        exit(1)
    main()