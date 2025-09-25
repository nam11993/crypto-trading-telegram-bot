#!/usr/bin/env python3
"""
📊 Professional Crypto Chart Bot - Binance Style Charts
Features:
- High-quality PNG chart images like Binance
- Multiple timeframes (1m, 5m, 15m, 1h, 4h, 1d)
- Technical indicators (MA, Bollinger Bands, RSI)
- Volume analysis
- Comparison charts
- Real-time OHLCV data
"""
import logging
import asyncio
import time
import requests
import json
import os
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from src.binance_chart import BinanceLikeChart
from src.price_tracker import PriceTracker
from config.config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot configuration
config = Config()
BOT_TOKEN = config.TELEGRAM_BOT_TOKEN

# Global instances
chart_generator = BinanceLikeChart()
price_tracker = PriceTracker()

# Create reply keyboard
keyboard = [
    [KeyboardButton("📊 Market Summary"), KeyboardButton("📈 BTC Chart")],
    [KeyboardButton("🔥 Top Gainers"), KeyboardButton("📉 Top Losers")],
    [KeyboardButton("🎯 ETH Chart"), KeyboardButton("🚀 ADA Chart")],
    [KeyboardButton("💡 Help"), KeyboardButton("📋 All Coins")]
]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

class ProfessionalChartBot:
    """Professional crypto chart bot with Binance-like visualization"""
    
    def __init__(self):
        self.supported_coins = [
            'BTC', 'ETH', 'ADA', 'DOT', 'LINK', 'BNB', 'SOL',
            'MATIC', 'AVAX', 'ATOM', 'XRP', 'LTC', 'UNI', 'SUSHI', 'AAVE'
        ]
        
        self.valid_timeframes = ['1m', '5m', '15m', '1h', '4h', '1d']
        
    async def start_command(self, update: Update, context) -> None:
        """Start command handler"""
        user = update.effective_user
        welcome_message = f"""🚀 PROFESSIONAL CRYPTO CHART BOT

Xin chào {user.first_name}! 👋

📊 FEATURES:
✅ High-quality candlestick charts như Binance
✅ Hỗ trợ {len(self.supported_coins)} cặp coin chính
✅ Multiple timeframes: 1m, 5m, 15m, 1h, 4h, 1d
✅ Technical indicators (MA, Bollinger Bands)
✅ Volume analysis
✅ Comparison charts

💡 CÁCH SỬ DỤNG:
• Nhấn nút để xem chart nhanh
• Gửi tên coin: BTC, ETH, ADA...
• Với timeframe: BTC 4h, ETH 15m, ADA 1d
• So sánh: compare BTC ETH ADA
• Nhiều nến: BTC 1h 500 (tối đa 1000 nến)

🎨 Chart được tạo với chất lượng cao, đẹp như Binance!"""

        await update.message.reply_text(welcome_message, reply_markup=reply_markup)

    async def handle_message(self, update: Update, context) -> None:
        """Handle all text messages"""
        try:
            text = update.message.text.strip()
            user = update.effective_user
            
            logger.info(f"Message from {user.first_name}: {text}")
            
            if text == "📊 Market Summary":
                await self.send_market_summary(update)
                
            elif text in ["📈 BTC Chart", "🎯 ETH Chart", "🚀 ADA Chart"]:
                coin = text.split()[1]  # Extract coin name
                await self.send_chart(update, coin, '1h', 200)
                
            elif text == "🔥 Top Gainers":
                await self.send_top_gainers(update)
                
            elif text == "📉 Top Losers":
                await self.send_top_losers(update)
                
            elif text == "💡 Help":
                await self.send_help(update)
                
            elif text == "📋 All Coins":
                await self.send_supported_coins(update)
                
            else:
                await self.handle_coin_request(update, text)
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await update.message.reply_text(f"❌ Lỗi xử lý: {e}")

    async def send_chart(self, update: Update, coin: str, timeframe: str = '1h', 
                        limit: int = 200, show_indicators: bool = True):
        """Send professional chart image"""
        try:
            # Show typing action
            await update.message.chat.send_action('upload_photo')
            
            # Generate chart
            chart_path = chart_generator.generate_professional_chart(
                coin.upper() + 'USDT', timeframe, limit, show_indicators
            )
            
            if chart_path.startswith('❌'):
                await update.message.reply_text(chart_path)
                return
            
            # Get price data for caption
            price_data = price_tracker.get_price_by_symbol(coin.upper() + 'USDT')
            
            if price_data:
                caption = f"📊 {coin.upper()}/USDT Professional Chart ({timeframe})\n\n"
                caption += f"💰 Price: ${price_data['price']:.4f}\n"
                caption += f"📈 24h: {price_data['change_percent']:+.2f}% {price_data['emoji']}\n"
                caption += f"🔝 High: ${price_data['high_24h']:.4f}\n"
                caption += f"🔻 Low: ${price_data['low_24h']:.4f}\n"
                caption += f"📦 Volume: {price_tracker._format_volume(price_data['volume'])}\n"
                caption += f"🕐 Candles: {limit}\n\n"
                caption += "💡 Try: BTC 4h 500, ETH 15m, compare BTC ETH ADA"
            else:
                caption = f"📊 {coin.upper()}/USDT Professional Chart ({timeframe} • {limit} candles)"
            
            # Send image
            with open(chart_path, 'rb') as photo:
                await update.message.reply_photo(
                    photo=photo, 
                    caption=caption,
                    reply_markup=reply_markup
                )
            
            # Clean up
            try:
                os.remove(chart_path)
                logger.info(f"Cleaned up: {chart_path}")
            except:
                pass
                
        except Exception as e:
            logger.error(f"Error sending chart for {coin}: {e}")
            await update.message.reply_text(f"❌ Lỗi tạo chart cho {coin}: {e}")

    async def send_comparison_chart(self, update: Update, coins: list):
        """Send comparison chart"""
        try:
            await update.message.chat.send_action('upload_photo')
            
            # Generate comparison chart
            chart_path = chart_generator.generate_comparison_chart(
                [coin + 'USDT' for coin in coins], '1h'
            )
            
            if chart_path.startswith('❌'):
                await update.message.reply_text(chart_path)
                return
            
            caption = f"📊 Price Comparison: {' vs '.join(coins)}\n\n"
            caption += "📈 Normalized percentage changes (1h timeframe)\n"
            caption += "🔍 Base: Starting point = 0%\n"
            caption += "💡 Green = better performance, Red = worse\n\n"
            caption += "Try: compare BTC ETH ADA SOL MATIC"
            
            # Send image
            with open(chart_path, 'rb') as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=caption,
                    reply_markup=reply_markup
                )
            
            # Clean up
            try:
                os.remove(chart_path)
            except:
                pass
                
        except Exception as e:
            logger.error(f"Error sending comparison chart: {e}")
            await update.message.reply_text(f"❌ Lỗi tạo comparison chart: {e}")

    async def handle_coin_request(self, update: Update, text: str):
        """Handle coin chart requests"""
        try:
            text = text.upper().strip()
            
            # Handle comparison charts
            if text.startswith('COMPARE'):
                coins = text.replace('COMPARE', '').strip().split()
                valid_coins = [coin for coin in coins if coin in self.supported_coins]
                
                if len(valid_coins) >= 2:
                    await self.send_comparison_chart(update, valid_coins)
                else:
                    await update.message.reply_text(
                        "❌ Cần ít nhất 2 coins hợp lệ để so sánh\n"
                        f"💡 Supported: {', '.join(self.supported_coins)}\n"
                        "🔍 VD: compare BTC ETH ADA"
                    )
                return
            
            # Parse coin, timeframe, and limit
            parts = text.split()
            coin = parts[0] if parts else text
            timeframe = parts[1] if len(parts) > 1 else '1h'
            limit = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 200
            
            # Validate inputs
            if timeframe not in self.valid_timeframes:
                timeframe = '1h'
                
            if limit > 1000:
                limit = 1000
            elif limit < 50:
                limit = 50
                
            if coin in self.supported_coins:
                await self.send_chart(update, coin, timeframe, limit)
            else:
                await update.message.reply_text(
                    f"❌ '{coin}' không được hỗ trợ\n\n"
                    f"🪙 SUPPORTED COINS:\n{', '.join(self.supported_coins)}\n\n"
                    "💡 EXAMPLES:\n"
                    "• BTC (default 1h, 200 candles)\n"
                    "• ETH 4h (4h timeframe)\n"
                    "• ADA 15m 500 (15m, 500 candles)\n"
                    "• compare BTC ETH SOL"
                )
                
        except Exception as e:
            logger.error(f"Error handling coin request '{text}': {e}")
            await update.message.reply_text(f"❌ Lỗi xử lý yêu cầu: {e}")

    async def send_market_summary(self, update: Update):
        """Send market summary"""
        try:
            summary = price_tracker.get_market_summary()
            await update.message.reply_text(summary, reply_markup=reply_markup)
        except Exception as e:
            await update.message.reply_text(f"❌ Lỗi lấy market summary: {e}")

    async def send_top_gainers(self, update: Update):
        """Send top gainers"""
        try:
            gainers = price_tracker.get_top_gainers_losers()
            if gainers:
                message = "🔥 TOP GAINERS (24h)\n\n"
                for i, coin in enumerate(gainers['gainers'][:5], 1):
                    message += f"{i}. {coin['symbol'].replace('USDT', '')}: "
                    message += f"${coin['price']:.4f} (+{coin['change_percent']:.2f}%)\n"
                
                message += "\n💡 Gửi tên coin để xem chart chi tiết!"
                await update.message.reply_text(message, reply_markup=reply_markup)
            else:
                await update.message.reply_text("❌ Không thể lấy dữ liệu top gainers")
        except Exception as e:
            await update.message.reply_text(f"❌ Lỗi: {e}")

    async def send_top_losers(self, update: Update):
        """Send top losers"""
        try:
            losers = price_tracker.get_top_gainers_losers()
            if losers:
                message = "📉 TOP LOSERS (24h)\n\n"
                for i, coin in enumerate(losers['losers'][:5], 1):
                    message += f"{i}. {coin['symbol'].replace('USDT', '')}: "
                    message += f"${coin['price']:.4f} ({coin['change_percent']:.2f}%)\n"
                
                message += "\n💡 Gửi tên coin để xem chart chi tiết!"
                await update.message.reply_text(message, reply_markup=reply_markup)
            else:
                await update.message.reply_text("❌ Không thể lấy dữ liệu top losers")
        except Exception as e:
            await update.message.reply_text(f"❌ Lỗi: {e}")

    async def send_help(self, update: Update):
        """Send help message"""
        help_text = """💡 HƯỚNG DẪN SỬ DỤNG

📊 CHART COMMANDS:
• BTC - Chart BTC với 1h, 200 nến
• ETH 4h - Chart ETH với 4h timeframe  
• ADA 15m 500 - Chart ADA 15m với 500 nến
• compare BTC ETH ADA - So sánh nhiều coins

⏰ TIMEFRAMES:
1m, 5m, 15m, 1h, 4h, 1d

🕯️ CANDLES:
• Minimum: 50 nến
• Maximum: 1000 nến
• Default: 200 nến

🎨 FEATURES:
✅ Candlestick charts như Binance
✅ Technical indicators (MA20, MA50, BB)
✅ Volume analysis với colors
✅ Support/Resistance levels
✅ Professional styling
✅ Real-time OHLCV data

💡 TIPS:
• Nhấn nút để nhanh chóng
• Charts được tạo real-time từ Binance
• Chất lượng HD, đẹp như exchange"""

        await update.message.reply_text(help_text, reply_markup=reply_markup)

    async def send_supported_coins(self, update: Update):
        """Send list of supported coins"""
        message = f"🪙 SUPPORTED COINS ({len(self.supported_coins)} coins)\n\n"
        message += ", ".join(self.supported_coins)
        message += "\n\n💡 Gửi tên coin để xem chart chi tiết!"
        message += "\n🔍 VD: BTC, ETH 4h, ADA 15m 500"
        
        await update.message.reply_text(message, reply_markup=reply_markup)

    def run(self):
        """Run the bot"""
        try:
            print("🚀 Starting Professional Chart Bot...")
            print("📊 Binance-style charts ready!")
            print("🎨 High-quality PNG generation enabled")
            
            # Create application
            app = Application.builder().token(BOT_TOKEN).build()
            
            # Add handlers
            app.add_handler(CommandHandler("start", self.start_command))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
            
            # Start bot
            app.run_polling(drop_pending_updates=True)
            
        except Exception as e:
            logger.error(f"Error running bot: {e}")
            print(f"❌ Lỗi chạy bot: {e}")

if __name__ == "__main__":
    bot = ProfessionalChartBot()
    bot.run()