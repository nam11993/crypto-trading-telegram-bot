"""
🔑 Binance API Integration
Tích hợp API để check thông tin tài khoản thật
"""
import requests
import hmac
import hashlib
import time
from urllib.parse import urlencode
from config.config import Config

class BinanceAccountChecker:
    """Class để check thông tin tài khoản Binance"""
    
    def __init__(self):
        self.config = Config()
        self.api_key = self.config.BINANCE_API_KEY
        self.secret_key = self.config.BINANCE_SECRET_KEY
        self.use_testnet = self.config.USE_TESTNET
        
        # URLs
        if self.use_testnet:
            self.base_url = "https://testnet.binance.vision/api"
        else:
            self.base_url = "https://api.binance.com/api"
    
    def _create_signature(self, query_string):
        """Tạo signature cho request"""
        return hmac.new(
            self.secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _make_request(self, endpoint, params=None):
        """Thực hiện request tới Binance API"""
        if not self.api_key or not self.secret_key:
            return {
                "error": "Binance API keys chưa được cấu hình",
                "message": "Hãy thêm BINANCE_API_KEY và BINANCE_SECRET_KEY vào .env"
            }
        
        if params is None:
            params = {}
        
        # Thêm timestamp
        params['timestamp'] = int(time.time() * 1000)
        
        # Tạo query string
        query_string = urlencode(params)
        
        # Tạo signature
        signature = self._create_signature(query_string)
        
        # Headers
        headers = {
            'X-MBX-APIKEY': self.api_key
        }
        
        # URL với signature
        url = f"{self.base_url}{endpoint}?{query_string}&signature={signature}"
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            return response.json()
        except Exception as e:
            return {
                "error": "Lỗi kết nối API",
                "message": str(e)
            }
    
    def get_account_info(self):
        """Lấy thông tin tài khoản"""
        endpoint = "/v3/account"
        result = self._make_request(endpoint)
        
        if "error" in result:
            return result
        
        # Parse account info
        account_info = {
            "can_trade": result.get("canTrade", False),
            "can_withdraw": result.get("canWithdraw", False),
            "can_deposit": result.get("canDeposit", False),
            "account_type": result.get("accountType", "Unknown"),
            "balances": [],
            "total_wallet_balance": 0.0
        }
        
        # Lọc balances có giá trị > 0
        for balance in result.get("balances", []):
            free = float(balance.get("free", 0))
            locked = float(balance.get("locked", 0))
            total = free + locked
            
            if total > 0:
                account_info["balances"].append({
                    "asset": balance["asset"],
                    "free": free,
                    "locked": locked,
                    "total": total
                })
        
        return account_info
    
    def get_usdt_balance(self):
        """Lấy số dư USDT"""
        account = self.get_account_info()
        
        if "error" in account:
            return account
        
        for balance in account["balances"]:
            if balance["asset"] == "USDT":
                return {
                    "asset": "USDT",
                    "free": balance["free"],
                    "locked": balance["locked"],
                    "total": balance["total"]
                }
        
        return {
            "asset": "USDT",
            "free": 0.0,
            "locked": 0.0,
            "total": 0.0
        }
    
    def get_btc_balance(self):
        """Lấy số dư BTC"""
        account = self.get_account_info()
        
        if "error" in account:
            return account
        
        for balance in account["balances"]:
            if balance["asset"] == "BTC":
                return {
                    "asset": "BTC",
                    "free": balance["free"],
                    "locked": balance["locked"],
                    "total": balance["total"]
                }
        
        return {
            "asset": "BTC",
            "free": 0.0,
            "locked": 0.0,
            "total": 0.0
        }
    
    def get_current_price(self, symbol="BTCUSDT"):
        """Lấy giá hiện tại"""
        endpoint = "/v3/ticker/price"
        url = f"{self.base_url}{endpoint}?symbol={symbol}"
        
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            return {
                "symbol": data["symbol"],
                "price": float(data["price"])
            }
        except Exception as e:
            return {
                "error": "Lỗi lấy giá",
                "message": str(e)
            }
    
    def get_portfolio_value(self):
        """Tính tổng giá trị portfolio theo USDT"""
        account = self.get_account_info()
        
        if "error" in account:
            return account
        
        total_value = 0.0
        portfolio = []
        
        for balance in account["balances"]:
            asset = balance["asset"]
            total_amount = balance["total"]
            
            if asset == "USDT":
                # USDT = 1:1
                value_usdt = total_amount
            elif asset == "BTC":
                # Lấy giá BTC/USDT
                price_info = self.get_current_price("BTCUSDT")
                if "error" not in price_info:
                    value_usdt = total_amount * price_info["price"]
                else:
                    value_usdt = 0
            else:
                # Thử lấy giá với USDT
                price_info = self.get_current_price(f"{asset}USDT")
                if "error" not in price_info:
                    value_usdt = total_amount * price_info["price"]
                else:
                    value_usdt = 0
            
            portfolio.append({
                "asset": asset,
                "amount": total_amount,
                "value_usdt": value_usdt
            })
            
            total_value += value_usdt
        
        return {
            "total_value_usdt": total_value,
            "portfolio": portfolio
        }
    
    def format_account_summary(self):
        """Format thông tin tài khoản để hiển thị"""
        account = self.get_account_info()
        
        if "error" in account:
            return f"""❌ LỖI BINANCE API

{account['error']}
{account.get('message', '')}

💡 HƯỚNG DẪN SETUP:
1. Truy cập binance.com → API Management
2. Tạo API Key mới (chỉ đọc)
3. Thêm vào .env:
   BINANCE_API_KEY=your_api_key
   BINANCE_SECRET_KEY=your_secret_key"""
        
        # Portfolio value
        portfolio = self.get_portfolio_value()
        total_value = portfolio.get("total_value_usdt", 0)
        
        # Format balances
        balance_text = ""
        for balance in account["balances"][:5]:  # Top 5
            asset = balance["asset"]
            amount = balance["total"]
            if amount >= 0.001:  # Chỉ hiện những coin có giá trị
                balance_text += f"• {asset}: {amount:.6f}\n"
        
        mode = "🔄 TESTNET" if self.use_testnet else "💰 LIVE"
        trade_status = "✅ CÓ THỂ" if account["can_trade"] else "❌ KHÔNG THỂ"
        
        return f"""💼 BINANCE ACCOUNT INFO

{mode} MODE
📊 Giao dịch: {trade_status}

💰 PORTFOLIO:
Tổng giá trị: ${total_value:.2f} USDT

🪙 TOP BALANCES:
{balance_text if balance_text else "• Không có coin nào"}

📈 PERMISSIONS:
• Trade: {'✅' if account['can_trade'] else '❌'}
• Withdraw: {'✅' if account['can_withdraw'] else '❌'}
• Deposit: {'✅' if account['can_deposit'] else '❌'}

🕐 Cập nhật: {time.strftime('%H:%M:%S')}"""