#!/usr/bin/env python3
"""
🤖 Telegram Bot Standalone - Chạy bot để nhận lệnh
"""

import asyncio
import sys
import os
from datetime import datetime

# Thêm thư mục gốc vào path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config.config import Config

class SimpleTelegramBot:
    def __init__(self):
        self.config = Config()
        if not self.config.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN không được cấu hình!")
        
        # Tạo application
        self.application = Application.builder().token(self.config.TELEGRAM_BOT_TOKEN).build()
        
        # Đăng ký handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("status", self.status))
        self.application.add_handler(CommandHandler("stats", self.stats))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        print(f"✅ Bot initialized với token: {self.config.TELEGRAM_BOT_TOKEN[:10]}...")
        print(f"✅ Chat ID: {self.config.TELEGRAM_CHAT_ID}")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Xử lý lệnh /start"""
        welcome_text = """
🤖 **Crypto Trading Bot**

Chào mừng! Bot đang hoạt động.

**📱 Commands:**
/status - Trạng thái bot
/stats - Thống kê giao dịch  
/help - Trợ giúp

**🚀 Bot đã sẵn sàng!**
"""
        await update.message.reply_text(welcome_text, parse_mode='Markdown')
        print(f"✅ Đã trả lời /start cho {update.effective_user.first_name}")

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Xử lý lệnh /status"""
        status_text = f"""
📊 **Bot Status**

🕐 Time: {datetime.now().strftime('%H:%M:%S')}
✅ Status: Active
🤖 Mode: Demo/Test

**💰 Portfolio:**
• Balance: $1000.00 (Demo)
• Position: None
• P&L: $0.00
"""
        await update.message.reply_text(status_text, parse_mode='Markdown')
        print(f"✅ Đã trả lời /status cho {update.effective_user.first_name}")

    async def stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Xử lý lệnh /stats"""
        stats_text = """
📈 **Trading Statistics**

**🎯 Performance:**
• Total Trades: 0
• Win Rate: 0%
• Total P&L: $0.00

**📊 Today:**
• Trades: 0
• Profit: $0.00

*Demo mode - No real trades*
"""
        await update.message.reply_text(stats_text, parse_mode='Markdown')
        print(f"✅ Đã trả lời /stats cho {update.effective_user.first_name}")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Xử lý lệnh /help"""
        help_text = """
🆘 **Help - Commands**

**📱 Available Commands:**

/start - Khởi động bot
/status - Xem trạng thái
/stats - Thống kê giao dịch
/help - Hiển thị trợ giúp

**💡 Tips:**
• Bot đang ở chế độ demo
• Không có giao dịch thật
• An toàn 100%

**🔧 Status:** ✅ Online
"""
        await update.message.reply_text(help_text, parse_mode='Markdown')
        print(f"✅ Đã trả lời /help cho {update.effective_user.first_name}")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Xử lý tin nhắn thông thường"""
        message = update.message.text
        response = f"""
👋 Chào {update.effective_user.first_name}!

Bạn vừa gửi: "{message}"

Hãy sử dụng các lệnh:
/start - Bắt đầu
/status - Trạng thái  
/help - Trợ giúp
"""
        await update.message.reply_text(response)
        print(f"✅ Đã trả lời tin nhắn cho {update.effective_user.first_name}: {message}")

    async def run(self):
        """Chạy bot"""
        print("🚀 Starting Telegram bot...")
        print("📱 Bot sẵn sàng nhận lệnh từ Telegram!")
        print("⏹️  Nhấn Ctrl+C để dừng")
        print("-" * 50)
        
        try:
            # Khởi động bot
            await self.application.run_polling()
        except KeyboardInterrupt:
            print("\n⏹️  Bot đã dừng!")
        except Exception as e:
            print(f"❌ Lỗi: {e}")

async def main():
    """Main function"""
    try:
        bot = SimpleTelegramBot()
        await bot.run()
    except Exception as e:
        print(f"❌ Không thể khởi động bot: {e}")

if __name__ == "__main__":
    asyncio.run(main())