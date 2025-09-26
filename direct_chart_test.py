#!/usr/bin/env python3
"""Simple direct test of chart sending"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def direct_chart_test():
    """Direct test without bot polling"""
    
    # Import after path setup
    from config.config import Config
    from src.binance_chart import BinanceLikeChart
    import requests
    
    # Config
    config = Config()
    BOT_TOKEN = config.TELEGRAM_BOT_TOKEN
    CHAT_ID = config.TELEGRAM_CHAT_ID
    
    print("🔧 DIRECT CHART TEST")
    print("=" * 40)
    
    # 1. Generate chart
    print("📊 Generating chart...")
    try:
        chart_gen = BinanceLikeChart()
        image_path = chart_gen.generate_professional_chart('BTCUSDT', '1h', 50)
        print(f"✅ Chart: {image_path}")
        
        if not os.path.exists(image_path):
            print(f"❌ File not found!")
            return
            
    except Exception as e:
        print(f"❌ Generate error: {e}")
        return
    
    # 2. Send directly
    print("📤 Sending to Telegram...")
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        
        with open(image_path, 'rb') as photo:
            files = {'photo': photo}
            data = {
                'chat_id': CHAT_ID,
                'caption': '📈 DIRECT TEST CHART\n\n🧪 Nếu bạn thấy ảnh này, chart system hoạt động OK!'
            }
            
            response = requests.post(url, files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    print("✅ SUCCESS: Ảnh đã gửi!")
                    print(f"Message ID: {result['result']['message_id']}")
                else:
                    print(f"❌ Telegram error: {result}")
            else:
                print(f"❌ HTTP {response.status_code}: {response.text}")
                
    except Exception as e:
        print(f"❌ Send error: {e}")
        
    # Cleanup
    try:
        os.remove(image_path) 
        print("🗑️ Cleaned up")
    except:
        pass

if __name__ == "__main__":
    direct_chart_test()