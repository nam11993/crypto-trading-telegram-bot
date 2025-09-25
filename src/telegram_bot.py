import logging
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
import threading

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from telegram.error import TelegramError

from config.config import Config

class TelegramNotifier:
    """
    Telegram Bot for sending notifications and receiving commands
    """
    
    def __init__(self, trading_bot=None):
        self.bot_token = Config.TELEGRAM_BOT_TOKEN
        self.chat_id = Config.TELEGRAM_CHAT_ID
        self.trading_bot = trading_bot
        self.application = None
        self.logger = logging.getLogger(__name__)
        
        # Bot status
        self.is_running = False
        self.bot_thread = None
        
        if not self.bot_token or not self.chat_id:
            self.logger.warning("Telegram bot token or chat ID not configured")
            return
        
        # Initialize bot
        self.application = Application.builder().token(self.bot_token).build()
        self._setup_handlers()
        
        self.logger.info("Telegram bot initialized")
    
    def _setup_handlers(self):
        """Setup command and callback handlers"""
        if not self.application:
            return
        
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("balance", self.balance_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("stop", self.stop_trading_command))
        self.application.add_handler(CommandHandler("resume", self.resume_trading_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        # Callback handlers for inline keyboard
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Message handler for text messages
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        keyboard = [
            [
                InlineKeyboardButton("📊 Status", callback_data='status'),
                InlineKeyboardButton("💰 Balance", callback_data='balance')
            ],
            [
                InlineKeyboardButton("📈 Statistics", callback_data='stats'),
                InlineKeyboardButton("❓ Help", callback_data='help')
            ],
            [
                InlineKeyboardButton("⏸️ Stop Trading", callback_data='stop'),
                InlineKeyboardButton("▶️ Resume Trading", callback_data='resume')
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_message = """
🤖 **Crypto Trading Bot**

Chào mừng bạn đến với Trading Bot Dashboard!

**Các lệnh có sẵn:**
• `/status` - Xem trạng thái bot
• `/balance` - Xem số dư tài khoản  
• `/stats` - Thống kê trading
• `/stop` - Tạm dừng trading
• `/resume` - Tiếp tục trading
• `/help` - Xem hướng dẫn

Sử dụng keyboard bên dưới để tương tác nhanh! 👇
        """
        
        await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        if not self.trading_bot:
            await update.message.reply_text("❌ Trading bot chưa được khởi tạo")
            return
        
        try:
            # Get current status
            current_price = self.trading_bot.price_history[-1] if self.trading_bot.price_history else 0
            position = self.trading_bot.strategy.position or "None"
            entry_price = self.trading_bot.strategy.entry_price
            
            # Calculate unrealized P&L
            unrealized_pnl = 0
            if entry_price > 0 and current_price > 0:
                unrealized_pnl = ((current_price - entry_price) / entry_price) * 100
            
            status_message = f"""
📊 **Bot Status - {datetime.now().strftime('%H:%M:%S')}**

🔸 **Symbol:** {self.trading_bot.symbol}
🔸 **Current Price:** ${current_price:,.2f}
🔸 **Position:** {position}
🔸 **Strategy:** {Config.STRATEGY}
🔸 **Bot Status:** {'🟢 Active' if self.trading_bot.is_running else '🔴 Stopped'}

{f'🔸 **Entry Price:** ${entry_price:,.2f}' if entry_price > 0 else ''}
{f'🔸 **Unrealized P&L:** {unrealized_pnl:+.2f}%' if unrealized_pnl != 0 else ''}
            """
            
            await update.message.reply_text(status_message, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Lỗi khi lấy status: {str(e)}")
    
    async def balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /balance command"""
        balance_message = """
💰 **Account Balance**

🔸 **USDT Balance:** $1,000.00
🔸 **BTC Balance:** 0.001 BTC
🔸 **Total Value:** $1,045.50

⚠️ *Note: Real balance requires API connection*
        """
        await update.message.reply_text(balance_message, parse_mode='Markdown')
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        if not self.trading_bot:
            await update.message.reply_text("❌ Trading bot chưa được khởi tạo")
            return
        
        try:
            stats = self.trading_bot.database.get_trading_statistics()
            
            stats_message = f"""
📈 **Trading Statistics**

🔸 **Total Trades:** {stats.get('total_trades', 0)}
🔸 **Profitable Trades:** {stats.get('profitable_trades', 0)}
🔸 **Win Rate:** {stats.get('win_rate', 0):.1f}%
🔸 **Total P&L:** ${stats.get('total_pnl', 0):,.2f}
🔸 **Best Trade:** {stats.get('best_trade_percent', 0):+.2f}%
🔸 **Worst Trade:** {stats.get('worst_trade_percent', 0):+.2f}%
            """
            
            await update.message.reply_text(stats_message, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Lỗi khi lấy thống kê: {str(e)}")
    
    async def stop_trading_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stop command"""
        if self.trading_bot:
            self.trading_bot.is_running = False
            await update.message.reply_text("⏸️ **Trading đã được tạm dừng**")
        else:
            await update.message.reply_text("❌ Trading bot chưa được khởi tạo")
    
    async def resume_trading_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /resume command"""
        if self.trading_bot:
            self.trading_bot.is_running = True
            await update.message.reply_text("▶️ **Trading đã được tiếp tục**")
        else:
            await update.message.reply_text("❌ Trading bot chưa được khởi tạo")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """
❓ **Bot Commands Help**

**📊 Trading Commands:**
• `/status` - Xem trạng thái hiện tại
• `/balance` - Xem số dư tài khoản
• `/stats` - Thống kê trading chi tiết

**⚙️ Control Commands:**
• `/stop` - Tạm dừng trading (emergency)
• `/resume` - Tiếp tục trading

**🛠️ Utility Commands:**
• `/start` - Hiển thị menu chính
• `/help` - Hiển thị hướng dẫn này

**📱 Quick Actions:**
Sử dụng inline keyboard để tương tác nhanh!

**⚠️ Lưu ý quan trọng:**
- Bot chỉ thông báo, không thay đổi cài đặt trading
- Để thay đổi strategy/config, cần sửa file .env
- Always monitor your bot!
        """
        
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard callbacks"""
        query = update.callback_query
        await query.answer()
        
        # Route to appropriate handler
        if query.data == 'status':
            await self.status_command(query, context)
        elif query.data == 'balance':
            await self.balance_command(query, context)
        elif query.data == 'stats':
            await self.stats_command(query, context)
        elif query.data == 'stop':
            await self.stop_trading_command(query, context)
        elif query.data == 'resume':
            await self.resume_trading_command(query, context)
        elif query.data == 'help':
            await self.help_command(query, context)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        message = update.message.text.lower()
        
        if 'status' in message or 'trạng thái' in message:
            await self.status_command(update, context)
        elif 'balance' in message or 'số dư' in message:
            await self.balance_command(update, context)
        elif 'stats' in message or 'thống kê' in message:
            await self.stats_command(update, context)
        elif 'help' in message or 'giúp' in message:
            await self.help_command(update, context)
        else:
            await update.message.reply_text(
                "🤖 Tôi không hiểu lệnh này. Gửi `/help` để xem danh sách lệnh có sẵn!"
            )
    
    async def send_notification(self, message: str, parse_mode: str = 'Markdown'):
        """Send notification to Telegram"""
        if not self.application or not self.chat_id:
            self.logger.warning("Telegram not configured, skipping notification")
            return
        
        try:
            await self.application.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode
            )
            self.logger.debug("Telegram notification sent successfully")
            
        except TelegramError as e:
            self.logger.error(f"Failed to send Telegram notification: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error sending notification: {e}")
    
    def send_notification_sync(self, message: str):
        """Send notification synchronously (for use in non-async contexts)"""
        if not self.application or not self.chat_id:
            return
        
        try:
            # Create new event loop for this thread if needed
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Send notification
            loop.run_until_complete(self.send_notification(message))
            
        except Exception as e:
            self.logger.error(f"Error in sync notification: {e}")
    
    def start_bot(self):
        """Start the Telegram bot in a separate thread"""
        if not self.application:
            self.logger.warning("Telegram bot not configured")
            return
        
        def run_bot():
            try:
                self.logger.info("Starting Telegram bot...")
                self.application.run_polling()
            except Exception as e:
                self.logger.error(f"Telegram bot error: {e}")
        
        self.bot_thread = threading.Thread(target=run_bot, daemon=True)
        self.bot_thread.start()
        self.is_running = True
        
        # Send startup notification
        self.send_notification_sync("""
🤖 **Trading Bot Started!**

Bot đã khởi động thành công và sẵn sàng hoạt động.

Gửi `/help` để xem danh sách lệnh có sẵn!
        """)
    
    def stop_bot(self):
        """Stop the Telegram bot"""
        if self.application and self.is_running:
            self.application.stop()
            self.is_running = False
            self.logger.info("Telegram bot stopped")
    
    def notify_trade(self, action: str, symbol: str, amount: float, price: float, profit_loss: float = None):
        """Send trading notification"""
        if action.upper() == 'BUY':
            emoji = "🔵"
            message = f"""
{emoji} **BUY ORDER EXECUTED**

🔸 **Symbol:** {symbol}
🔸 **Amount:** {amount} {symbol.replace('USDT', '')}
🔸 **Price:** ${price:,.2f}
🔸 **Time:** {datetime.now().strftime('%H:%M:%S')}

📈 Position opened successfully!
            """
        else:  # SELL
            emoji = "🔴"
            profit_emoji = "💰" if profit_loss and profit_loss > 0 else "📉"
            message = f"""
{emoji} **SELL ORDER EXECUTED**

🔸 **Symbol:** {symbol}
🔸 **Amount:** {amount} {symbol.replace('USDT', '')}
🔸 **Price:** ${price:,.2f}
🔸 **Time:** {datetime.now().strftime('%H:%M:%S')}

{profit_emoji} **P&L:** {profit_loss:+.2f}% {f'(${profit_loss * amount * price / 100:+,.2f})' if profit_loss else ''}
            """
        
        self.send_notification_sync(message)
    
    def notify_signal(self, signal: str, symbol: str, price: float, strategy: str):
        """Send trading signal notification"""
        emoji = "🔵" if signal == 'BUY' else "🔴" if signal == 'SELL' else "⏸️"
        
        message = f"""
{emoji} **TRADING SIGNAL**

🔸 **Signal:** {signal}
🔸 **Symbol:** {symbol}  
🔸 **Price:** ${price:,.2f}
🔸 **Strategy:** {strategy}
🔸 **Time:** {datetime.now().strftime('%H:%M:%S')}
        """
        
        self.send_notification_sync(message)
    
    def notify_error(self, error_message: str):
        """Send error notification"""
        message = f"""
❌ **ERROR ALERT**

🔸 **Error:** {error_message}
🔸 **Time:** {datetime.now().strftime('%H:%M:%S')}

Please check the bot logs for more details.
        """
        
        self.send_notification_sync(message)