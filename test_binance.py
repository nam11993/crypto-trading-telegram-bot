#!/usr/bin/env python3
"""
🧪 Test Binance Account API
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.binance_account import BinanceAccountChecker

def test_binance_api():
    """Test Binance API"""
    print("🧪 TESTING BINANCE API")
    print("=" * 50)
    
    checker = BinanceAccountChecker()
    
    print("1. Testing Account Info...")
    account = checker.get_account_info()
    if "error" in account:
        print(f"❌ Lỗi: {account['error']}")
        print(f"💡 {account['message']}")
    else:
        print(f"✅ Account Type: {account['account_type']}")
        print(f"✅ Can Trade: {account['can_trade']}")
        print(f"✅ Balances found: {len(account['balances'])}")
    
    print("\n2. Testing USDT Balance...")
    usdt = checker.get_usdt_balance()
    if "error" not in usdt:
        print(f"💰 USDT Total: {usdt['total']}")
    
    print("\n3. Testing BTC Balance...")
    btc = checker.get_btc_balance()
    if "error" not in btc:
        print(f"₿ BTC Total: {btc['total']}")
    
    print("\n4. Testing Price...")
    price = checker.get_current_price()
    if "error" not in price:
        print(f"💹 {price['symbol']}: ${price['price']:,.2f}")
    
    print("\n5. Full Account Summary:")
    print("-" * 30)
    summary = checker.format_account_summary()
    print(summary)

if __name__ == "__main__":
    test_binance_api()