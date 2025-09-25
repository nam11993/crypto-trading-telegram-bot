@echo off
echo ==================================================
echo          🤖 CRYPTO TRADING BOT 
echo ==================================================
echo.
echo Chọn chế độ chạy:
echo 1. Demo Mode (Không cần API keys)
echo 2. Real Trading (Cần API keys)
echo 3. Setup và cài đặt
echo.
set /p choice="Nhập lựa chọn (1-3): "

if "%choice%"=="1" (
    echo.
    echo 🎮 Khởi động Demo Mode...
    python demo.py
    pause
) else if "%choice%"=="2" (
    echo.
    echo 🚨 CẢNH BÁO: Chế độ này sử dụng tiền thật!
    echo Đảm bảo bạn đã:
    echo - Cấu hình API keys trong file .env
    echo - Test kỹ với Demo mode trước
    echo - Hiểu rõ về rủi ro trading
    echo.
    set /p confirm="Gõ YES để xác nhận: "
    if "%confirm%"=="YES" (
        python main.py
    ) else (
        echo Hủy bỏ real trading.
    )
    pause
) else if "%choice%"=="3" (
    echo.
    echo 🔧 Chạy setup...
    python setup.py
    pause
) else (
    echo Lựa chọn không hợp lệ!
    pause
)