#!/usr/bin/env python3
"""
💹 Price Tracker & Chart Generator với Candlestick Charts
Features:
- Real-time price tracking
- Beautiful candlestick charts (Binance style)
- Price alerts and notifications
- 24h statistics
- Multiple timeframes
- Volume analysis
"""
import logging
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time
import math
from src.binance_chart import BinanceLikeChart

class PriceTracker:
    """Price tracking and candlestick chart generation for ALL Binance USDT pairs"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # ALL 422 USDT trading pairs from Binance
        self.symbols = [
            '0GUSDT', '1000CATUSDT', '1000CHEEMSUSDT', '1000SATSUSDT', '1INCHUSDT', '1MBABYDOGEUSDT', 'AUSDT', 'A2ZUSDT', 'AAVEUSDT', 'ACAUSDT',
            'ACEUSDT', 'ACHUSDT', 'ACMUSDT', 'ACTUSDT', 'ACXUSDT', 'ADAUSDT', 'ADXUSDT', 'AEURUSDT', 'AEVOUSDT', 'AGLDUSDT',
            'AIUSDT', 'AIXBTUSDT', 'ALCXUSDT', 'ALGOUSDT', 'ALICEUSDT', 'ALPINEUSDT', 'ALTUSDT', 'AMPUSDT', 'ANIMEUSDT', 'ANKRUSDT',
            'APEUSDT', 'API3USDT', 'APTUSDT', 'ARUSDT', 'ARBUSDT', 'ARDRUSDT', 'ARKUSDT', 'ARKMUSDT', 'ARPAUSDT', 'ASRUSDT',
            'ASTRUSDT', 'ATAUSDT', 'ATMUSDT', 'ATOMUSDT', 'AUCTIONUSDT', 'AUDIOUSDT', 'AVAUSDT', 'AVAXUSDT', 'AVNTUSDT', 'AWEUSDT',
            'AXLUSDT', 'AXSUSDT', 'BABYUSDT', 'BANANAUSDT', 'BANANAS31USDT', 'BANDUSDT', 'BARUSDT', 'BARDUSDT', 'BATUSDT', 'BBUSDT',
            'BCHUSDT', 'BEAMXUSDT', 'BELUSDT', 'BERAUSDT', 'BFUSDUSDT', 'BICOUSDT', 'BIFIUSDT', 'BIGTIMEUSDT', 'BIOUSDT', 'BLURUSDT',
            'BMTUSDT', 'BNBUSDT', 'BNSOLUSDT', 'BNTUSDT', 'BOMEUSDT', 'BONKUSDT', 'BROCCOLI714USDT', 'BTCUSDT', 'BTTCUSDT', 'CUSDT',
            'C98USDT', 'CAKEUSDT', 'CATIUSDT', 'CELOUSDT', 'CELRUSDT', 'CETUSUSDT', 'CFXUSDT', 'CGPTUSDT', 'CHESSUSDT', 'CHRUSDT',
            'CHZUSDT', 'CITYUSDT', 'CKBUSDT', 'COMPUSDT', 'COOKIEUSDT', 'COSUSDT', 'COTIUSDT', 'COWUSDT', 'CRVUSDT', 'CTKUSDT',
            'CTSIUSDT', 'CVCUSDT', 'CVXUSDT', 'CYBERUSDT', 'DUSDT', 'DASHUSDT', 'DATAUSDT', 'DCRUSDT', 'DEGOUSDT', 'DENTUSDT',
            'DEXEUSDT', 'DFUSDT', 'DGBUSDT', 'DIAUSDT', 'DODOUSDT', 'DOGEUSDT', 'DOGSUSDT', 'DOLOUSDT', 'DOTUSDT', 'DUSKUSDT',
            'DYDXUSDT', 'DYMUSDT', 'EDUUSDT', 'EGLDUSDT', 'EIGENUSDT', 'ENAUSDT', 'ENJUSDT', 'ENSUSDT', 'EPICUSDT', 'ERAUSDT',
            'ETCUSDT', 'ETHUSDT', 'ETHFIUSDT', 'EURUSDT', 'EURIUSDT', 'FARMUSDT', 'FDUSDUSDT', 'FETUSDT', 'FIDAUSDT', 'FILUSDT',
            'FIOUSDT', 'FISUSDT', 'FLMUSDT', 'FLOKIUSDT', 'FLOWUSDT', 'FLUXUSDT', 'FORMUSDT', 'FORTHUSDT', 'FTTUSDT', 'FUNUSDT',
            'FXSUSDT', 'GUSDT', 'GALAUSDT', 'GASUSDT', 'GHSTUSDT', 'GLMUSDT', 'GLMRUSDT', 'GMTUSDT', 'GMXUSDT', 'GNOUSDT',
            'GNSUSDT', 'GPSUSDT', 'GRTUSDT', 'GTCUSDT', 'GUNUSDT', 'HAEDALUSDT', 'HBARUSDT', 'HEIUSDT', 'HEMIUSDT', 'HFTUSDT',
            'HIGHUSDT', 'HIVEUSDT', 'HMSTRUSDT', 'HOLOUSDT', 'HOMEUSDT', 'HOOKUSDT', 'HOTUSDT', 'HUMAUSDT', 'HYPERUSDT', 'ICPUSDT',
            'ICXUSDT', 'IDUSDT', 'IDEXUSDT', 'ILVUSDT', 'IMXUSDT', 'INITUSDT', 'INJUSDT', 'IOUSDT', 'IOSTUSDT', 'IOTAUSDT',
            'IOTXUSDT', 'IQUSDT', 'JASMYUSDT', 'JOEUSDT', 'JSTUSDT', 'JTOUSDT', 'JUPUSDT', 'JUVUSDT', 'KAIAUSDT', 'KAITOUSDT',
            'KAVAUSDT', 'KDAUSDT', 'KERNELUSDT', 'KMNOUSDT', 'KNCUSDT', 'KSMUSDT', 'LAUSDT', 'LAYERUSDT', 'LAZIOUSDT', 'LDOUSDT',
            'LINEAUSDT', 'LINKUSDT', 'LISTAUSDT', 'LPTUSDT', 'LQTYUSDT', 'LRCUSDT', 'LSKUSDT', 'LTCUSDT', 'LUMIAUSDT', 'LUNAUSDT',
            'LUNCUSDT', 'MAGICUSDT', 'MANAUSDT', 'MANTAUSDT', 'MASKUSDT', 'MAVUSDT', 'MBLUSDT', 'MBOXUSDT', 'MDTUSDT', 'MEUSDT',
            'MEMEUSDT', 'METISUSDT', 'MINAUSDT', 'MITOUSDT', 'MLNUSDT', 'MOVEUSDT', 'MOVRUSDT', 'MTLUSDT', 'MUBARAKUSDT', 'NEARUSDT',
            'NEIROUSDT', 'NEOUSDT', 'NEWTUSDT', 'NEXOUSDT', 'NFPUSDT', 'NILUSDT', 'NKNUSDT', 'NMRUSDT', 'NOTUSDT', 'NTRNUSDT',
            'NXPCUSDT', 'OGUSDT', 'OGNUSDT', 'OMUSDT', 'OMNIUSDT', 'ONDOUSDT', 'ONEUSDT', 'ONGUSDT', 'ONTUSDT', 'OPUSDT',
            'OPENUSDT', 'ORCAUSDT', 'ORDIUSDT', 'OSMOUSDT', 'OXTUSDT', 'PARTIUSDT', 'PAXGUSDT', 'PENDLEUSDT', 'PENGUUSDT', 'PEOPLEUSDT',
            'PEPEUSDT', 'PERPUSDT', 'PHAUSDT', 'PHBUSDT', 'PIVXUSDT', 'PIXELUSDT', 'PLUMEUSDT', 'PNUTUSDT', 'POLUSDT', 'POLYXUSDT',
            'PONDUSDT', 'PORTALUSDT', 'PORTOUSDT', 'POWRUSDT', 'PROMUSDT', 'PROVEUSDT', 'PSGUSDT', 'PUMPUSDT', 'PUNDIXUSDT', 'PYRUSDT',
            'PYTHUSDT', 'QIUSDT', 'QKCUSDT', 'QNTUSDT', 'QTUMUSDT', 'QUICKUSDT', 'RADUSDT', 'RAREUSDT', 'RAYUSDT', 'RDNTUSDT',
            'REDUSDT', 'REIUSDT', 'RENDERUSDT', 'REQUSDT', 'RESOLVUSDT', 'REZUSDT', 'RIFUSDT', 'RLCUSDT', 'RONINUSDT', 'ROSEUSDT',
            'RPLUSDT', 'RSRUSDT', 'RUNEUSDT', 'RVNUSDT', 'SUSDT', 'SAGAUSDT', 'SAHARAUSDT', 'SANDUSDT', 'SANTOSUSDT', 'SCUSDT',
            'SCRUSDT', 'SCRTUSDT', 'SEIUSDT', 'SFPUSDT', 'SHELLUSDT', 'SHIBUSDT', 'SIGNUSDT', 'SKLUSDT', 'SKYUSDT', 'SLPUSDT',
            'SNXUSDT', 'SOLUSDT', 'SOLVUSDT', 'SOMIUSDT', 'SOPHUSDT', 'SPELLUSDT', 'SPKUSDT', 'SSVUSDT', 'STEEMUSDT', 'STGUSDT',
            'STOUSDT', 'STORJUSDT', 'STRAXUSDT', 'STRKUSDT', 'STXUSDT', 'SUIUSDT', 'SUNUSDT', 'SUPERUSDT', 'SUSHIUSDT', 'SXPUSDT',
            'SXTUSDT', 'SYNUSDT', 'SYRUPUSDT', 'SYSUSDT', 'TUSDT', 'TAOUSDT', 'TFUELUSDT', 'THEUSDT', 'THETAUSDT', 'TIAUSDT',
            'TKOUSDT', 'TLMUSDT', 'TNSRUSDT', 'TONUSDT', 'TOWNSUSDT', 'TRBUSDT', 'TREEUSDT', 'TRUUSDT', 'TRUMPUSDT', 'TRXUSDT',
            'TSTUSDT', 'TURBOUSDT', 'TUSDUSDT', 'TUTUSDT', 'TWTUSDT', 'UMAUSDT', 'UNIUSDT', 'USD1USDT', 'USDCUSDT', 'USDEUSDT',
            'USDPUSDT', 'USTCUSDT', 'USUALUSDT', 'UTKUSDT', 'VANAUSDT', 'VANRYUSDT', 'VELODROMEUSDT', 'VETUSDT', 'VICUSDT', 'VIRTUALUSDT',
            'VOXELUSDT', 'VTHOUSDT', 'WUSDT', 'WANUSDT', 'WAXPUSDT', 'WBETHUSDT', 'WBTCUSDT', 'WCTUSDT', 'WIFUSDT', 'WINUSDT',
            'WLDUSDT', 'WLFIUSDT', 'WOOUSDT', 'XAIUSDT', 'XECUSDT', 'XLMUSDT', 'XNOUSDT', 'XPLUSDT', 'XRPUSDT', 'XTZUSDT',
            'XUSDUSDT', 'XVGUSDT', 'XVSUSDT', 'YFIUSDT', 'YGGUSDT', 'ZECUSDT', 'ZENUSDT', 'ZILUSDT', 'ZKUSDT', 'ZKCUSDT',
            'ZROUSDT', 'ZRXUSDT'
        ]
        
        # Major pairs for quick access (top 20 by market cap)
        self.major_symbols = [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT', 
            'DOGEUSDT', 'ADAUSDT', 'TONUSDT', 'TRXUSDT', 'AVAXUSDT',
            'SHIBUSDT', 'WBTCUSDT', 'LINKUSDT', 'BCHUSDT', 'DOTUSDT',
            'SUIUSDT', 'NEARUSDT', 'LTCUSDT', 'UNIUSDT', 'PEPEUSDT'
        ]
        
        # Price data storage
        self.current_prices: Dict[str, float] = {}
        self.price_history: Dict[str, List[Tuple[datetime, float]]] = {
            symbol: [] for symbol in self.symbols
        }
        self.daily_stats: Dict[str, Dict] = {}
        
        # Initialize candlestick chart generator
        self.candlestick_chart = BinanceLikeChart()
        
        # Legacy chart settings (kept for compatibility)
        self.chart_width = 40
        self.chart_height = 8
        
        self.logger.info(f"Price Tracker initialized for {len(self.symbols)} symbols with candlestick charts")
    
    def get_current_prices(self) -> Dict[str, Dict]:
        """Lấy giá hiện tại tất cả coins"""
        try:
            url = "https://api.binance.com/api/v3/ticker/24hr"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                result = {}
                
                for item in data:
                    symbol = item['symbol']
                    if symbol in self.symbols:
                        current_price = float(item['lastPrice'])
                        price_change = float(item['priceChange'])
                        price_change_percent = float(item['priceChangePercent'])
                        volume = float(item['volume'])
                        high_24h = float(item['highPrice'])
                        low_24h = float(item['lowPrice'])
                        
                        # Update current prices
                        self.current_prices[symbol] = current_price
                        
                        # Store in history
                        now = datetime.now()
                        if symbol not in self.price_history:
                            self.price_history[symbol] = []
                        self.price_history[symbol].append((now, current_price))
                        
                        # Keep only last 100 points per symbol
                        if len(self.price_history[symbol]) > 100:
                            self.price_history[symbol].pop(0)
                        
                        # Store daily stats
                        self.daily_stats[symbol] = {
                            'price': current_price,
                            'change': price_change,
                            'change_percent': price_change_percent,
                            'volume': volume,
                            'high_24h': high_24h,
                            'low_24h': low_24h
                        }
                        
                        result[symbol] = {
                            'price': current_price,
                            'change': price_change,
                            'change_percent': price_change_percent,
                            'volume': volume,
                            'high_24h': high_24h,
                            'low_24h': low_24h,
                            'emoji': '🟢' if price_change_percent >= 0 else '🔴'
                        }
                
                self.logger.info(f"Updated prices for {len(result)} symbols")
                return result
            
        except Exception as e:
            self.logger.error(f"Error fetching prices: {e}")
            return {}
    
    def get_price_by_symbol(self, symbol: str) -> Optional[Dict]:
        """Lấy giá 1 symbol cụ thể"""
        try:
            symbol = symbol.upper()
            if not symbol.endswith('USDT'):
                symbol += 'USDT'
            
            url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                current_price = float(data['lastPrice'])
                price_change = float(data['priceChange'])
                price_change_percent = float(data['priceChangePercent'])
                volume = float(data['volume'])
                high_24h = float(data['highPrice'])
                low_24h = float(data['lowPrice'])
                
                # Update tracking
                self.current_prices[symbol] = current_price
                
                return {
                    'symbol': symbol,
                    'price': current_price,
                    'change': price_change,
                    'change_percent': price_change_percent,
                    'volume': volume,
                    'high_24h': high_24h,
                    'low_24h': low_24h,
                    'emoji': '🟢' if price_change_percent >= 0 else '🔴'
                }
            
        except Exception as e:
            self.logger.error(f"Error fetching price for {symbol}: {e}")
            return None
    
    def get_klines(self, symbol: str, interval: str = '1h', limit: int = 24) -> List[Dict]:
        """Lấy dữ liệu candlestick để vẽ chart"""
        try:
            symbol = symbol.upper()
            if not symbol.endswith('USDT'):
                symbol += 'USDT'
            
            url = f"https://api.binance.com/api/v3/klines"
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                klines = []
                
                for item in data:
                    klines.append({
                        'timestamp': int(item[0]),
                        'open': float(item[1]),
                        'high': float(item[2]),
                        'low': float(item[3]),
                        'close': float(item[4]),
                        'volume': float(item[5])
                    })
                
                return klines
            
        except Exception as e:
            self.logger.error(f"Error fetching klines for {symbol}: {e}")
            return []
    
    def generate_candlestick_chart(self, symbol: str, interval: str = '1h', 
                                  limit: int = 20) -> str:
        """Generate beautiful candlestick chart using BinanceLikeChart"""
        try:
            return self.candlestick_chart.generate_professional_chart(symbol, interval, limit)
        except Exception as e:
            self.logger.error(f"Error generating candlestick chart for {symbol}: {e}")
            return f"❌ Lỗi tạo candlestick chart cho {symbol}: {e}"
    
    def get_multi_timeframe_chart(self, symbol: str) -> str:
        """Get multi-timeframe candlestick analysis"""
        try:
            return self.candlestick_chart.get_multiple_timeframes(symbol)
        except Exception as e:
            self.logger.error(f"Error generating multi-timeframe chart for {symbol}: {e}")
            return f"❌ Lỗi tạo multi-timeframe chart cho {symbol}: {e}"
    
    def generate_ascii_chart(self, symbol: str, interval: str = '1h', 
                            limit: int = 24) -> str:
        """Legacy ASCII chart method - now returns beautiful candlestick chart"""
        # Redirect to beautiful candlestick chart
        return self.generate_candlestick_chart(symbol, interval, limit)
    
    def _format_volume(self, volume: float) -> str:
        """Format volume number"""
        if volume >= 1e9:
            return f"{volume/1e9:.1f}B"
        elif volume >= 1e6:
            return f"{volume/1e6:.1f}M"
        elif volume >= 1e3:
            return f"{volume/1e3:.1f}K"
        else:
            return f"{volume:.1f}"
    
    def get_top_movers(self, limit: int = 5) -> Tuple[List[Dict], List[Dict]]:
        """Lấy top gainers và losers"""
        try:
            prices = self.get_current_prices()
            
            # Sort by change percent
            sorted_by_change = sorted(
                prices.items(),
                key=lambda x: x[1]['change_percent'],
                reverse=True
            )
            
            gainers = []
            losers = []
            
            # Top gainers
            for symbol, data in sorted_by_change[:limit]:
                if data['change_percent'] > 0:
                    gainers.append({
                        'symbol': symbol,
                        'price': data['price'],
                        'change_percent': data['change_percent']
                    })
            
            # Top losers
            for symbol, data in sorted_by_change[-limit:]:
                if data['change_percent'] < 0:
                    losers.append({
                        'symbol': symbol,
                        'price': data['price'],
                        'change_percent': data['change_percent']
                    })
            
            return gainers, losers
            
        except Exception as e:
            self.logger.error(f"Error getting top movers: {e}")
            return [], []
    
    def get_market_summary(self) -> str:
        """Tạo market summary"""
        try:
            prices = self.get_current_prices()
            gainers, losers = self.get_top_movers(3)
            
            if not prices:
                return "❌ Không thể lấy dữ liệu market"
            
            # Calculate market stats
            total_symbols = len(prices)
            up_count = sum(1 for data in prices.values() if data['change_percent'] >= 0)
            down_count = total_symbols - up_count
            
            market_sentiment = "🟢 TĂNG" if up_count > down_count else "🔴 GIẢM" if down_count > up_count else "🟡 ĐỨNG IM"
            
            summary = f"""📊 MARKET SUMMARY - {len(self.symbols)} Coins

🎯 MARKET SENTIMENT: {market_sentiment}
📈 Tăng: {up_count} | 📉 Giảm: {down_count}

🏆 TOP GAINERS:"""
            
            for gainer in gainers:
                summary += f"""
🟢 {gainer['symbol'].replace('USDT', '')}: ${gainer['price']:.4f} (+{gainer['change_percent']:.2f}%)"""
            
            if losers:
                summary += f"""

💥 TOP LOSERS:"""
                for loser in losers:
                    summary += f"""
🔴 {loser['symbol'].replace('USDT', '')}: ${loser['price']:.4f} ({loser['change_percent']:.2f}%)"""
            
            # Add major coins
            major_coins = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
            summary += f"""

💎 MAJOR COINS:"""
            
            for symbol in major_coins:
                if symbol in prices:
                    data = prices[symbol]
                    coin_name = symbol.replace('USDT', '')
                    summary += f"""
{data['emoji']} {coin_name}: ${data['price']:.2f} ({data['change_percent']:+.2f}%)"""
            
            summary += f"""

🕒 Cập nhật: {datetime.now().strftime('%H:%M:%S')}
💡 Gửi tên coin để xem chi tiết + chart"""
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error creating market summary: {e}")
            return "❌ Lỗi tạo market summary"

# Test function
if __name__ == "__main__":
    tracker = PriceTracker()
    
    # Test price fetching
    print("Testing price fetching...")
    prices = tracker.get_current_prices()
    print(f"Fetched {len(prices)} prices")
    
    # Test individual price
    btc_price = tracker.get_price_by_symbol('BTC')
    if btc_price:
        print(f"BTC: ${btc_price['price']:.2f}")
    
    # Test chart generation
    print("\nGenerating BTC chart...")
    chart = tracker.generate_ascii_chart('BTCUSDT')
    print(chart)
    
    # Test market summary
    print("\nMarket Summary:")
    summary = tracker.get_market_summary()
    print(summary)