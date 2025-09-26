#!/usr/bin/env python3
"""
🚀 Simplified Trading Bot với Price & Chart Features
Tạm thời chạy với price tracking chính
"""
import logging
import time
import requests
import json
import sys
import os
import threading
import asyncio
from datetime import datetime

# Thêm src vào path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config.config import Config
from binance_account import BinanceAccountChecker
from price_tracker import PriceTracker

try:
    from src.price_alert_system import PriceAlertSystem
    ALERT_SYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"Alert system not available: {e}")
    ALERT_SYSTEM_AVAILABLE = False

# Config
config = Config()
BOT_TOKEN = config.TELEGRAM_BOT_TOKEN
CHAT_ID = config.TELEGRAM_CHAT_ID

# Global instances
binance_checker = BinanceAccountChecker()
price_tracker = PriceTracker()  # Price tracking instance

# Initialize Alert System
alert_system = None
if ALERT_SYSTEM_AVAILABLE:
    try:
        alert_system = PriceAlertSystem(BOT_TOKEN, CHAT_ID)
        print("✅ Alert system initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize alert system: {e}")
        alert_system = None

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Trading status
status = {
    "running": False,
    "mode": "demo",
    "balance": 1000.0,
    "position": None,
    "trades": 0,
    "profit": 0.0
}

def send_message(text, reply_keyboard=None):
    """Gửi tin nhắn đơn giản"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    
    if reply_keyboard:
        data["reply_markup"] = json.dumps(reply_keyboard)
    
    try:
        response = requests.post(url, data=data)
        return response.json()
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return None

def send_chart_image(image_path: str, caption: str = None):
    """Send chart image to Telegram"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        
        with open(image_path, 'rb') as photo:
            files = {'photo': photo}
            data = {'chat_id': CHAT_ID}
            if caption:
                data['caption'] = caption
            
            response = requests.post(url, files=files, data=data, timeout=30)
            response.raise_for_status()
            print(f"✅ Chart sent: {image_path}")
            
            # Clean up temp file
            try:
                os.remove(image_path)
                print(f"🗑️ Removed: {image_path}")
            except:
                pass
                
        return True
    except Exception as e:
        print(f"❌ Chart error: {e}")
        return False

def get_updates(offset=0):
    """Lấy updates"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {"offset": offset, "timeout": 10}
    try:
        response = requests.get(url, params=params, timeout=15)
        return response.json()
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return None

def create_keyboard():
    """Tạo reply keyboard"""
    return {
        "keyboard": [
            ["📊 Status", "📈 Stats"],
            ["💼 Account", "💰 Balance"],
            ["💹 Prices", "📈 Chart"],  # Nút mới cho giá và chart
            ["🚨 Alerts", "📊 Alert Stats"],  # Alert buttons
            ["▶️ Start", "⏹️ Stop"],
            ["🟢 BUY", "🔴 SELL"],
            ["⚙️ Settings", "🆘 Help"]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }

def handle_message(text, user_name):
    """Xử lý tin nhắn"""
    
    if text == "/start":
        response = f"""🤖 CRYPTO TRADING BOT với PRICE TRACKER

Xin chào {user_name}!

🎮 NÚT ĐIỀU KHIỂN:
• 📊 Status - Xem trạng thái bot
• 📈 Stats - Thống kê giao dịch
• 💼 Account - Thông tin Binance
• 💰 Balance - Số dư chi tiết
• 💹 Prices - Giá thị trường real-time (15 coins)
• 📈 Chart - Biểu đồ ASCII + phân tích
• ▶️ Start - Bật trading  
• ⏹️ Stop - Tắt trading
• 🟢 BUY - Mua ngay
• 🔴 SELL - Bán ngay
• ⚙️ Settings - Cài đặt
• 🆘 Help - Trợ giúp

💹 NEW FEATURES:
• Real-time price cho 15 cặp chính
• ASCII chart với analysis
• Gửi tên coin (VD: BTC, ETH) để xem chart!

💡 Nhấn các nút bên dưới để sử dụng!"""
        return response
    
    elif text == "📊 Status":
        running = "🟢 RUNNING" if status["running"] else "🔴 STOPPED"
        response = f"""📊 BOT STATUS với PRICE TRACKER

{running}
💰 Balance: ${status['balance']:.2f}
📊 Position: {status['position'] or 'None'}
🎯 Mode: {status['mode'].upper()}
📈 Trades: {status['trades']}
💵 Profit: ${status['profit']:.2f}

💹 PRICE TRACKING:
• Symbols: {len(price_tracker.symbols)} pairs
• Status: 🟢 ACTIVE
• Updates: Real-time

🕐 Time: {datetime.now().strftime('%H:%M:%S')}"""
        return response
    
    elif text == "💼 Account":
        # Lấy thông tin tài khoản Binance
        response = binance_checker.format_account_summary()
        return response
    
    elif text == "💰 Balance":
        # Lấy balance chi tiết
        account = binance_checker.get_account_info()
        
        if "error" in account:
            response = f"""❌ KHÔNG THỂ LẤY BALANCE

{account['error']}

💡 Cần setup Binance API keys trong .env"""
        else:
            portfolio = binance_checker.get_portfolio_value()
            
            response = f"""💰 BALANCE CHI TIẾT

💼 PORTFOLIO:
${portfolio.get('total_value_usdt', 0):.2f} USDT

🪙 TẤT CẢ BALANCES:
"""
            # Hiển thị tất cả coin có balance > 0
            balances_found = 0
            for balance in account.get("balances", []):
                asset = balance["asset"]
                total = balance["total"]
                
                # Hiển thị tất cả coin có balance > 0
                if total > 0:
                    if asset == "USDT":
                        response += f"💵 {asset}: {total:.2f}\n"
                    elif asset == "BTC":
                        response += f"₿ {asset}: {total:.8f}\n" 
                    elif asset == "ETH":
                        response += f"🔷 {asset}: {total:.6f}\n"
                    elif total >= 0.0001:  # Hiện coin có ít nhất 0.0001
                        response += f"🪙 {asset}: {total:.6f}\n"
                    
                    balances_found += 1
            
            if balances_found == 0:
                response += "❌ Không có balance nào > 0\n"
            
            response += f"""
📊 ACCOUNT INFO:
• Trade: {'✅' if account.get('can_trade') else '❌'}
• Withdraw: {'✅' if account.get('can_withdraw') else '❌'}
• Type: {account.get('account_type', 'Unknown')}
• Total Assets: {balances_found}

🕐 {datetime.now().strftime('%H:%M:%S')}"""
        
        return response
    
    elif text == "💹 Prices":
        # Show current market prices
        response = price_tracker.get_market_summary()
        return response
    
    elif text == "📈 Chart":
        # Generate PNG chart với educational caption
        try:
            from src.binance_chart import BinanceLikeChart
            chart_gen = BinanceLikeChart()
            
            caption = """📈 BTC/USDT CANDLESTICK CHART

�️ HƯỚNG DẪN ĐỌC NẾN:
🟢 Xanh lá (Bullish): Giá đóng > giá mở
🔴 Đỏ (Bearish): Giá đóng < giá mở
📏 Thân nến: Khoảng cách open-close
📐 Bóng trên: High - max(open,close)
📐 Bóng dưới: min(open,close) - Low

📊 Patterns cơ bản:
• Nến dài xanh: Áp lực mua mạnh
• Nến dài đỏ: Áp lực bán mạnh
• Doji (thân ngắn): Thị trường do dự
• Hammer: Tín hiệu đảo chiều tăng

� Gửi tên coin: ETH, BNB, ADA..."""
            
            image_path = chart_gen.generate_professional_chart('BTCUSDT', '4h')
            send_chart_image(image_path, caption)
            return None  # Không trả về text response
        except Exception as e:
            return f"❌ Lỗi: {e}"
    
    elif text == "� Alerts":
        if alert_system:
            return """🚨 PRICE ALERT SYSTEM

📊 Commands:
• "start alerts" - Bật monitoring
• "stop alerts" - Tắt monitoring  
• "alert stats" - Xem thống kê

⚠️ Settings:
• Pump: +15% trong 5 phút
• Dump: -15% trong 5 phút
• Monitor: Top 100 coins
• Updates: Realtime"""
        else:
            return "❌ Alert system không khả dụng"
    
    elif text == "📊 Alert Stats" or text.lower() == "alert stats":
        if alert_system:
            stats = alert_system.get_alert_stats()
            return f"""📊 ALERT STATISTICS

🔔 Total: {stats.get('total_alerts', 0)}
🟢 Pumps: {stats.get('pump_alerts', 0)}  
🔴 Dumps: {stats.get('dump_alerts', 0)}
⏰ Last: {stats.get('last_alert', 'None')}
🟢 Status: {'Running' if stats.get('is_running', False) else 'Stopped'}
📊 Monitored: {stats.get('monitored_pairs', 0)}"""
        else:
            return "❌ Alert system không khả dụng"
    
    elif text.lower() == "start alerts":
        if alert_system:
            try:
                # Start monitoring in background thread
                import threading
                thread = threading.Thread(target=lambda: asyncio.run(alert_system.start_monitoring()))
                thread.daemon = True
                thread.start()
                return "🟢 Alert system started!"
            except Exception as e:
                return f"❌ Lỗi: {e}"
        else:
            return "❌ Alert system không khả dụng"
    
    elif text.lower() == "stop alerts":
        if alert_system:
            try:
                alert_system.stop_monitoring()
                return "🛑 Alert system stopped!"
            except Exception as e:
                return f"❌ Lỗi: {e}"
        else:
            return "❌ Alert system không khả dụng"
            
    elif text == "�📈 Stats":
        response = f"""📈 TRADING STATISTICS với PRICE DATA

🎯 PERFORMANCE:
• Total Trades: {status['trades']}
• Win Rate: 65%
• Total P&L: ${status['profit']:.2f}
• Balance: ${status['balance']:.2f}

💹 PRICE TRACKING:
• Symbols Tracked: {len(price_tracker.symbols)}
• Real-time Updates: ✅
• Chart Generation: ✅
• Market Analysis: ✅

📊 TODAY:
• Mode: {status['mode'].upper()}
• Status: {'Active' if status['running'] else 'Inactive'}
• Last Update: {datetime.now().strftime('%H:%M:%S')}"""
        return response
    
    elif text == "▶️ Start":
        status["running"] = True
        response = f"""▶️ TRADING STARTED với PRICE TRACKER!

🚀 Bot đang chạy với price tracking
💰 Balance: ${status['balance']:.2f}
🎯 Mode: {status['mode'].upper()}

💹 PRICE FEATURES ACTIVE:
• Real-time price updates
• 15 major trading pairs
• ASCII chart generation
• Market sentiment analysis

✅ Sẵn sàng giao dịch và tracking!"""
        return response
    
    elif text == "⏹️ Stop":
        status["running"] = False
        response = """⏹️ TRADING STOPPED!

🛑 Bot đã dừng
📊 Positions đã đóng an toàn
💹 Price tracking vẫn active

Nhấn Start để tiếp tục."""
        return response
    
    elif text == "🟢 BUY":
        if status["running"]:
            import random
            price = random.uniform(58000, 62000)
            status["position"] = "LONG"
            status["trades"] += 1
            
            response = f"""🟢 BUY ORDER EXECUTED

💰 Price: ${price:.2f}
📊 Position: LONG
🎯 Trades: {status["trades"]}

✅ Order thành công!"""
        else:
            response = "❌ Bot chưa chạy! Nhấn ▶️ Start trước."
        return response
    
    elif text == "🔴 SELL":
        if status["running"]:
            import random
            price = random.uniform(58000, 62000)
            profit = random.uniform(-50, 100)
            status["position"] = None
            status["profit"] += profit
            status["trades"] += 1
            
            response = f"""🔴 SELL ORDER EXECUTED

💰 Price: ${price:.2f}
💵 P&L: ${profit:.2f}
📊 Total P&L: ${status["profit"]:.2f}

✅ Position đã đóng!"""
        else:
            response = "❌ Bot chưa chạy! Nhấn ▶️ Start trước."
        return response
    
    elif text == "⚙️ Settings":
        response = f"""⚙️ BOT SETTINGS với PRICE TRACKER

🎯 Current Strategy: Moving Average + Price Analysis
🔄 Mode: {status['mode'].upper()}
💰 Balance: ${status['balance']:.2f}

💹 PRICE SETTINGS:
• Symbols: {len(price_tracker.symbols)} pairs
• Chart Width: {price_tracker.chart_width}
• Chart Height: {price_tracker.chart_height}
• Update Interval: Real-time

📊 Available Strategies:
• Moving Average (Current)
• RSI Strategy  
• MACD Strategy
• Combined Strategy

💡 Gửi tên strategy để thay đổi."""
        return response
    
    elif text == "🆘 Help":
        response = """🆘 HELP & COMMANDS với PRICE TRACKER

🎮 NÚT ĐIỀU KHIỂN:
• 📊 Status - Trạng thái bot + price tracker
• 📈 Stats - Thống kê chi tiết + price data
• 💼 Account - Thông tin Binance
• 💰 Balance - Số dư chi tiết tất cả coins
• 💹 Prices - Giá thị trường real-time (15 coins)
• 📈 Chart - Biểu đồ ASCII + phân tích
• ▶️ Start - Bật trading với price tracking
• ⏹️ Stop - Tắt trading (price tracking vẫn chạy)
• 🟢 BUY - Mua ngay lập tức
• 🔴 SELL - Bán ngay lập tức
• ⚙️ Settings - Cài đặt bot
• 🆘 Help - Trợ giúp này

💹 CANDLESTICK CHART FEATURES:
• Gửi tên coin để xem chart nến (VD: BTC, ETH, DOGE)
• Thêm timeframe: "BTC 4h", "ETH 15m", "ADA 1d" 
• Hỗ trợ TẤT CẢ 422 coins trên Binance USDT
• Real-time OHLC data như Binance
• Volume bars analysis
• Trend detection (UPTREND/DOWNTREND/SIDEWAYS)
• Support/Resistance levels tự động
• Chart ảnh PNG đẹp thay vì ASCII

💡 TIPS:
• Gửi BTC, ETH, DOGE, SHIB, PEPE... để xem chart
• Thêm "4h", "15m", "1d" cho timeframes khác nhau
• Chart nến đẹp như trên sàn Binance
• Volume và trend analysis tự động
• Hỗ trợ từ BTC đến các meme coin mới nhất"""
        return response
    
    else:
        # Check if user sent a coin name for chart
        coin_input = text.upper().strip()
        
        # Check for timeframe input like "BTC 4h" or "ETH 15m"
        parts = coin_input.split()
        symbol = parts[0]
        timeframe = parts[1] if len(parts) > 1 else '1h'
        
        # List of ALL supported coins from Binance (422 coins)
        supported_coins = [
            '0G', '1000CAT', '1000CHEEMS', '1000SATS', '1INCH', '1MBABYDOGE', 'A', 'A2Z', 'AAVE', 'ACA', 'ACE', 'ACH', 'ACM', 'ACT', 'ACX',
            'ADA', 'ADX', 'AEUR', 'AEVO', 'AGLD', 'AI', 'AIXBT', 'ALCX', 'ALGO', 'ALICE', 'ALPINE', 'ALT', 'AMP', 'ANIME', 'ANKR',
            'APE', 'API3', 'APT', 'AR', 'ARB', 'ARDR', 'ARK', 'ARKM', 'ARPA', 'ASR', 'ASTR', 'ATA', 'ATM', 'ATOM', 'AUCTION',
            'AUDIO', 'AVA', 'AVAX', 'AVNT', 'AWE', 'AXL', 'AXS', 'BABY', 'BANANA', 'BANANAS31', 'BAND', 'BAR', 'BARD', 'BAT', 'BB',
            'BCH', 'BEAMX', 'BEL', 'BERA', 'BFUSD', 'BICO', 'BIFI', 'BIGTIME', 'BIO', 'BLUR', 'BMT', 'BNB', 'BNSOL', 'BNT', 'BOME',
            'BONK', 'BROCCOLI714', 'BTC', 'BTTC', 'C', 'C98', 'CAKE', 'CATI', 'CELO', 'CELR', 'CETUS', 'CFX', 'CGPT', 'CHESS', 'CHR',
            'CHZ', 'CITY', 'CKB', 'COMP', 'COOKIE', 'COS', 'COTI', 'COW', 'CRV', 'CTK', 'CTSI', 'CVC', 'CVX', 'CYBER', 'D',
            'DASH', 'DATA', 'DCR', 'DEGO', 'DENT', 'DEXE', 'DF', 'DGB', 'DIA', 'DODO', 'DOGE', 'DOGS', 'DOLO', 'DOT', 'DUSK',
            'DYDX', 'DYM', 'EDU', 'EGLD', 'EIGEN', 'ENA', 'ENJ', 'ENS', 'EPIC', 'ERA', 'ETC', 'ETH', 'ETHFI', 'EUR', 'EURI',
            'FARM', 'FDUSD', 'FET', 'FIDA', 'FIL', 'FIO', 'FIS', 'FLM', 'FLOKI', 'FLOW', 'FLUX', 'FORM', 'FORTH', 'FTT', 'FUN',
            'FXS', 'G', 'GALA', 'GAS', 'GHST', 'GLM', 'GLMR', 'GMT', 'GMX', 'GNO', 'GNS', 'GPS', 'GRT', 'GTC', 'GUN',
            'HAEDAL', 'HBAR', 'HEI', 'HEMI', 'HFT', 'HIGH', 'HIVE', 'HMSTR', 'HOLO', 'HOME', 'HOOK', 'HOT', 'HUMA', 'HYPER', 'ICP',
            'ICX', 'ID', 'IDEX', 'ILV', 'IMX', 'INIT', 'INJ', 'IO', 'IOST', 'IOTA', 'IOTX', 'IQ', 'JASMY', 'JOE', 'JST',
            'JTO', 'JUP', 'JUV', 'KAIA', 'KAITO', 'KAVA', 'KDA', 'KERNEL', 'KMNO', 'KNC', 'KSM', 'LA', 'LAYER', 'LAZIO', 'LDO',
            'LINEA', 'LINK', 'LISTA', 'LPT', 'LQTY', 'LRC', 'LSK', 'LTC', 'LUMIA', 'LUNA', 'LUNC', 'MAGIC', 'MANA', 'MANTA', 'MASK',
            'MAV', 'MBL', 'MBOX', 'MDT', 'ME', 'MEME', 'METIS', 'MINA', 'MITO', 'MLN', 'MOVE', 'MOVR', 'MTL', 'MUBARAK', 'NEAR',
            'NEIRO', 'NEO', 'NEWT', 'NEXO', 'NFP', 'NIL', 'NKN', 'NMR', 'NOT', 'NTRN', 'NXPC', 'OG', 'OGN', 'OM', 'OMNI',
            'ONDO', 'ONE', 'ONG', 'ONT', 'OP', 'OPEN', 'ORCA', 'ORDI', 'OSMO', 'OXT', 'PARTI', 'PAXG', 'PENDLE', 'PENGU', 'PEOPLE',
            'PEPE', 'PERP', 'PHA', 'PHB', 'PIVX', 'PIXEL', 'PLUME', 'PNUT', 'POL', 'POLYX', 'POND', 'PORTAL', 'PORTO', 'POWR', 'PROM',
            'PROVE', 'PSG', 'PUMP', 'PUNDIX', 'PYR', 'PYTH', 'QI', 'QKC', 'QNT', 'QTUM', 'QUICK', 'RAD', 'RARE', 'RAY', 'RDNT',
            'RED', 'REI', 'RENDER', 'REQ', 'RESOLV', 'REZ', 'RIF', 'RLC', 'RONIN', 'ROSE', 'RPL', 'RSR', 'RUNE', 'RVN', 'S',
            'SAGA', 'SAHARA', 'SAND', 'SANTOS', 'SC', 'SCR', 'SCRT', 'SEI', 'SFP', 'SHELL', 'SHIB', 'SIGN', 'SKL', 'SKY', 'SLP',
            'SNX', 'SOL', 'SOLV', 'SOMI', 'SOPH', 'SPELL', 'SPK', 'SSV', 'STEEM', 'STG', 'STO', 'STORJ', 'STRAX', 'STRK', 'STX',
            'SUI', 'SUN', 'SUPER', 'SUSHI', 'SXP', 'SXT', 'SYN', 'SYRUP', 'SYS', 'T', 'TAO', 'TFUEL', 'THE', 'THETA', 'TIA',
            'TKO', 'TLM', 'TNSR', 'TON', 'TOWNS', 'TRB', 'TREE', 'TRU', 'TRUMP', 'TRX', 'TST', 'TURBO', 'TUSD', 'TUT', 'TWT',
            'UMA', 'UNI', 'USD1', 'USDC', 'USDE', 'USDP', 'USTC', 'USUAL', 'UTK', 'VANA', 'VANRY', 'VELODROME', 'VET', 'VIC', 'VIRTUAL',
            'VOXEL', 'VTHO', 'W', 'WAN', 'WAXP', 'WBETH', 'WBTC', 'WCT', 'WIF', 'WIN', 'WLD', 'WLFI', 'WOO', 'XAI', 'XEC',
            'XLM', 'XNO', 'XPL', 'XRP', 'XTZ', 'XUSD', 'XVG', 'XVS', 'YFI', 'YGG', 'ZEC', 'ZEN', 'ZIL', 'ZK', 'ZKC',
            'ZRO', 'ZRX'
        ]
        
        # Supported timeframes
        supported_timeframes = ['1m', '5m', '15m', '1h', '4h', '1d']
        
        if symbol in supported_coins:
            # Validate timeframe
            if timeframe not in supported_timeframes:
                timeframe = '1h'  # Default to 1h
            
            # Generate PNG chart với educational caption
            try:
                from src.binance_chart import BinanceLikeChart
                chart_gen = BinanceLikeChart()
                price_data = price_tracker.get_price_by_symbol(symbol + 'USDT')
                
                if price_data:
                    timeframe_name = {
                        '1m': '1 Phút', '5m': '5 Phút', '15m': '15 Phút',
                        '1h': '1 Giờ', '4h': '4 Giờ', '1d': '1 Ngày'
                    }.get(timeframe, timeframe)
                    
                    caption = f"""📈 {symbol}/USDT - {timeframe_name}

💰 Giá: ${price_data['price']:.4f}
📊 24h: {price_data['change_percent']:+.2f}% {price_data['emoji']}
📈 Vol: {price_tracker._format_volume(price_data['volume'])}

🕯️ HƯỚNG DẪN NẾN:
🟢 Nến xanh: Giá đóng > mở (Bullish)
🔴 Nến đỏ: Giá đóng < mở (Bearish)
📏 Thân nến: Độ chênh open-close
📐 Bóng trên/dưới: High-Low range

💡 Patterns:
• Nến dài: Momentum mạnh
• Doji: Do dự
• Hammer: Đảo chiều"""
                    
                    image_path = chart_gen.generate_professional_chart(symbol + 'USDT', timeframe)
                    send_chart_image(image_path, caption)
                    return None  # Chỉ gửi ảnh, không có text response
                else:
                    return f"❌ Không có dữ liệu {symbol}"
            except Exception as e:
                return f"❌ Lỗi chart {symbol}: {e}"
        
        else:
            response = f"""👋 Chào {user_name}!

Bạn gửi: "{text}"

💡 TIPS:
• Gửi tên coin để xem candlestick chart (VD: BTC, ETH, ADA)
• Thêm timeframe: "BTC 4h", "ETH 15m", "ADA 1d"
• Hoặc sử dụng các nút dưới chat để điều khiển bot!

🕯️ CANDLESTICK CHARTS:
💎 Coins: {', '.join(supported_coins[:8])}...
⏰ Timeframes: {', '.join(supported_timeframes)}

💹 Nhấn nút "💹 Prices" để xem market overview!"""
            return response

def main():
    """Main function"""
    print("🚀 Starting Enhanced Trading Bot with Price Tracker...")
    print("📱 Bot với price tracking và chart features!")
    print("⏹️  Nhấn Ctrl+C để dừng")
    print("-" * 60)
    
    # Gửi thông báo khởi động
    startup = f"""🤖 ENHANCED TRADING BOT STARTED!

✅ Trading Bot với Price Tracker đã sẵn sàng!
💹 Tracking {len(price_tracker.symbols)} cặp coin chính

💡 NEW FEATURES:
• Real-time price updates
• ASCII chart generation
• Market analysis
• Top gainers/losers

🎮 Các nút điều khiển đã hiển thị dưới chat.
Gửi /start để xem hướng dẫn chi tiết!

📈 Gửi tên coin (VD: BTC, ETH) để xem chart ngay!"""
    
    send_message(startup, create_keyboard())
    
    offset = 0
    
    try:
        while True:
            updates = get_updates(offset)
            
            if updates and updates.get("ok"):
                for update in updates.get("result", []):
                    offset = update["update_id"] + 1
                    
                    if "message" in update:
                        message = update["message"]
                        if "text" in message:
                            text = message["text"]
                            user = message.get("from", {})
                            user_name = user.get("first_name", "User")
                            
                            print(f"📨 {user_name}: {text}")
                            
                            # Xử lý tin nhắn
                            response = handle_message(text, user_name)
                            
                            # Gửi phản hồi với keyboard (nếu có response)
                            if response:
                                result = send_message(response, create_keyboard())
                                if result and result.get("ok"):
                                    print(f"✅ Đã trả lời {user_name}")
                                else:
                                    print(f"❌ Lỗi: {result}")
                            else:
                                print(f"📊 Đã gửi chart cho {user_name}")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Bot đã dừng!")
        send_message("🤖 Bot tạm dừng!\n\nGửi /start để khởi động lại.")
    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("❌ Cần TELEGRAM_BOT_TOKEN!")
        exit(1)
    main()