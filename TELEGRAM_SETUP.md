# 📱 HƯỚNG DẪN SETUP TELEGRAM BOT

## Bước 1: Tạo Telegram Bot

1. **Mở Telegram** và tìm kiếm `@BotFather`
2. **Chat với BotFather** và gửi lệnh `/newbot`
3. **Đặt tên cho bot** (ví dụ: My Trading Bot)
4. **Đặt username cho bot** (phải kết thúc bằng "bot", ví dụ: mytradingbot)
5. **Copy Bot Token** mà BotFather gửi cho bạn

## Bước 2: Lấy Chat ID

### Phương pháp 1: Sử dụng script Python
```python
# Chạy lệnh này sau khi setup bot token
python get_chat_id.py
```

### Phương pháp 2: Thủ công
1. Gửi tin nhắn `/start` cho bot của bạn
2. Truy cập: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. Tìm `"chat":{"id":123456789}` trong response
4. Copy số ID đó

## Bước 3: Cấu hình .env

Điền thông tin vào file `.env`:
```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

## Bước 4: Test Bot

```bash
python telegram_test.py
```

## 🔧 Troubleshooting

### Bot không phản hồi:
- Kiểm tra Bot Token
- Đảm bảo bot đã được start (`/start`)
- Kiểm tra Chat ID

### Không nhận được tin nhắn:
- Kiểm tra Chat ID đúng chưa
- Bot phải được add vào group (nếu sử dụng group)

### Permission errors:
- Bot cần quyền gửi tin nhắn
- Trong group: bot cần là admin

---

**💡 Tips:**
- Có thể tạo group và add bot vào để nhiều người theo dõi
- Sử dụng Bot Commands để dễ tương tác
- Bảo mật Bot Token như password