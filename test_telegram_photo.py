#!/usr/bin/env python3
"""Test sending photo via Telegram API"""

import requests
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config.config import Config
from src.binance_chart import BinanceLikeChart

def test_telegram_photo():
    """Test sending photo via Telegram API"""
    
    # Load config
    config = Config()
    BOT_TOKEN = config.TELEGRAM_BOT_TOKEN
    CHAT_ID = config.TELEGRAM_CHAT_ID
    
    print("🧪 TESTING TELEGRAM PHOTO SENDING")
    print("=" * 50)
    print(f"Bot Token: {BOT_TOKEN[:20]}...")
    print(f"Chat ID: {CHAT_ID}")
    
    # 1. Generate chart
    try:
        print("\n📊 Step 1: Generating chart...")
        chart_gen = BinanceLikeChart()
        image_path = chart_gen.generate_professional_chart('BTCUSDT', '1h')
        print(f"✅ Chart generated: {image_path}")
        
        # Check file exists
        if not os.path.exists(image_path):
            print(f"❌ Chart file not found: {image_path}")
            return
        
        file_size = os.path.getsize(image_path)
        print(f"📏 File size: {file_size} bytes")
        
    except Exception as e:
        print(f"❌ Chart generation failed: {e}")
        return
    
    # 2. Test Telegram API
    try:
        print(f"\n📤 Step 2: Sending photo via Telegram...")
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        
        caption = """📈 BTC/USDT TEST CHART

🧪 This is a test chart to verify image sending works correctly.

🕯️ HƯỚNG DẪN:
🟢 Nến xanh: Giá đóng > mở
🔴 Nến đỏ: Giá đóng < mở
📊 Test successful if you see this image!"""
        
        with open(image_path, 'rb') as photo:
            files = {'photo': photo}
            data = {
                'chat_id': CHAT_ID,
                'caption': caption
            }
            
            print(f"📞 Calling Telegram API...")
            response = requests.post(url, files=files, data=data, timeout=30)
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    print("✅ SUCCESS: Photo sent to Telegram!")
                    print(f"📨 Message ID: {result['result']['message_id']}")
                else:
                    print(f"❌ Telegram API Error: {result}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                
    except Exception as e:
        print(f"❌ Telegram API call failed: {e}")
    
    # 3. Cleanup
    try:
        os.remove(image_path)
        print(f"🗑️ Cleaned up: {image_path}")
    except:
        pass

if __name__ == "__main__":
    test_telegram_photo()