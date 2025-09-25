#!/usr/bin/env python3
import requests
from config.config import Config

config = Config()
BOT_TOKEN = config.TELEGRAM_BOT_TOKEN
CHAT_ID = config.TELEGRAM_CHAT_ID

def test_send():
    text = "🧪 TEST MESSAGE - Bot có thể gửi tin nhắn!"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    response = requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text
    })
    
    result = response.json()
    print("Response:", result)
    
    if result.get("ok"):
        print("✅ GỬI THÀNH CÔNG!")
    else:
        print("❌ GỬI THẤT BẠI!")
        print("Error:", result.get("description"))

if __name__ == "__main__":
    test_send()