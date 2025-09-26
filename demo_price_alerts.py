#!/usr/bin/env python3
"""
Demo Price Alert System - Simulation với fake data
Tạo fake alerts để test notification system
"""
import sys
import os
import time
import random
from datetime import datetime

# Thêm src vào path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config.config import Config
from src.price_alert_system import PriceAlertSystem

def simulate_pump_dump_alert(alert_system, symbol="DOGEUSDT"):
    """Simulate một pump/dump alert"""
    
    # Fake ticker data for pump
    pump_ticker = {
        'symbol': symbol,
        'lastPrice': '0.08500',
        'priceChangePercent': '18.5',  # Pump 18.5%
        'quoteVolume': '15000000'  # 15M USDT volume
    }
    
    print(f"📤 Sending PUMP alert for {symbol}...")
    alert_system._send_pump_alert(symbol, pump_ticker)
    
    time.sleep(3)
    
    # Fake ticker data for dump
    dump_ticker = {
        'symbol': symbol,
        'lastPrice': '0.06200',
        'priceChangePercent': '-22.3',  # Dump -22.3%
        'quoteVolume': '25000000'  # 25M USDT volume
    }
    
    print(f"📤 Sending DUMP alert for {symbol}...")
    alert_system._send_dump_alert(symbol, dump_ticker)

def simulate_volume_spike_alert(alert_system, symbol="SHIBUSDT"):
    """Simulate volume spike alert"""
    
    volume_ticker = {
        'symbol': symbol,
        'lastPrice': '0.00002150',
        'priceChangePercent': '8.2',
        'quoteVolume': '45000000'  # 45M USDT volume spike
    }
    
    print(f"📤 Sending VOLUME SPIKE alert for {symbol}...")
    alert_system._send_volume_spike_alert(symbol, volume_ticker)

def simulate_breakout_alert(alert_system, symbol="BTCUSDT"):
    """Simulate breakout alert"""
    
    breakout_ticker = {
        'symbol': symbol,
        'lastPrice': '72500.00',
        'priceChangePercent': '12.8',  # Breakout upward
        'quoteVolume': '120000000'  # 120M USDT volume
    }
    
    print(f"📤 Sending BREAKOUT alert for {symbol}...")
    alert_system._send_breakout_alert(symbol, breakout_ticker)

def main():
    print("🚨 Demo Price Alert System - Simulation Mode")
    print("=" * 50)
    
    # Load config
    config = Config()
    BOT_TOKEN = config.TELEGRAM_BOT_TOKEN
    CHAT_ID = config.TELEGRAM_CHAT_ID
    
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Missing BOT_TOKEN or CHAT_ID in .env file!")
        return
    
    # Create alert system
    alert_system = PriceAlertSystem(BOT_TOKEN, CHAT_ID)
    
    print("\n🎯 Sending demo alerts to Telegram...")
    
    # Send startup message
    startup_msg = """🧪 DEMO PRICE ALERT SYSTEM

🎯 Testing các loại alerts:
• PUMP Alert (DOGE +18.5%)
• DUMP Alert (DOGE -22.3%) 
• VOLUME SPIKE (SHIB)
• BREAKOUT Alert (BTC)

⚠️ Đây là DEMO - không phải alerts thực!"""
    
    alert_system._send_telegram_message(startup_msg)
    time.sleep(2)
    
    # Simulate different types of alerts
    print("\n1. Testing PUMP & DUMP alerts...")
    simulate_pump_dump_alert(alert_system, "DOGEUSDT")
    
    time.sleep(3)
    
    print("\n2. Testing VOLUME SPIKE alert...")
    simulate_volume_spike_alert(alert_system, "SHIBUSDT")
    
    time.sleep(3)
    
    print("\n3. Testing BREAKOUT alert...")
    simulate_breakout_alert(alert_system, "BTCUSDT")
    
    time.sleep(2)
    
    # Send completion message
    completion_msg = """✅ DEMO ALERTS COMPLETED!

🎉 Tất cả các loại alerts đã được test:
• ✅ Pump Alert
• ✅ Dump Alert  
• ✅ Volume Spike Alert
• ✅ Breakout Alert

💡 Để sử dụng alerts thực:
• Gửi "start alerts" trong bot
• Alerts sẽ tự động phát hiện biến động thực tế
• Có thể điều chỉnh threshold qua "⚙️ Alert Settings"

🚨 Price Alert System sẵn sàng!"""
    
    alert_system._send_telegram_message(completion_msg)
    
    print("\n🎉 Demo completed! Check your Telegram for alerts.")
    print("💡 Giờ bạn có thể sử dụng 'start alerts' trong bot để bắt đầu monitoring thực tế!")

if __name__ == "__main__":
    main()