#!/usr/bin/env python3
"""
🤖 Telegram Bot Test - Rất đơn giản
Chỉ nhận lệnh /start và trả lời
"""
import time
import requests
import json
from config.config import Config

# Lấy config
config = Config()
BOT_TOKEN = config.TELEGRAM_BOT_TOKEN
CHAT_ID = config.TELEGRAM_CHAT_ID

if not BOT_TOKEN:
    print("❌ TELEGRAM_BOT_TOKEN không được cấu hình!")
    exit(1)

print(f"✅ Bot Token: {BOT_TOKEN[:10]}...")
print(f"✅ Chat ID: {CHAT_ID}")
print()

def send_message(message):
    """Gửi tin nhắn"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
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

def handle_command(message_text, user_name):
    """Xử lý lệnh"""
    if message_text == "/start":
        response = f"""🤖 **Crypto Trading Bot**

Xin chào {user_name}! Bot đã hoạt động.

**📱 Commands:**
/start - Menu chính
/status - Trạng thái bot
/help - Trợ giúp

**🚀 Bot sẵn sàng!**"""
        return response
    
    elif message_text == "/status":
        response = """📊 **Bot Status**

✅ Status: Online
🤖 Mode: Demo
💰 Balance: $1000.00 (Demo)
🕐 Running time: Active"""
        return response
    
    elif message_text == "/help":
        response = """🆘 **Help**

**Commands:**
/start - Khởi động
/status - Trạng thái
/help - Trợ giúp

**💡 Bot đang ở chế độ demo an toàn**"""
        return response
    
    else:
        response = f"""👋 Chào {user_name}!

Bạn gửi: "{message_text}"

Thử các lệnh:
/start /status /help"""
        return response

def main():
    """Chạy bot"""
    print("🚀 Starting Simple Telegram Bot...")
    print("📱 Bot sẵn sàng nhận lệnh!")
    print("⏹️  Nhấn Ctrl+C để dừng")
    print("-" * 50)
    
    # Gửi thông báo khởi động
    send_message("🤖 **Bot Started!**\n\nBot đã sẵn sàng nhận lệnh!\nGửi /start để bắt đầu.")
    
    offset = 0
    
    try:
        while True:
            # Lấy updates
            updates = get_updates(offset)
            
            if updates and updates.get("ok"):
                for update in updates.get("result", []):
                    # Cập nhật offset
                    offset = update["update_id"] + 1
                    
                    # Kiểm tra có tin nhắn không
                    if "message" in update:
                        message = update["message"]
                        if "text" in message:
                            text = message["text"]
                            user = message.get("from", {})
                            user_name = user.get("first_name", "User")
                            
                            print(f"📨 Nhận tin nhắn từ {user_name}: {text}")
                            
                            # Xử lý lệnh
                            response = handle_command(text, user_name)
                            
                            # Gửi phản hồi
                            result = send_message(response)
                            if result and result.get("ok"):
                                print(f"✅ Đã trả lời cho {user_name}")
                            else:
                                print(f"❌ Lỗi gửi phản hồi: {result}")
            
            time.sleep(1)  # Chờ 1 giây
            
    except KeyboardInterrupt:
        print("\n⏹️  Bot đã dừng!")
    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    main()