#!/usr/bin/env python3
"""
Test Price Alert System
"""
import sys
import os
import time
from datetime import datetime

# Thêm src vào path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config.config import Config
from src.price_alert_system import PriceAlertSystem

def main():
    print("🧪 Testing Price Alert System...")
    
    # Load config
    config = Config()
    BOT_TOKEN = config.TELEGRAM_BOT_TOKEN
    CHAT_ID = config.TELEGRAM_CHAT_ID
    
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Missing BOT_TOKEN or CHAT_ID in .env file!")
        return
    
    # Create alert system
    alert_system = PriceAlertSystem(BOT_TOKEN, CHAT_ID)
    
    # Test basic functionality
    print("\n📊 Testing basic functions...")
    
    # Test settings
    settings = alert_system.get_alert_settings()
    print(f"✅ Default settings: {settings}")
    
    # Test stats
    stats = alert_system.get_alert_stats()
    print(f"✅ Initial stats: {stats}")
    
    # Test settings update
    print("\n⚙️ Testing settings update...")
    alert_system.update_alert_settings(pump_threshold=20.0, dump_threshold=-20.0)
    updated_settings = alert_system.get_alert_settings()
    print(f"✅ Updated settings: pump={updated_settings['pump_threshold']}%, dump={updated_settings['dump_threshold']}%")
    
    # Test monitoring start (short test)
    print("\n🚨 Testing alert monitoring (30 seconds)...")
    test_symbols = ['BTCUSDT', 'ETHUSDT', 'DOGEUSDT', 'SHIBUSDT', 'PEPEUSDT']
    
    print(f"Starting monitoring for {test_symbols}...")
    alert_system.start_monitoring(test_symbols)
    
    print("Monitoring for 30 seconds...")
    time.sleep(30)
    
    # Check stats after monitoring
    final_stats = alert_system.get_alert_stats()
    print(f"✅ Final stats after 30s: {final_stats}")
    
    # Stop monitoring
    alert_system.stop_monitoring()
    print("✅ Monitoring stopped")
    
    print("\n🎉 Price Alert System test completed!")
    print("\n💡 Để test thực tế:")
    print("1. Chạy price_bot.py")
    print("2. Gửi 'start alerts' trong Telegram")
    print("3. Đợi các biến động thị trường")
    
if __name__ == "__main__":
    main()