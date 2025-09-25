#!/usr/bin/env python3
"""
📊 Professional Candlestick Chart Generator - Exactly Like Binance
Features:
- Generate PNG images with beautiful candlestick charts
- Professional styling like Binance
- Multiple timeframes
- Volume indicators
- Technical indicators overlay
- Support/Resistance levels
- Real OHLCV data
"""
import logging
import requests
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import io
import os
from typing import Dict, List, Optional, Tuple

# Set matplotlib to use non-interactive backend
import matplotlib
matplotlib.use('Agg')

class BinanceLikeChart:
    """Generate professional candlestick charts exactly like Binance"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Chart styling - Binance colors
        self.bg_color = '#0B1426'  # Dark background like Binance
        self.grid_color = '#2B3139'  # Grid lines
        self.text_color = '#EAECEF'  # Text color
        self.green_color = '#0ECB81'  # Up candle green
        self.red_color = '#F6465D'  # Down candle red
        self.volume_up_color = '#0ECB8180'  # Volume up (with transparency)
        self.volume_down_color = '#F6465D80'  # Volume down (with transparency)
        self.current_price_color = '#FCD535'  # Current price line
        
        # Chart settings
        self.figure_width = 16
        self.figure_height = 10
        self.dpi = 100
        
        self.logger.info("Professional Binance-like Chart Generator initialized")
    
    def get_klines_data(self, symbol: str, interval: str = '1h', limit: int = 100) -> pd.DataFrame:
        """Get OHLCV data and return as DataFrame"""
        try:
            symbol = symbol.upper()
            if not symbol.endswith('USDT'):
                symbol += 'USDT'
            
            url = "https://api.binance.com/api/v3/klines"
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Convert to DataFrame
                df = pd.DataFrame(data, columns=[
                    'timestamp', 'open', 'high', 'low', 'close', 'volume',
                    'close_time', 'quote_asset_volume', 'number_of_trades',
                    'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
                ])
                
                # Convert data types
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df['open'] = df['open'].astype(float)
                df['high'] = df['high'].astype(float)
                df['low'] = df['low'].astype(float)
                df['close'] = df['close'].astype(float)
                df['volume'] = df['volume'].astype(float)
                
                return df
                
        except Exception as e:
            self.logger.error(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators"""
        try:
            # Moving averages
            df['MA20'] = df['close'].rolling(window=20).mean()
            df['MA50'] = df['close'].rolling(window=50).mean()
            
            # Bollinger Bands
            df['BB_upper'] = df['MA20'] + (df['close'].rolling(window=20).std() * 2)
            df['BB_lower'] = df['MA20'] - (df['close'].rolling(window=20).std() * 2)
            
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error calculating indicators: {e}")
            return df
    
    def generate_professional_chart(self, symbol: str, interval: str = '1h', 
                                  limit: int = 100, show_indicators: bool = True) -> str:
        """Generate professional candlestick chart PNG"""
        try:
            # Get data
            df = self.get_klines_data(symbol, interval, limit)
            
            if df.empty:
                return f"❌ Không thể lấy dữ liệu cho {symbol}"
            
            # Calculate indicators
            if show_indicators:
                df = self.calculate_technical_indicators(df)
            
            # Create figure with subplots
            fig = plt.figure(figsize=(self.figure_width, self.figure_height), 
                           facecolor=self.bg_color, dpi=self.dpi)
            
            # Main price chart (70% of height)
            ax1 = fig.add_subplot(2, 1, 1, facecolor=self.bg_color)
            
            # Volume chart (30% of height)  
            ax2 = fig.add_subplot(2, 1, 2, facecolor=self.bg_color)
            
            # Adjust subplot spacing
            plt.subplots_adjust(hspace=0.1, left=0.05, right=0.98, top=0.95, bottom=0.08)
            
            # Plot candlesticks
            self._plot_candlesticks(ax1, df)
            
            # Plot technical indicators
            if show_indicators and len(df) > 50:
                self._plot_indicators(ax1, df)
            
            # Plot volume
            self._plot_volume(ax2, df)
            
            # Style the axes
            self._style_axes(ax1, ax2, df, symbol, interval)
            
            # Add title and info
            self._add_title_and_info(fig, ax1, df, symbol, interval)
            
            # Save to file
            filename = f'chart_{symbol}_{interval}_{int(datetime.now().timestamp())}.png'
            filepath = os.path.join('charts', filename)
            
            # Create charts directory if not exists
            os.makedirs('charts', exist_ok=True)
            
            # Save with high quality
            plt.savefig(filepath, facecolor=self.bg_color, edgecolor='none',
                       bbox_inches='tight', dpi=self.dpi, format='png')
            
            plt.close()  # Close to free memory
            
            # Return filepath for Telegram
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error generating chart for {symbol}: {e}")
            return f"❌ Lỗi tạo chart cho {symbol}: {e}"
    
    def _plot_candlesticks(self, ax, df):
        """Plot candlestick chart"""
        try:
            for i, (idx, row) in enumerate(df.iterrows()):
                # Determine candle color
                color = self.green_color if row['close'] >= row['open'] else self.red_color
                
                # Candle body
                body_height = abs(row['close'] - row['open'])
                body_bottom = min(row['open'], row['close'])
                
                # Draw body
                if body_height > 0:
                    body = Rectangle((i - 0.4, body_bottom), 0.8, body_height,
                                   facecolor=color, edgecolor=color, linewidth=0.5)
                    ax.add_patch(body)
                else:
                    # Doji - draw line
                    ax.plot([i - 0.4, i + 0.4], [row['open'], row['open']], 
                           color=color, linewidth=1)
                
                # Upper shadow
                if row['high'] > max(row['open'], row['close']):
                    ax.plot([i, i], [max(row['open'], row['close']), row['high']], 
                           color=color, linewidth=1)
                
                # Lower shadow  
                if row['low'] < min(row['open'], row['close']):
                    ax.plot([i, i], [row['low'], min(row['open'], row['close'])], 
                           color=color, linewidth=1)
            
            # Current price line
            current_price = df.iloc[-1]['close']
            ax.axhline(y=current_price, color=self.current_price_color, 
                      linewidth=1, linestyle='--', alpha=0.8)
            
            # Add current price label
            ax.text(len(df) - 1, current_price, f' ${current_price:.4f}', 
                   color=self.current_price_color, fontsize=10, fontweight='bold',
                   verticalalignment='center')
                   
        except Exception as e:
            self.logger.error(f"Error plotting candlesticks: {e}")
    
    def _plot_indicators(self, ax, df):
        """Plot technical indicators"""
        try:
            x = range(len(df))
            
            # Moving averages
            if 'MA20' in df.columns and not df['MA20'].isna().all():
                ax.plot(x, df['MA20'], color='#FF6B35', linewidth=1.5, alpha=0.8, label='MA20')
            
            if 'MA50' in df.columns and not df['MA50'].isna().all():
                ax.plot(x, df['MA50'], color='#4ECDC4', linewidth=1.5, alpha=0.8, label='MA50')
            
            # Bollinger Bands
            if all(col in df.columns for col in ['BB_upper', 'BB_lower']):
                if not df['BB_upper'].isna().all():
                    ax.plot(x, df['BB_upper'], color='#9B59B6', linewidth=1, alpha=0.6)
                    ax.plot(x, df['BB_lower'], color='#9B59B6', linewidth=1, alpha=0.6)
                    ax.fill_between(x, df['BB_upper'], df['BB_lower'], 
                                  color='#9B59B6', alpha=0.1)
            
            # Add legend
            ax.legend(loc='upper left', frameon=False, fontsize=9, 
                     facecolor=self.bg_color, edgecolor='none')
                     
        except Exception as e:
            self.logger.error(f"Error plotting indicators: {e}")
    
    def _plot_volume(self, ax, df):
        """Plot volume bars"""
        try:
            for i, (idx, row) in enumerate(df.iterrows()):
                # Volume color based on price movement
                color = self.volume_up_color if row['close'] >= row['open'] else self.volume_down_color
                
                # Volume bar
                ax.bar(i, row['volume'], width=0.8, color=color, alpha=0.7)
            
            # Volume moving average
            if len(df) > 20:
                volume_ma = df['volume'].rolling(window=20).mean()
                ax.plot(range(len(df)), volume_ma, color='#FFA500', linewidth=1, alpha=0.8)
                
        except Exception as e:
            self.logger.error(f"Error plotting volume: {e}")
    
    def _style_axes(self, ax1, ax2, df, symbol, interval):
        """Style the chart axes like Binance"""
        try:
            # Main chart styling
            ax1.set_facecolor(self.bg_color)
            ax1.tick_params(colors=self.text_color, labelsize=9)
            ax1.grid(True, color=self.grid_color, linewidth=0.5, alpha=0.3)
            ax1.spines['bottom'].set_color(self.grid_color)
            ax1.spines['top'].set_color(self.grid_color)
            ax1.spines['left'].set_color(self.grid_color)
            ax1.spines['right'].set_color(self.grid_color)
            
            # Volume chart styling
            ax2.set_facecolor(self.bg_color)
            ax2.tick_params(colors=self.text_color, labelsize=8)
            ax2.grid(True, color=self.grid_color, linewidth=0.5, alpha=0.3)
            ax2.spines['bottom'].set_color(self.grid_color)
            ax2.spines['top'].set_color(self.grid_color)
            ax2.spines['left'].set_color(self.grid_color)
            ax2.spines['right'].set_color(self.grid_color)
            
            # X-axis labels (time)
            x_ticks = range(0, len(df), max(1, len(df)//10))
            x_labels = [df.iloc[i]['timestamp'].strftime('%m-%d %H:%M') for i in x_ticks]
            
            ax1.set_xticks(x_ticks)
            ax1.set_xticklabels([])  # Hide x labels on main chart
            
            ax2.set_xticks(x_ticks) 
            ax2.set_xticklabels(x_labels, rotation=45, ha='right')
            
            # Y-axis formatting
            ax1.yaxis.set_label_position('right')
            ax1.yaxis.tick_right()
            ax2.yaxis.set_label_position('right')
            ax2.yaxis.tick_right()
            
            # Set limits
            ax1.set_xlim(-0.5, len(df) - 0.5)
            ax2.set_xlim(-0.5, len(df) - 0.5)
            
        except Exception as e:
            self.logger.error(f"Error styling axes: {e}")
    
    def _add_title_and_info(self, fig, ax1, df, symbol, interval):
        """Add title and trading info"""
        try:
            # Calculate stats
            current = df.iloc[-1]
            previous = df.iloc[-2] if len(df) > 1 else current
            
            price_change = current['close'] - previous['close']
            change_percent = (price_change / previous['close']) * 100 if previous['close'] > 0 else 0
            
            volume_24h = current['volume']
            high_24h = df['high'].max()
            low_24h = df['low'].min()
            
            # Timeframe name
            timeframe_names = {
                '1m': '1m', '5m': '5m', '15m': '15m',
                '1h': '1H', '4h': '4H', '1d': '1D'
            }
            tf_name = timeframe_names.get(interval, interval)
            
            # Title
            change_color = self.green_color if price_change >= 0 else self.red_color
            title = f'{symbol} • {tf_name} • ${current["close"]:.4f} '
            title += f'({price_change:+.4f} {change_percent:+.2f}%)'
            
            fig.suptitle(title, color=self.text_color, fontsize=16, fontweight='bold', y=0.98)
            
            # Info text
            info_text = f'Vol: {self._format_volume(volume_24h)} • '
            info_text += f'H: ${high_24h:.4f} • L: ${low_24h:.4f}'
            
            ax1.text(0.01, 0.98, info_text, transform=ax1.transAxes, 
                    color=self.text_color, fontsize=10, verticalalignment='top')
            
            # Watermark
            ax1.text(0.99, 0.02, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 
                    transform=ax1.transAxes, color=self.text_color, fontsize=8, 
                    horizontalalignment='right', alpha=0.7)
                    
        except Exception as e:
            self.logger.error(f"Error adding title/info: {e}")
    
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
    
    def generate_comparison_chart(self, symbols: List[str], interval: str = '1h') -> str:
        """Generate comparison chart for multiple symbols"""
        try:
            fig, ax = plt.subplots(figsize=(16, 8), facecolor=self.bg_color)
            ax.set_facecolor(self.bg_color)
            
            colors = [self.green_color, self.red_color, '#FF6B35', '#4ECDC4', '#9B59B6']
            
            for i, symbol in enumerate(symbols[:5]):  # Max 5 symbols
                df = self.get_klines_data(symbol, interval, 100)
                if not df.empty:
                    # Normalize to percentage change
                    base_price = df.iloc[0]['close']
                    normalized = ((df['close'] - base_price) / base_price) * 100
                    
                    ax.plot(range(len(df)), normalized, 
                           color=colors[i % len(colors)], linewidth=2, 
                           label=symbol.replace('USDT', ''), alpha=0.8)
            
            # Styling
            ax.set_facecolor(self.bg_color)
            ax.tick_params(colors=self.text_color)
            ax.grid(True, color=self.grid_color, alpha=0.3)
            ax.legend(loc='upper left', frameon=False, fontsize=12)
            ax.set_ylabel('Price Change (%)', color=self.text_color)
            ax.set_title('Price Comparison Chart', color=self.text_color, fontsize=16, pad=20)
            
            # Save
            filename = f'comparison_{interval}_{int(datetime.now().timestamp())}.png'
            filepath = os.path.join('charts', filename)
            os.makedirs('charts', exist_ok=True)
            
            plt.savefig(filepath, facecolor=self.bg_color, bbox_inches='tight', dpi=100)
            plt.close()
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error generating comparison chart: {e}")
            return f"❌ Lỗi tạo comparison chart: {e}"

# Test function
if __name__ == "__main__":
    chart_gen = BinanceLikeChart()
    
    print("Generating professional BTC chart...")
    result = chart_gen.generate_professional_chart('BTCUSDT', '1h', 200)
    print(f"Chart saved: {result}")
    
    print("\nGenerating ETH chart...")  
    result2 = chart_gen.generate_professional_chart('ETHUSDT', '4h', 150)
    print(f"Chart saved: {result2}")
    
    print("\nGenerating comparison chart...")
    result3 = chart_gen.generate_comparison_chart(['BTCUSDT', 'ETHUSDT', 'ADAUSDT'], '1h')
    print(f"Comparison chart saved: {result3}")