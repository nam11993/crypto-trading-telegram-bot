"""
Test Telegram Bot Integration
"""

import sys
import os
import asyncio
from datetime import datetime

# Add src directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.telegram_bot import TelegramNotifier
from config.config import Config

class MockTradingBot:
    """Mock trading bot for testing"""
    def __init__(self):
        self.symbol = 'BTCUSDT'
        self.price_history = [45000, 45500, 46000, 45800, 46200]
        self.is_running = True
        
        class MockStrategy:
            def __init__(self):
                self.position = 'LONG'
                self.entry_price = 45000
                
        class MockDatabase:
            def get_trading_statistics(self):
                return {
                    'total_trades': 15,
                    'profitable_trades': 12,
                    'win_rate': 80.0,
                    'total_pnl': 145.67,
                    'best_trade_percent': 15.2,
                    'worst_trade_percent': -3.4
                }
        
        self.strategy = MockStrategy()
        self.database = MockDatabase()

def test_telegram_integration():
    """Test Telegram bot integration"""
    
    print("🤖 Testing Telegram Bot Integration")
    print("=" * 40)
    
    # Check configuration
    if not Config.TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN chưa được cấu hình!")
        print("Hãy:")
        print("1. Tạo bot với @BotFather")
        print("2. Thêm token vào file .env")
        return False
    
    if not Config.TELEGRAM_CHAT_ID:
        print("❌ TELEGRAM_CHAT_ID chưa được cấu hình!")
        print("Hãy:")
        print("1. Chạy: python get_chat_id.py")
        print("2. Thêm chat ID vào file .env")
        return False
    
    print(f"✅ Bot Token: {Config.TELEGRAM_BOT_TOKEN[:10]}...")
    print(f"✅ Chat ID: {Config.TELEGRAM_CHAT_ID}")
    
    # Create mock trading bot
    mock_bot = MockTradingBot()
    
    # Initialize Telegram notifier
    print("\n📱 Initializing Telegram Bot...")
    telegram = TelegramNotifier(mock_bot)
    
    if not telegram.application:
        print("❌ Failed to initialize Telegram bot")
        return False
    
    print("✅ Telegram bot initialized successfully!")
    
    # Start bot
    print("\n🚀 Starting Telegram bot...")
    telegram.start_bot()
    
    # Send test notifications
    print("\n📤 Sending test notifications...")
    
    try:
        # Test startup notification
        telegram.send_notification_sync("""
🧪 **TEST NOTIFICATION**

Đây là test notification từ Trading Bot!

Bot đã khởi động thành công và sẵn sàng nhận lệnh.

Gửi `/help` để xem danh sách lệnh có sẵn!
        """)
        print("✅ Startup notification sent")
        
        # Test trade notification
        telegram.notify_trade('BUY', 'BTCUSDT', 0.001, 46000)
        print("✅ Buy notification sent")
        
        # Wait a bit
        import time
        time.sleep(2)
        
        # Test sell notification
        telegram.notify_trade('SELL', 'BTCUSDT', 0.001, 47000, 2.17)
        print("✅ Sell notification sent")
        
        # Test signal notification
        telegram.notify_signal('BUY', 'BTCUSDT', 46500, 'moving_average')
        print("✅ Signal notification sent")
        
        print(f"\n🎉 All notifications sent successfully!")
        print(f"📱 Check your Telegram for messages!")
        
        print(f"\n🕒 Bot will run for 2 minutes to test commands...")
        print(f"📝 Try these commands in Telegram:")
        print(f"   /start - Main menu")
        print(f"   /status - Bot status") 
        print(f"   /stats - Trading statistics")
        print(f"   /help - Help menu")
        
        # Keep running for 2 minutes
        time.sleep(120)
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False
    
    finally:
        # Stop bot
        print(f"\n⏹️ Stopping Telegram bot...")
        telegram.stop_bot()
        print(f"✅ Test completed!")
    
    return True

def main():
    """Main test function"""
    try:
        success = test_telegram_integration()
        if success:
            print(f"\n🎉 Telegram integration test PASSED!")
            print(f"Bot sẵn sàng để sử dụng với Telegram!")
        else:
            print(f"\n❌ Telegram integration test FAILED!")
            print(f"Kiểm tra lại cấu hình và thử lại.")
            
    except KeyboardInterrupt:
        print(f"\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()