import pandas as pd
import numpy as np

def detect_v_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect V-Top and V-Bottom patterns (sharp reversals)
    """
    df = self.normalize_dataframe(df)
    patterns = []
    
    # Calculate price velocity
    price_velocity = df['close'].diff().abs()
    high_velocity_threshold = price_velocity.quantile(0.9)
    
    for i in range(10, len(df) - 10):
        # V-Top pattern
        if df['high'].iloc[i] == df['high'].iloc[i-10:i+11].max():
            # Check for sharp rise and fall
            left_velocity = price_velocity.iloc[i-5:i].mean()
            right_velocity = price_velocity.iloc[i:i+5].mean()
            
            if (left_velocity > high_velocity_threshold * 0.7 and
                right_velocity > high_velocity_threshold * 0.7):
                
                # Ensure it's actually a peak
                if (df['close'].iloc[i-5] < df['close'].iloc[i] and
                    df['close'].iloc[i+5] < df['close'].iloc[i]):
                    
                    patterns.append({
                        'pattern': 'v_top',
                        'type': 'bearish',
                        'start': df.index[i-5],
                        'peak': df.index[i],
                        'end': df.index[i+5],
                        'peak_price': df['high'].iloc[i],
                        'sharpness': (left_velocity + right_velocity) / 2
                    })
        
        # V-Bottom pattern
        elif df['low'].iloc[i] == df['low'].iloc[i-10:i+11].min():
            # Check for sharp fall and rise
            left_velocity = price_velocity.iloc[i-5:i].mean()
            right_velocity = price_velocity.iloc[i:i+5].mean()
            
            if (left_velocity > high_velocity_threshold * 0.7 and
                right_velocity > high_velocity_threshold * 0.7):
                
                # Ensure it's actually a trough
                if (df['close'].iloc[i-5] > df['close'].iloc[i] and
                    df['close'].iloc[i+5] > df['close'].iloc[i]):
                    
                    patterns.append({
                        'pattern': 'v_bottom',
                        'type': 'bullish',
                        'start': df.index[i-5],
                        'trough': df.index[i],
                        'end': df.index[i+5],
                        'trough_price': df['low'].iloc[i],
                        'sharpness': (left_velocity + right_velocity) / 2
                    })
    
    return pd.DataFrame(patterns)