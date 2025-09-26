# 🚨 Price Alert System - Hướng dẫn sử dụng

## Tính năng chính như Binance

Hệ thống cảnh báo giá thay đổi đột biến với các tính năng tương tự như trên sàn Binance:

### 🚀 Các loại cảnh báo:

1. **PUMP Alert** - Tăng đột biến
   - Phát hiện khi coin tăng >15% trong 24h
   - Kèm theo volume cao (>100k USDT)
   - Gửi thông báo ngay lập tức

2. **DUMP Alert** - Giảm đột biến  
   - Phát hiện khi coin giảm <-15% trong 24h
   - Cảnh báo về khả năng stop loss
   - Volume analysis kèm theo

3. **Volume Spike Alert** - Volume tăng đột biến
   - Phát hiện khi volume tăng 5x so với trung bình
   - Dấu hiệu của tin tức lớn hoặc whale activity
   - Real-time monitoring

4. **Price Breakout Alert** - Vượt khỏi trading range
   - Phát hiện khi giá vượt support/resistance
   - Upward hoặc downward breakout
   - Technical analysis tự động

## 🎮 Cách sử dụng

### Bước 1: Bật Price Alert System
```
Gửi: start alerts
```
- Bắt đầu monitoring 50 top coins
- Threshold mặc định: ±15% pump/dump
- Volume spike: 5x threshold
- Min volume: 100k USDT

### Bước 2: Xem trạng thái alerts
```
Nhấn nút: 🚨 Alerts
```
Hiển thị:
- Status monitoring (ON/OFF)
- Số coins đang theo dõi
- Thống kê alerts đã gửi
- Settings hiện tại

### Bước 3: Điều chỉnh settings
```
Nhấn nút: ⚙️ Alert Settings
```

Các lệnh điều chỉnh:
- `pump 20` - Set pump threshold 20%
- `dump -18` - Set dump threshold -18%
- `volume 4` - Set volume spike 4x
- `minvol 50000` - Set min volume 50k USDT

### Bước 4: Bật/tắt alerts
```
enable alerts - Bật notifications
disable alerts - Tắt notifications  
stop alerts - Dừng monitoring
```

## 📊 Monitoring Coverage

**50 Top Coins được theo dõi:**
- Major: BTC, ETH, BNB, SOL, ADA, XRP, DOT, AVAX
- DeFi: UNI, AAVE, SUSHI, CAKE, CRV, COMP, MKR
- Meme: DOGE, SHIB, PEPE, FLOKI, BONK
- Gaming: SAND, MANA, AXS, GMT, GALA
- AI/Tech: FET, OCEAN, RNDR, WLD
- Và nhiều coins khác...

## ⚡ Real-time Features

- **Monitoring interval:** 1 phút
- **Data source:** Binance API 24hr ticker
- **Anti-spam:** 30 phút timeout giữa alerts của cùng 1 coin
- **Volume filter:** Chỉ alert coins có volume >100k USDT
- **Multi-condition:** Kết hợp price + volume + breakout analysis

## 🔧 Advanced Settings

### Sensitivity Levels:
- **Conservative:** pump/dump ±20%, volume 3x
- **Normal:** pump/dump ±15%, volume 5x (mặc định)  
- **Aggressive:** pump/dump ±10%, volume 8x

### Custom Commands:
```bash
# Sensitivity presets
pump 25      # Conservative pump threshold
dump -12     # Aggressive dump threshold  
volume 6     # Higher volume sensitivity
minvol 200000 # Higher minimum volume
```

## 📱 Alert Format

**PUMP Alert Example:**
```
🚀 PUMP ALERT! 

💰 DOGE 
📈 +18.50% trong 24h!
💵 Price: $0.085000
📊 Volume: 15.0M
🕐 Time: 14:35:20

⚡ Tăng đột biến - Cân nhắc take profit!
```

**DUMP Alert Example:**
```
📉 DUMP ALERT!

💰 DOGE
📉 -22.30% trong 24h!
💵 Price: $0.062000  
📊 Volume: 25.0M
🕐 Time: 14:38:45

⚠️ Giảm đột biến - Cẩn thận stop loss!
```

## 💡 Pro Tips

1. **Volume + Price:** Kết hợp cả 2 yếu tố để xác thực alert
2. **Time Window:** Alerts có 30 phút cooldown để tránh spam
3. **Multiple Timeframes:** Kết hợp với chart analysis cho quyết định tốt hơn
4. **Risk Management:** Luôn set stop loss khi nhận dump alerts

## 🚀 Getting Started

1. Chạy bot: `python price_bot.py`
2. Gửi `/start` trong Telegram
3. Nhấn `🚨 Alerts` để xem trạng thái
4. Gửi `start alerts` để bắt đầu monitoring
5. Đợi alerts khi thị trường có biến động!

---
*Hệ thống được thiết kế để phát hiện các cơ hội và rủi ro trong thị trường crypto volatile, giúp bạn không bỏ lỡ những movement quan trọng!*