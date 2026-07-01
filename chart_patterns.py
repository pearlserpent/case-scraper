import pandas as pd
import numpy as np


def detect_v_patterns(df: pd.DataFrame, window: int = 5, lookback: int = 10) -> pd.DataFrame:
    """
    Detect V-Top and V-Bottom patterns (sharp reversals).
    """
    patterns = []
    price_velocity = df['close'].diff().abs()
    high_velocity_threshold = price_velocity.quantile(0.9)

    for i in range(lookback, len(df) - lookback):
        window_high = df['high'].iloc[i - lookback:i + lookback + 1]
        window_low = df['low'].iloc[i - lookback:i + lookback + 1]

        is_local_high = df['high'].iloc[i] == window_high.max()
        is_local_low = df['low'].iloc[i] == window_low.min()

        left_velocity = price_velocity.iloc[i - window:i].mean()
        right_velocity = price_velocity.iloc[i:i + window].mean()
        sharp_enough = (
            left_velocity > high_velocity_threshold * 0.7
            and right_velocity > high_velocity_threshold * 0.7
        )

        if is_local_high and sharp_enough:
            # confirm using the SAME series (high) used to find the extremum
            if (df['high'].iloc[i - window] < df['high'].iloc[i] and
                    df['high'].iloc[i + window] < df['high'].iloc[i]):
                patterns.append({
                    'pattern': 'v_top',
                    'type': 'bearish',
                    'start': df.index[i - window],
                    'peak': df.index[i],
                    'end': df.index[i + window],
                    'peak_price': df['high'].iloc[i],
                    'sharpness': (left_velocity + right_velocity) / 2,
                })
        elif is_local_low and sharp_enough:
            if (df['low'].iloc[i - window] > df['low'].iloc[i] and
                    df['low'].iloc[i + window] > df['low'].iloc[i]):
                patterns.append({
                    'pattern': 'v_bottom',
                    'type': 'bullish',
                    'start': df.index[i - window],
                    'trough': df.index[i],
                    'end': df.index[i + window],
                    'trough_price': df['low'].iloc[i],
                    'sharpness': (left_velocity + right_velocity) / 2,
                })

    return pd.DataFrame(patterns)


def detect_rectangles(df: pd.DataFrame, min_rectangle_size: int = 20,
                       min_pattern_bars: int = 20) -> pd.DataFrame:
    """
    Detect Rectangle patterns (horizontal channels).
    """
    patterns = []
    size = max(min_rectangle_size, min_pattern_bars)

    for i in range(size, len(df)):
        w = df.iloc[i - size:i]

        resistance_level = w['high'].quantile(0.95)
        support_level = w['low'].quantile(0.05)

        touches_resistance = (w['high'] >= resistance_level * 0.998).sum()
        touches_support = (w['low'] <= support_level * 1.002).sum()

        if (touches_resistance >= 2 and touches_support >= 2 and
                (resistance_level - support_level) / support_level > 0.02):

            within_rectangle = ((w['low'] >= support_level * 0.995) &
                                 (w['high'] <= resistance_level * 1.005)).sum()

            if within_rectangle / len(w) > 0.8:
                patterns.append({
                    'pattern': 'rectangle',
                    'type': 'neutral',
                    'start': w.index[0],
                    'end': w.index[-1],
                    'resistance_level': resistance_level,
                    'support_level': support_level,
                    'height': resistance_level - support_level,
                    'resistance_touches': touches_resistance,
                    'support_touches': touches_support,
                })

    return pd.DataFrame(patterns)