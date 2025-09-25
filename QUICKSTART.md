# 🚀 HƯỚNG DẪN SỬ DỤNG NHANH

## 📋 Yêu cầu hệ thống
- Python 3.8+
- Kết nối Internet
- Windows/Linux/Mac

## ⚡ Cài đặt nhanh

### Bước 1: Cài đặt dependencies
```bash
pip install python-binance requests pandas numpy python-dotenv schedule colorlog
```

### Bước 2: Chạy Demo (không cần API)
```bash
python demo.py
```

### Bước 3: Cấu hình cho Live Trading
1. Copy `.env.example` thành `.env`
2. Điền API keys từ Binance
3. Chạy: `python main.py`

## 🎮 Demo Mode (Khuyến nghị cho người mới)

Demo mode mô phỏng trading mà không cần API keys:

```bash
python demo.py
```

Chọn:
- **1**: Mô phỏng 5 phút
- **2**: Mô phỏng 30 phút  
- **3**: Backtest nhanh
- **4**: Xem cấu hình

## 🔧 Cấu hình nhanh

File `.env`:
```env
BINANCE_API_KEY=your_api_key
BINANCE_SECRET_KEY=your_secret_key
DEFAULT_SYMBOL=BTCUSDT
TRADE_AMOUNT=0.001
STRATEGY=moving_average
USE_TESTNET=true
```

## 📈 Chiến lược có sẵn

- `moving_average`: MA crossover (mặc định)
- `rsi`: RSI overbought/oversold
- `bollinger_bands`: Bollinger Bands
- `macd`: MACD crossover
- `combined`: Kết hợp nhiều chỉ báo

## ⚠️ Lưu ý quan trọng

1. **LUÔN test với Demo trước**
2. **Bắt đầu với USE_TESTNET=true**
3. **Chỉ đầu tư số tiền có thể mất được**
4. **Theo dõi bot thường xuyên**

## 🆘 Troubleshooting

### Lỗi import module:
```bash
# Từ thư mục crypto-trading-bot/
python -c "import sys; print(sys.path)"
```

### Lỗi API keys:
- Kiểm tra file `.env`
- Đảm bảo API có quyền trading
- Thử với testnet trước

### Bot không giao dịch:
- Kiểm tra balance
- Xem logs trong `logs/`
- Đảm bảo có đủ dữ liệu giá

## 📊 Xem kết quả

Logs: `logs/trading_bot.log`
Database: `data/trading.db`
Status: Bot in real-time

## 🔄 Cập nhật cấu hình

Sửa file `.env` và restart bot:
```bash
# Stop bot: Ctrl+C
# Edit .env
# Restart: python main.py
```

---

**💡 Tips:**
- Demo mode tốt nhất để học
- Backtest để test strategy
- Start small với real money
- Monitor thường xuyên