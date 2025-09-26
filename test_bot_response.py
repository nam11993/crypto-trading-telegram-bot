#!/usr/bin/env python3
"""
Test bot response với các lệnh khác nhau
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def send_test_message(text):
    """Send test message to check bot response"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': CHAT_ID,
        'text': f"🧪 TEST: {text}",
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(url, data=data)
        result = response.json()
        if result.get('ok'):
            print(f"✅ Sent test: {text}")
        else:
            print(f"❌ Failed: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")

def check_bot_status():
    """Check if bot is running"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
    try:
        response = requests.get(url)
        result = response.json()
        if result.get('ok'):
            bot_info = result.get('result', {})
            print(f"🤖 Bot Status: {bot_info.get('first_name')} (@{bot_info.get('username')})")
            print(f"✅ Bot is {('active' if bot_info.get('can_read_all_group_messages') else 'active')}")
            return True
        else:
            print(f"❌ Bot error: {result}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 BOT RESPONSE TEST")
    print("-" * 40)
    
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Missing credentials")
        exit(1)
    
    # Check bot status
    if not check_bot_status():
        print("❌ Bot không hoạt động!")
        exit(1)
    
    print("\n🚀 Sending test commands...")
    
    # Test various commands
    test_commands = [
        "/start",
        "BTC",
        "ETH 4h", 
        "💹 Prices",
        "hello",
        "DOGE",
        "help"
    ]
    
    for cmd in test_commands:
        send_test_message(cmd)
        import time
        time.sleep(2)  # Wait between messages
        
    print("\n✅ Test completed! Check Telegram for bot responses.")