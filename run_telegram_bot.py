#!/usr/bin/env python3
"""
🤖 Chạy Demo Trading Bot với Telegram
"""

import sys
import os

# Thêm thư mục gốc vào path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🤖 Starting Demo Trading Bot với Telegram...")
print("=" * 60)
print("📱 Bot sẽ gửi thông báo và nhận lệnh từ Telegram!")
print("� Giao dịch giả lập an toàn (không ảnh hưởng tiền thật)")
print("⏹️  Nhấn Ctrl+C để dừng")
print("=" * 60)

# Import và chạy demo
try:
    exec(open("demo.py").read())
except KeyboardInterrupt:
    print("\n⏹️  Bot đã dừng!")
except Exception as e:
    print(f"❌ Lỗi: {e}")