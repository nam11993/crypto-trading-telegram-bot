#!/usr/bin/env python3
"""Test chart command to debug issue"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from price_bot import handle_message

def test_chart_commands():
    """Test various chart commands"""
    
    commands = [
        "📈 Chart",
        "Chart", 
        "BTC",
        "ETH",
        "BTC 4h"
    ]
    
    print("Testing chart commands...")
    print("=" * 50)
    
    for cmd in commands:
        print(f"\nTesting: '{cmd}'")
        print(f"Command repr: {repr(cmd)}")
        
        try:
            result = handle_message(cmd, "TestUser")
            
            if result:
                if "Chart" in result and "đã gửi" in result:
                    print("✅ SUCCESS: Chart sent!")
                elif len(result) > 100:
                    print(f"📝 TEXT RESPONSE: {len(result)} chars")
                else:
                    print(f"💬 SHORT RESPONSE: {result}")
            else:
                print("❌ No response")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        print("-" * 30)

if __name__ == "__main__":
    test_chart_commands()