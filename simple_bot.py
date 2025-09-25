#!/usr/bin/env python3
"""
🤖 Simple Telegram Bot - Nhận và trả lời lệnh
Không có async conflict
"""

import sys
import os
import time
import threading

# Thêm thư mục gốc vào path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from config.config import Config

class SimpleTelegramBot:
    def __init__(self):
        self.config = Config()
        if not self.config.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN không được cấu hình!")
        
        # Tạo bot với python-telegram-bot v13 (sync version)
        self.updater = Updater(token=self.config.TELEGRAM_BOT_TOKEN, use_context=True)
        self.dispatcher = self.updater.dispatcher
        
        # Đăng ký handlers
        self.dispatcher.add_handler(CommandHandler('start', self.start))
        self.dispatcher.add_handler(CommandHandler('status', self.status))
        self.dispatcher.add_handler(CommandHandler('stats', self.stats))
        self.dispatcher.add_handler(CommandHandler('help', self.help_command))
        self.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.handle_message))
        
        print(f"✅ Bot initialized với token: {self.config.TELEGRAM_BOT_TOKEN[:10]}...")
        print(f"✅ Chat ID: {self.config.TELEGRAM_CHAT_ID}")

    def start(self, update, context):
        """Xử lý lệnh /start"""
        welcome_text = """🤖 **Crypto Trading Bot**

Chào mừng! Bot đang hoạt động.

**📱 Commands:**
/status - Trạng thái bot
/stats - Thống kê giao dịch  
/help - Trợ giúp

**🚀 Bot đã sẵn sàng!**"""
        
        update.message.reply_text(welcome_text, parse_mode='Markdown')
        print(f"✅ Đã trả lời /start cho {update.effective_user.first_name}")

    def status(self, update, context):
        """Xử lý lệnh /status"""
        from datetime import datetime
        status_text = f"""📊 **Bot Status**

🕐 Time: {datetime.now().strftime('%H:%M:%S')}
✅ Status: Active
🤖 Mode: Demo/Test

**💰 Portfolio:**
• Balance: $1000.00 (Demo)
• Position: None
• P&L: $0.00"""
        
        update.message.reply_text(status_text, parse_mode='Markdown')
        print(f"✅ Đã trả lời /status cho {update.effective_user.first_name}")

    def stats(self, update, context):
        """Xử lý lệnh /stats"""
        stats_text = """📈 **Trading Statistics**

**🎯 Performance:**
• Total Trades: 0
• Win Rate: 0%
• Total P&L: $0.00

**📊 Today:**
• Trades: 0
• Profit: $0.00

*Demo mode - No real trades*"""
        
        update.message.reply_text(stats_text, parse_mode='Markdown')
        print(f"✅ Đã trả lời /stats cho {update.effective_user.first_name}")

    def help_command(self, update, context):
        """Xử lý lệnh /help"""
        help_text = """🆘 **Help - Commands**

**📱 Available Commands:**

/start - Khởi động bot
/status - Xem trạng thái
/stats - Thống kê giao dịch
/help - Hiển thị trợ giúp

**💡 Tips:**
• Bot đang ở chế độ demo
• Không có giao dịch thật
• An toàn 100%

**🔧 Status:** ✅ Online"""
        
        update.message.reply_text(help_text, parse_mode='Markdown')
        print(f"✅ Đã trả lời /help cho {update.effective_user.first_name}")

    def handle_message(self, update, context):
        """Xử lý tin nhắn thông thường"""
        message = update.message.text
        response = f"""👋 Chào {update.effective_user.first_name}!

Bạn vừa gửi: "{message}"

Hãy sử dụng các lệnh:
/start - Bắt đầu
/status - Trạng thái  
/help - Trợ giúp"""
        
        update.message.reply_text(response)
        print(f"✅ Đã trả lời tin nhắn cho {update.effective_user.first_name}: {message}")

    def run(self):
        """Chạy bot"""
        print("🚀 Starting Telegram bot...")
        print("📱 Bot sẵn sàng nhận lệnh từ Telegram!")
        print("⏹️  Nhấn Ctrl+C để dừng")
        print("-" * 50)
        
        try:
            # Khởi động bot với polling
            self.updater.start_polling()
            print("✅ Bot đang chạy và lắng nghe tin nhắn...")
            
            # Giữ bot chạy
            self.updater.idle()
            
        except KeyboardInterrupt:
            print("\n⏹️  Đang dừng bot...")
            self.updater.stop()
            print("✅ Bot đã dừng!")
        except Exception as e:
            print(f"❌ Lỗi: {e}")

def main():
    """Main function"""
    try:
        bot = SimpleTelegramBot()
        bot.run()
    except Exception as e:
        print(f"❌ Không thể khởi động bot: {e}")
        print("💡 Hãy kiểm tra TELEGRAM_BOT_TOKEN trong .env")

if __name__ == "__main__":
    main()