#!/usr/bin/env python3
"""
🚨 Simple Alert Test Bot - Debug alerts issue
"""
import logging
import time
import requests
import json
import sys
import os

# Thêm src vào path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config.config import Config

# Config
config = Config()
BOT_TOKEN = config.TELEGRAM_BOT_TOKEN
CHAT_ID = config.TELEGRAM_CHAT_ID

print("🧪 Testing Simple Alert Bot...")
print(f"BOT_TOKEN: {'✅ SET' if BOT_TOKEN else '❌ NOT SET'}")
print(f"CHAT_ID: {'✅ SET' if CHAT_ID else '❌ NOT SET'}")

# Try to import PriceAlertSystem
try:
    from src.price_alert_system import PriceAlertSystem
    print("✅ PriceAlertSystem imported successfully")
    
    # Initialize alert system
    alert_system = PriceAlertSystem(BOT_TOKEN, CHAT_ID)
    print("✅ PriceAlertSystem initialized successfully")
    
    # Test basic functions
    settings = alert_system.get_alert_settings()
    stats = alert_system.get_alert_stats()
    
    print(f"✅ Settings: {settings}")
    print(f"✅ Stats: {stats}")
    
except Exception as e:
    print(f"❌ Error with PriceAlertSystem: {e}")
    print("This is the problem with alerts!")

# Simple bot function
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
    """Tạo keyboard test"""
    return {
        "keyboard": [
            ["🚨 Test Alert", "⚙️ Test Settings"],
            ["📊 Status", "🆘 Help"]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }

def handle_message(text, user_name):
    """Xử lý tin nhắn"""
    
    if text == "/start":
        response = f"""🧪 SIMPLE ALERT TEST BOT

Xin chào {user_name}!

Testing alerts functionality:
• 🚨 Test Alert - Test alert system
• ⚙️ Test Settings - Test settings
• 📊 Status - Bot status

Bot này để debug alert issue."""
        return response
    
    elif text == "🚨 Test Alert":
        try:
            if 'alert_system' in globals():
                stats = alert_system.get_alert_stats()
                settings = alert_system.get_alert_settings()
                
                response = f"""🚨 ALERT TEST RESULT

✅ Alert System: WORKING
📊 Stats: {stats}
⚙️ Settings: Pump {settings['pump_threshold']}%, Dump {settings['dump_threshold']}%

✅ Alert system hoạt động bình thường!"""
            else:
                response = """❌ ALERT TEST FAILED

🚫 Alert system không available
💡 Đây là nguyên nhân tại sao alerts không hoạt động!"""
        except Exception as e:
            response = f"""❌ ALERT TEST ERROR

🚫 Error: {str(e)}
💡 Đây là lỗi alerts!"""
            
        return response
    
    elif text == "⚙️ Test Settings":
        try:
            if 'alert_system' in globals():
                settings = alert_system.get_alert_settings()
                response = f"""⚙️ SETTINGS TEST

✅ Alert Settings:
• Pump: {settings['pump_threshold']}%
• Dump: {settings['dump_threshold']}%
• Volume: {settings['volume_spike_multiplier']}x
• Min Volume: {settings['min_volume_usdt']:,}

✅ Settings đọc thành công!"""
            else:
                response = """❌ SETTINGS TEST FAILED

🚫 Alert system không tồn tại
💡 Không thể đọc settings!"""
        except Exception as e:
            response = f"""❌ SETTINGS ERROR

🚫 Error: {str(e)}"""
            
        return response
    
    elif text == "📊 Status":
        response = f"""📊 BOT STATUS

✅ Bot: RUNNING
🔧 Alert System: {'✅ OK' if 'alert_system' in globals() else '❌ FAILED'}
💬 Telegram: {'✅ OK' if BOT_TOKEN and CHAT_ID else '❌ FAILED'}

Debug info cho alerts issue."""
        return response
    
    else:
        response = f"""👋 Hello {user_name}!

Bạn gửi: "{text}"
Sử dụng các nút bên dưới để test!"""
        return response

def main():
    """Main function"""
    print("🧪 Starting Simple Alert Test Bot...")
    
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Missing BOT_TOKEN or CHAT_ID!")
        return
    
    # Send startup message
    startup = """🧪 SIMPLE ALERT TEST BOT STARTED!

Bot này để debug alert system issue.
Nhấn các nút để test functionality."""
    
    send_message(startup)
    result = send_message("Test keyboard", create_keyboard())
    
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
                            
                            # Handle message
                            response = handle_message(text, user_name)
                            
                            # Send response with keyboard
                            result = send_message(response)
                            result2 = send_message("Use buttons:", create_keyboard())
                            
                            if result and result.get("ok"):
                                print(f"✅ Replied to {user_name}")
                            else:
                                print(f"❌ Error: {result}")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Bot stopped!")
        send_message("🧪 Alert Test Bot stopped!")

if __name__ == "__main__":
    main()