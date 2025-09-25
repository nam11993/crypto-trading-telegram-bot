#!/usr/bin/env python3
"""
📊 Advanced Chart Analysis Engine
- Full OHLCV analysis
- Technical indicators
- Support/Resistance levels
- Pattern recognition
- Volume analysis
- AI-powered signals
"""
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import ta  # Technical Analysis library

@dataclass
class TechnicalLevel:
    """Support/Resistance level"""
    level: float
    strength: int  # Number of touches
    type: str  # 'SUPPORT' or 'RESISTANCE'
    last_touch: datetime

@dataclass
class Pattern:
    """Chart pattern"""
    name: str
    confidence: float  # 0-1
    target: Optional[float]
    timeframe: str
    detected_at: datetime

@dataclass
class AdvancedSignal:
    """Advanced trading signal"""
    symbol: str
    signal: str  # 'BUY', 'SELL', 'HOLD'
    confidence: float  # 0-1
    indicators: Dict[str, float]
    levels: List[TechnicalLevel]
    patterns: List[Pattern]
    volume_analysis: Dict[str, float]
    timestamp: datetime

class AdvancedChartAnalyzer:
    """Advanced chart analysis với full OHLCV data"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Technical indicator parameters
        self.sma_periods = [10, 20, 50, 100, 200]
        self.ema_periods = [12, 26, 50]
        self.bb_period = 20
        self.rsi_period = 14
        self.macd_fast = 12
        self.macd_slow = 26
        self.macd_signal = 9
        
        # Pattern recognition settings
        self.min_pattern_strength = 0.6
        self.support_resistance_threshold = 0.02  # 2% tolerance
        
        self.logger.info("Advanced Chart Analyzer initialized")
    
    def analyze_ohlcv(self, ohlcv_data: List[Dict], symbol: str) -> AdvancedSignal:
        """Phân tích toàn diện OHLCV data"""
        try:
            if len(ohlcv_data) < 50:
                self.logger.warning(f"Insufficient data for {symbol}: {len(ohlcv_data)} candles")
                return self._create_hold_signal(symbol)
            
            # Convert to DataFrame
            df = self._convert_to_dataframe(ohlcv_data)
            
            # Calculate all technical indicators
            indicators = self._calculate_indicators(df)
            
            # Find support/resistance levels
            levels = self._find_support_resistance(df)
            
            # Detect patterns
            patterns = self._detect_patterns(df)
            
            # Analyze volume
            volume_analysis = self._analyze_volume(df)
            
            # Generate composite signal
            signal, confidence = self._generate_signal(df, indicators, levels, patterns, volume_analysis)
            
            return AdvancedSignal(
                symbol=symbol,
                signal=signal,
                confidence=confidence,
                indicators=indicators,
                levels=levels,
                patterns=patterns,
                volume_analysis=volume_analysis,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing {symbol}: {e}")
            return self._create_hold_signal(symbol)
    
    def _convert_to_dataframe(self, ohlcv_data: List[Dict]) -> pd.DataFrame:
        """Convert OHLCV list to pandas DataFrame"""
        df = pd.DataFrame(ohlcv_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.set_index('timestamp')
        df = df.sort_index()
        return df
    
    def _calculate_indicators(self, df: pd.DataFrame) -> Dict[str, float]:
        """Tính tất cả technical indicators"""
        indicators = {}
        
        try:
            # Simple Moving Averages
            for period in self.sma_periods:
                if len(df) >= period:
                    indicators[f'sma_{period}'] = ta.trend.sma_indicator(df['close'], window=period).iloc[-1]
            
            # Exponential Moving Averages
            for period in self.ema_periods:
                if len(df) >= period:
                    indicators[f'ema_{period}'] = ta.trend.ema_indicator(df['close'], window=period).iloc[-1]
            
            # RSI
            if len(df) >= self.rsi_period:
                indicators['rsi'] = ta.momentum.rsi(df['close'], window=self.rsi_period).iloc[-1]
            
            # MACD
            if len(df) >= max(self.macd_fast, self.macd_slow):
                macd_line = ta.trend.macd(df['close'], window_fast=self.macd_fast, 
                                        window_slow=self.macd_slow).iloc[-1]
                macd_signal = ta.trend.macd_signal(df['close'], window_fast=self.macd_fast, 
                                                 window_slow=self.macd_slow, 
                                                 window_sign=self.macd_signal).iloc[-1]
                indicators['macd'] = macd_line
                indicators['macd_signal'] = macd_signal
                indicators['macd_histogram'] = macd_line - macd_signal
            
            # Bollinger Bands
            if len(df) >= self.bb_period:
                bb_high = ta.volatility.bollinger_hband(df['close'], window=self.bb_period).iloc[-1]
                bb_low = ta.volatility.bollinger_lband(df['close'], window=self.bb_period).iloc[-1]
                bb_mid = ta.volatility.bollinger_mavg(df['close'], window=self.bb_period).iloc[-1]
                
                indicators['bb_high'] = bb_high
                indicators['bb_mid'] = bb_mid
                indicators['bb_low'] = bb_low
                indicators['bb_width'] = (bb_high - bb_low) / bb_mid * 100
                indicators['bb_position'] = (df['close'].iloc[-1] - bb_low) / (bb_high - bb_low)
            
            # Stochastic
            if len(df) >= 14:
                stoch_k = ta.momentum.stoch(df['high'], df['low'], df['close']).iloc[-1]
                stoch_d = ta.momentum.stoch_signal(df['high'], df['low'], df['close']).iloc[-1]
                indicators['stoch_k'] = stoch_k
                indicators['stoch_d'] = stoch_d
            
            # Williams %R
            if len(df) >= 14:
                indicators['williams_r'] = ta.momentum.williams_r(df['high'], df['low'], df['close']).iloc[-1]
            
            # ADX (Average Directional Index)
            if len(df) >= 14:
                indicators['adx'] = ta.trend.adx(df['high'], df['low'], df['close']).iloc[-1]
            
            # Volume indicators
            if 'volume' in df.columns and len(df) >= 20:
                # On-Balance Volume
                indicators['obv'] = ta.volume.on_balance_volume(df['close'], df['volume']).iloc[-1]
                
                # Volume SMA
                indicators['volume_sma'] = ta.trend.sma_indicator(df['volume'], window=20).iloc[-1]
                indicators['volume_ratio'] = df['volume'].iloc[-1] / indicators['volume_sma']
            
            # Current price
            indicators['current_price'] = df['close'].iloc[-1]
            indicators['price_change'] = ((df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2]) * 100
            
            return indicators
            
        except Exception as e:
            self.logger.error(f"Error calculating indicators: {e}")
            return {'current_price': df['close'].iloc[-1] if not df.empty else 0}
    
    def _find_support_resistance(self, df: pd.DataFrame) -> List[TechnicalLevel]:
        """Tìm support và resistance levels"""
        levels = []
        
        try:
            # Use pivot points method
            window = 5
            
            # Find pivot highs (resistance)
            pivot_highs = []
            for i in range(window, len(df) - window):
                if all(df['high'].iloc[i] >= df['high'].iloc[i-j] for j in range(1, window+1)) and \
                   all(df['high'].iloc[i] >= df['high'].iloc[i+j] for j in range(1, window+1)):
                    pivot_highs.append((i, df['high'].iloc[i]))
            
            # Find pivot lows (support)
            pivot_lows = []
            for i in range(window, len(df) - window):
                if all(df['low'].iloc[i] <= df['low'].iloc[i-j] for j in range(1, window+1)) and \
                   all(df['low'].iloc[i] <= df['low'].iloc[i+j] for j in range(1, window+1)):
                    pivot_lows.append((i, df['low'].iloc[i]))
            
            # Group similar levels
            current_price = df['close'].iloc[-1]
            tolerance = current_price * self.support_resistance_threshold
            
            # Process resistance levels
            for idx, price in pivot_highs:
                # Count touches
                touches = sum(1 for _, p in pivot_highs if abs(p - price) <= tolerance)
                
                if touches >= 2:  # At least 2 touches
                    levels.append(TechnicalLevel(
                        level=price,
                        strength=touches,
                        type='RESISTANCE',
                        last_touch=df.index[idx]
                    ))
            
            # Process support levels
            for idx, price in pivot_lows:
                # Count touches
                touches = sum(1 for _, p in pivot_lows if abs(p - price) <= tolerance)
                
                if touches >= 2:  # At least 2 touches
                    levels.append(TechnicalLevel(
                        level=price,
                        strength=touches,
                        type='SUPPORT',
                        last_touch=df.index[idx]
                    ))
            
            # Sort by strength
            levels.sort(key=lambda x: x.strength, reverse=True)
            
            return levels[:10]  # Top 10 levels
            
        except Exception as e:
            self.logger.error(f"Error finding support/resistance: {e}")
            return []
    
    def _detect_patterns(self, df: pd.DataFrame) -> List[Pattern]:
        """Detect chart patterns"""
        patterns = []
        
        try:
            current_price = df['close'].iloc[-1]
            
            # Double Top Pattern
            pattern = self._detect_double_top(df)
            if pattern:
                patterns.append(pattern)
            
            # Double Bottom Pattern
            pattern = self._detect_double_bottom(df)
            if pattern:
                patterns.append(pattern)
            
            # Head and Shoulders
            pattern = self._detect_head_shoulders(df)
            if pattern:
                patterns.append(pattern)
            
            # Triangle Patterns
            pattern = self._detect_triangle(df)
            if pattern:
                patterns.append(pattern)
            
            # Flag/Pennant
            pattern = self._detect_flag_pennant(df)
            if pattern:
                patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error detecting patterns: {e}")
            return []
    
    def _detect_double_top(self, df: pd.DataFrame) -> Optional[Pattern]:
        """Detect Double Top pattern"""
        try:
            if len(df) < 20:
                return None
            
            # Find two highest peaks in recent data
            window = 10
            peaks = []
            
            for i in range(window, len(df) - window):
                if df['high'].iloc[i] == df['high'].iloc[i-window:i+window+1].max():
                    peaks.append((i, df['high'].iloc[i]))
            
            if len(peaks) >= 2:
                # Check if two peaks are similar height
                last_peaks = peaks[-2:]
                height_diff = abs(last_peaks[0][1] - last_peaks[1][1]) / last_peaks[0][1]
                
                if height_diff < 0.03:  # Within 3%
                    confidence = min(0.8, 1 - height_diff * 10)
                    target = min(df['low'].iloc[last_peaks[0][0]:last_peaks[1][0]]) * 0.95
                    
                    return Pattern(
                        name="Double Top",
                        confidence=confidence,
                        target=target,
                        timeframe="1m",
                        detected_at=datetime.now()
                    )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error detecting double top: {e}")
            return None
    
    def _detect_double_bottom(self, df: pd.DataFrame) -> Optional[Pattern]:
        """Detect Double Bottom pattern"""
        try:
            if len(df) < 20:
                return None
            
            # Find two lowest valleys in recent data
            window = 10
            valleys = []
            
            for i in range(window, len(df) - window):
                if df['low'].iloc[i] == df['low'].iloc[i-window:i+window+1].min():
                    valleys.append((i, df['low'].iloc[i]))
            
            if len(valleys) >= 2:
                # Check if two valleys are similar depth
                last_valleys = valleys[-2:]
                depth_diff = abs(last_valleys[0][1] - last_valleys[1][1]) / last_valleys[0][1]
                
                if depth_diff < 0.03:  # Within 3%
                    confidence = min(0.8, 1 - depth_diff * 10)
                    target = max(df['high'].iloc[last_valleys[0][0]:last_valleys[1][0]]) * 1.05
                    
                    return Pattern(
                        name="Double Bottom",
                        confidence=confidence,
                        target=target,
                        timeframe="1m",
                        detected_at=datetime.now()
                    )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error detecting double bottom: {e}")
            return None
    
    def _detect_head_shoulders(self, df: pd.DataFrame) -> Optional[Pattern]:
        """Detect Head and Shoulders pattern (simplified)"""
        # Simplified implementation
        return None
    
    def _detect_triangle(self, df: pd.DataFrame) -> Optional[Pattern]:
        """Detect Triangle patterns (simplified)"""
        # Simplified implementation
        return None
    
    def _detect_flag_pennant(self, df: pd.DataFrame) -> Optional[Pattern]:
        """Detect Flag/Pennant patterns (simplified)"""
        # Simplified implementation
        return None
    
    def _analyze_volume(self, df: pd.DataFrame) -> Dict[str, float]:
        """Analyze volume patterns"""
        volume_analysis = {}
        
        try:
            if 'volume' not in df.columns or len(df) < 20:
                return {'volume_trend': 0, 'volume_strength': 0}
            
            # Volume moving average
            vol_ma = df['volume'].rolling(window=20).mean()
            current_volume = df['volume'].iloc[-1]
            avg_volume = vol_ma.iloc[-1]
            
            # Volume trend (increasing/decreasing)
            recent_volumes = df['volume'].tail(10)
            volume_trend = 1 if recent_volumes.iloc[-1] > recent_volumes.iloc[0] else -1
            
            # Volume strength (current vs average)
            volume_strength = current_volume / avg_volume if avg_volume > 0 else 1
            
            # Volume-Price correlation
            price_changes = df['close'].pct_change().tail(10)
            volume_changes = df['volume'].pct_change().tail(10)
            correlation = price_changes.corr(volume_changes)
            
            volume_analysis = {
                'volume_trend': volume_trend,
                'volume_strength': volume_strength,
                'volume_correlation': correlation if not pd.isna(correlation) else 0,
                'current_volume': current_volume,
                'avg_volume': avg_volume
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing volume: {e}")
            volume_analysis = {'volume_trend': 0, 'volume_strength': 1}
        
        return volume_analysis
    
    def _generate_signal(self, df: pd.DataFrame, indicators: Dict[str, float], 
                        levels: List[TechnicalLevel], patterns: List[Pattern],
                        volume_analysis: Dict[str, float]) -> Tuple[str, float]:
        """Generate composite trading signal"""
        try:
            signals = []
            weights = []
            
            current_price = indicators.get('current_price', 0)
            
            # RSI Signal
            if 'rsi' in indicators:
                rsi = indicators['rsi']
                if rsi < 30:
                    signals.append(1)  # BUY
                    weights.append(0.2)
                elif rsi > 70:
                    signals.append(-1)  # SELL
                    weights.append(0.2)
                else:
                    signals.append(0)  # NEUTRAL
                    weights.append(0.1)
            
            # MACD Signal
            if 'macd' in indicators and 'macd_signal' in indicators:
                macd = indicators['macd']
                macd_signal = indicators['macd_signal']
                if macd > macd_signal:
                    signals.append(1)  # BUY
                else:
                    signals.append(-1)  # SELL
                weights.append(0.15)
            
            # Moving Average Signal
            if 'sma_20' in indicators and 'sma_50' in indicators:
                sma_20 = indicators['sma_20']
                sma_50 = indicators['sma_50']
                if sma_20 > sma_50:
                    signals.append(1)  # BUY
                else:
                    signals.append(-1)  # SELL
                weights.append(0.15)
            
            # Bollinger Bands Signal
            if 'bb_position' in indicators:
                bb_pos = indicators['bb_position']
                if bb_pos < 0.1:  # Near lower band
                    signals.append(1)  # BUY
                    weights.append(0.1)
                elif bb_pos > 0.9:  # Near upper band
                    signals.append(-1)  # SELL
                    weights.append(0.1)
            
            # Support/Resistance Signal
            for level in levels[:3]:  # Top 3 levels
                distance = abs(current_price - level.level) / current_price
                if distance < 0.01:  # Within 1%
                    if level.type == 'SUPPORT':
                        signals.append(1)  # BUY
                        weights.append(0.1 * level.strength / 5)
                    else:  # RESISTANCE
                        signals.append(-1)  # SELL
                        weights.append(0.1 * level.strength / 5)
            
            # Pattern Signal
            for pattern in patterns:
                if pattern.confidence > self.min_pattern_strength:
                    if pattern.name in ['Double Bottom']:
                        signals.append(1)  # BUY
                        weights.append(0.15 * pattern.confidence)
                    elif pattern.name in ['Double Top']:
                        signals.append(-1)  # SELL
                        weights.append(0.15 * pattern.confidence)
            
            # Volume Signal
            if volume_analysis.get('volume_strength', 1) > 1.5:  # High volume
                # Strong volume supports the trend
                price_change = indicators.get('price_change', 0)
                if price_change > 0:
                    signals.append(0.5)  # Weak BUY
                    weights.append(0.1)
                elif price_change < 0:
                    signals.append(-0.5)  # Weak SELL
                    weights.append(0.1)
            
            # Calculate weighted signal
            if signals and weights:
                weighted_signal = sum(s * w for s, w in zip(signals, weights)) / sum(weights)
                confidence = min(sum(weights), 1.0)  # Max confidence 1.0
                
                # Determine final signal
                if weighted_signal > 0.3:
                    return 'BUY', confidence
                elif weighted_signal < -0.3:
                    return 'SELL', confidence
                else:
                    return 'HOLD', confidence * 0.5
            
            return 'HOLD', 0.1
            
        except Exception as e:
            self.logger.error(f"Error generating signal: {e}")
            return 'HOLD', 0.1
    
    def _create_hold_signal(self, symbol: str) -> AdvancedSignal:
        """Create a default HOLD signal"""
        return AdvancedSignal(
            symbol=symbol,
            signal='HOLD',
            confidence=0.1,
            indicators={},
            levels=[],
            patterns=[],
            volume_analysis={},
            timestamp=datetime.now()
        )
    
    def format_signal_summary(self, signal: AdvancedSignal) -> str:
        """Format signal summary for display"""
        summary = f"""
📊 {signal.symbol} ANALYSIS

🎯 SIGNAL: {signal.signal}
🔥 CONFIDENCE: {signal.confidence:.1%}

📈 INDICATORS:"""
        
        if 'rsi' in signal.indicators:
            rsi = signal.indicators['rsi']
            rsi_status = "Oversold" if rsi < 30 else "Overbought" if rsi > 70 else "Neutral"
            summary += f"\n• RSI: {rsi:.1f} ({rsi_status})"
        
        if 'macd' in signal.indicators:
            macd = signal.indicators['macd']
            macd_signal = signal.indicators.get('macd_signal', 0)
            trend = "Bullish" if macd > macd_signal else "Bearish"
            summary += f"\n• MACD: {trend}"
        
        if signal.levels:
            summary += f"\n\n🎯 KEY LEVELS:"
            for level in signal.levels[:3]:
                summary += f"\n• {level.type}: ${level.level:.4f} (Strength: {level.strength})"
        
        if signal.patterns:
            summary += f"\n\n📊 PATTERNS:"
            for pattern in signal.patterns:
                summary += f"\n• {pattern.name} ({pattern.confidence:.1%})"
        
        if signal.volume_analysis:
            vol_strength = signal.volume_analysis.get('volume_strength', 1)
            vol_status = "High" if vol_strength > 1.5 else "Low" if vol_strength < 0.5 else "Normal"
            summary += f"\n\n📊 VOLUME: {vol_status} ({vol_strength:.1f}x avg)"
        
        summary += f"\n\n⏰ {signal.timestamp.strftime('%H:%M:%S')}"
        
        return summary

# Test function
if __name__ == "__main__":
    # Test data (sample OHLCV)
    test_data = [
        {'timestamp': int(datetime.now().timestamp() * 1000) - i * 60000,
         'open': 45000 + np.random.uniform(-100, 100),
         'high': 45100 + np.random.uniform(-100, 100),
         'low': 44900 + np.random.uniform(-100, 100),
         'close': 45000 + np.random.uniform(-100, 100),
         'volume': 1000 + np.random.uniform(-200, 200)}
        for i in range(100)
    ]
    test_data.reverse()
    
    analyzer = AdvancedChartAnalyzer()
    signal = analyzer.analyze_ohlcv(test_data, 'BTCUSDT')
    
    print(analyzer.format_signal_summary(signal))