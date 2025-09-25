# Crypto Trading Telegram Bot

🤖 **Automated crypto trading bot with Telegram integration and real-time Binance API**

## ✨ Features

### 🎮 Telegram Bot Interface
- **Reply Keyboard** - Nút bấm cố định dưới chat
- **Real-time Commands** - Điều khiển bot qua Telegram
- **Interactive Controls** - Không cần nhớ lệnh

### 💼 Binance Integration  
- **Live Account Info** - Thông tin tài khoản thật
- **Real-time Balance** - Số dư các coin
- **Portfolio Value** - Tổng giá trị theo USDT
- **Price Monitoring** - Giá real-time

### 🎯 Trading Features
- **Multiple Strategies** - MA, RSI, MACD, Combined
- **Demo Mode** - An toàn 100% để test
- **Live Mode** - Giao dịch thật với Binance API
- **Risk Management** - Stop loss & Take profit

### 📊 Monitoring
- **Real-time Status** - Trạng thái bot
- **Trading Statistics** - Thống kê chi tiết  
- **Trade History** - Lịch sử giao dịch
- **Performance Tracking** - Theo dõi hiệu suất

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/nam11993/crypto-trading-telegram-bot.git
cd crypto-trading-telegram-bot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Environment
Copy `.env.example` to `.env` and fill in your API keys:
```env
# Binance API (Get from binance.com → API Management)
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET_KEY=your_binance_secret_key
USE_TESTNET=false

# Telegram Bot (Get from @BotFather)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# Trading Settings
DEFAULT_SYMBOL=BTCUSDT
TRADE_AMOUNT=0.001
STRATEGY=moving_average
```

### 4. Run Bot
```bash
# Simple bot with reply keyboard
python simple_reply_bot.py

# Or run demo mode for testing
python demo.py
```

## 📱 Telegram Commands

### Reply Keyboard Buttons:
- **📊 Status** - Bot status and current position
- **📈 Stats** - Trading statistics and performance  
- **💼 Account** - Binance account information
- **💰 Balance** - Detailed balance for all coins
- **▶️ Start** - Start automated trading
- **⏹️ Stop** - Stop trading safely
- **🟢 BUY** - Execute buy order immediately
- **🔴 SELL** - Execute sell order immediately
- **⚙️ Settings** - Bot configuration
- **🆘 Help** - Help and commands guide

## 🔧 Configuration

### Binance API Setup
1. Go to [binance.com](https://binance.com) → API Management
2. Create new API key with permissions:
   - ✅ Enable Reading
   - ✅ Enable Spot & Margin Trading
   - ❌ Enable Withdrawals (for security)
3. Add IP restrictions (recommended)
4. Copy keys to `.env` file

### Telegram Bot Setup
1. Message @BotFather on Telegram
2. Create new bot with `/newbot`
3. Copy bot token to `.env`
4. Run `python get_chat_id.py` to get your chat ID

### Trading Strategies
- **Moving Average** - MA crossover signals
- **RSI** - Oversold/overbought levels  
- **MACD** - MACD line crossovers
- **Combined** - Multiple indicators

## 🛡️ Security Features

- **Read-Only by Default** - Only account reading enabled
- **Demo Mode** - Test without real money
- **API Key Encryption** - Secure key storage
- **IP Whitelisting** - Restrict API access
- **No Withdrawal Rights** - Cannot withdraw funds

## 📊 Bot Status Examples

```
💼 BINANCE ACCOUNT INFO

💰 LIVE MODE  
📊 Giao dịch: ✅ CÓ THỂ

💰 PORTFOLIO:
Tổng giá trị: $1,234.56 USDT

🪙 TOP BALANCES:
• BTC: 0.001234
• ETH: 0.052100  
• USDT: 500.00

📈 PERMISSIONS:
• Trade: ✅
• Withdraw: ✅  
• Deposit: ✅
```

## 🚧 Development

### Project Structure
```
crypto-trading-bot/
├── config/
│   └── config.py           # Configuration management
├── src/
│   ├── api_client.py       # Binance API client
│   ├── binance_account.py  # Account information
│   ├── strategy.py         # Trading strategies
│   ├── database.py         # SQLite database
│   └── telegram_bot.py     # Telegram integration
├── simple_reply_bot.py     # Main bot with reply keyboard
├── demo.py                 # Demo trading mode
├── main.py                 # Full trading bot
├── requirements.txt        # Python dependencies
└── README.md
```

### Adding New Features
1. Fork the repository
2. Create feature branch
3. Add your changes
4. Submit pull request

## ⚠️ Disclaimer

**This bot is for educational purposes only. Cryptocurrency trading involves significant risk of loss. Never trade with money you cannot afford to lose.**

- Not financial advice
- Past performance ≠ future results  
- Always test in demo mode first
- Use at your own risk

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

1. Fork the project
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📞 Support

- **GitHub Issues** - Bug reports and feature requests
- **Telegram** - @yourusername (for urgent issues)
- **Documentation** - Check wiki for detailed guides

---

⭐ **Star this repo if it helps you!** ⭐