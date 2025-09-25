#!/usr/bin/env python3
"""
Get all USDT trading pairs from Binance
"""
import requests

def get_all_usdt_pairs():
    """Get all active USDT trading pairs from Binance"""
    try:
        response = requests.get('https://api.binance.com/api/v3/exchangeInfo', timeout=10)
        data = response.json()
        
        # Filter for active USDT pairs
        usdt_pairs = []
        for symbol_info in data['symbols']:
            symbol = symbol_info['symbol']
            status = symbol_info['status']
            
            if symbol.endswith('USDT') and status == 'TRADING':
                # Remove USDT suffix for display
                coin = symbol[:-4]
                usdt_pairs.append({
                    'symbol': symbol,
                    'coin': coin,
                    'base': symbol_info['baseAsset'],
                    'quote': symbol_info['quoteAsset']
                })
        
        # Sort alphabetically by coin name
        usdt_pairs.sort(key=lambda x: x['coin'])
        
        print(f"Total USDT pairs: {len(usdt_pairs)}")
        print("\nTop 50 coins:")
        for i, pair in enumerate(usdt_pairs[:50]):
            print(f"{i+1:2d}. {pair['coin']:8s} - {pair['symbol']}")
        
        # Generate Python list
        symbols = [pair['symbol'] for pair in usdt_pairs]
        coins = [pair['coin'] for pair in usdt_pairs]
        
        print(f"\n# All {len(symbols)} USDT pairs")
        print("symbols = [")
        for i in range(0, len(symbols), 10):
            batch = symbols[i:i+10]
            print("    " + ", ".join(f"'{s}'" for s in batch) + ("," if i+10 < len(symbols) else ""))
        print("]")
        
        print(f"\n# All {len(coins)} coin names (without USDT)")
        print("supported_coins = [")
        for i in range(0, len(coins), 15):
            batch = coins[i:i+15]
            print("    " + ", ".join(f"'{s}'" for s in batch) + ("," if i+15 < len(coins) else ""))
        print("]")
        
        return symbols, coins
        
    except Exception as e:
        print(f"Error fetching symbols: {e}")
        return [], []

if __name__ == "__main__":
    get_all_usdt_pairs()