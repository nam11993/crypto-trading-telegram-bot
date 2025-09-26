#!/usr/bin/env python3
"""
Quick test for PNG chart image sending
"""
import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Get Telegram credentials
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

async def send_chart_image(chat_id, image_path, caption=""):
    """Send chart image to Telegram"""
    import aiohttp
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return False
        
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    
    try:
        async with aiohttp.ClientSession() as session:
            with open(image_path, 'rb') as photo:
                data = aiohttp.FormData()
                data.add_field('chat_id', chat_id)
                data.add_field('photo', photo, filename='chart.png')
                data.add_field('caption', caption)
                
                async with session.post(url, data=data) as response:
                    result = await response.json()
                    
                    if result.get('ok'):
                        print("✅ Chart image sent successfully!")
                        return True
                    else:
                        print(f"❌ Error: {result.get('description', 'Unknown error')}")
                        return False
                        
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

async def test_png_chart():
    """Test PNG chart generation and sending"""
    try:
        from binance_chart import BinanceLikeChart
        
        print("🔧 Testing PNG Chart Generation...")
        chart_generator = BinanceLikeChart()
        chart_path = chart_generator.generate_professional_chart('BTCUSDT', '1h', 50)
        
        if chart_path and os.path.exists(chart_path):
            print(f"✅ Chart generated: {chart_path}")
            
            caption = """🕯️ BTC TEST CHART - 1 Giờ

💰 STATS:
• This is a test chart
• Professional PNG generation
• Binance-style candlesticks

📊 Chart test successful!"""
            
            result = await send_chart_image(CHAT_ID, chart_path, caption)
            if result:
                print("🎉 PNG Chart test completed successfully!")
            else:
                print("❌ Failed to send chart image")
        else:
            print("❌ Failed to generate chart")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    print("🧪 PNG Chart Sending Test")
    print("-" * 40)
    
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Missing BOT_TOKEN or CHAT_ID")
        exit(1)
    
    asyncio.run(test_png_chart())