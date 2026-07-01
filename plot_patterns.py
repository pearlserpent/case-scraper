"""
Plot OHLC candlesticks with V-pattern and rectangle overlays.

Usage:
    v_patterns = detect_v_patterns(df)
    rectangles = detect_rectangles(df)
    plot_patterns(df, v_patterns, rectangles)
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import pandas as pd
import numpy as np


def _plot_candlesticks(ax, df: pd.DataFrame, width: float = 0.6):
    """Draw simple OHLC candlesticks. df.index must be datetime-like or numeric."""
    x = np.arange(len(df))
    up = df['close'] >= df['open']

    # wicks
    ax.vlines(x, df['low'], df['high'], color='black', linewidth=0.8, zorder=2)

    # bodies
    body_bottom = np.where(up, df['open'], df['close'])
    body_height = (df['close'] - df['open']).abs().clip(lower=1e-9)
    colors = np.where(up, '#26a69a', '#ef5350')

    ax.bar(x, body_height, bottom=body_bottom, width=width,
           color=colors, edgecolor='black', linewidth=0.4, zorder=3)

    return x


def plot_patterns(df: pd.DataFrame, v_patterns: pd.DataFrame = None,
                   rectangles: pd.DataFrame = None, figsize=(16, 8),
                   title: str = 'Price with Detected Patterns'):
    df = df.reset_index(drop=False)
    idx_col = df.columns[0]  # original index (e.g. datetime), now a column
    pos_of = {ts: i for i, ts in enumerate(df[idx_col])}

    fig, ax = plt.subplots(figsize=figsize)
    x = _plot_candlesticks(ax, df)

    # --- V-tops / V-bottoms ---
    if v_patterns is not None and not v_patterns.empty:
        for _, row in v_patterns.iterrows():
            if row['pattern'] == 'v_top':
                p = pos_of[row['peak']]
                ax.scatter(p, row['peak_price'] * 1.01, marker='v', s=140,
                           color='red', zorder=5, label='V-Top')
                ax.annotate('V-Top', (p, row['peak_price'] * 1.015),
                            ha='center', fontsize=8, color='red')
            elif row['pattern'] == 'v_bottom':
                p = pos_of[row['trough']]
                ax.scatter(p, row['trough_price'] * 0.99, marker='^', s=140,
                           color='green', zorder=5, label='V-Bottom')
                ax.annotate('V-Bottom', (p, row['trough_price'] * 0.985),
                            ha='center', fontsize=8, color='green', va='top')

    # --- Rectangles ---
    if rectangles is not None and not rectangles.empty:
        for _, row in rectangles.iterrows():
            x0 = pos_of[row['start']]
            x1 = pos_of[row['end']]
            rect = Rectangle(
                (x0, row['support_level']),
                width=(x1 - x0),
                height=row['height'],
                linewidth=1.2, edgecolor='blue', facecolor='blue',
                alpha=0.08, zorder=1,
            )
            ax.add_patch(rect)

    # x-axis labels: show a subset of original index values as ticks
    step = max(1, len(df) // 12)
    tick_pos = list(range(0, len(df), step))
    ax.set_xticks(tick_pos)
    ax.set_xticklabels([str(df[idx_col].iloc[i])[:10] for i in tick_pos],
                        rotation=45, ha='right')

    # dedupe legend entries (scatter calls repeat labels)
    handles, labels = ax.get_legend_handles_labels()
    seen = dict(zip(labels, handles))
    if seen:
        ax.legend(seen.values(), seen.keys(), loc='upper left')

    ax.set_title(title)
    ax.set_ylabel('Price')
    ax.margins(x=0.01)
    fig.tight_layout()
    return fig, ax


if __name__ == '__main__':
    # quick smoke test with synthetic data
    rng = pd.date_range('2024-01-01', periods=200, freq='D')
    np.random.seed(0)
    close = 100 + np.cumsum(np.random.randn(200))
    df = pd.DataFrame({
        'open': close + np.random.randn(200) * 0.3,
        'high': close + np.abs(np.random.randn(200)) * 1.2,
        'low': close - np.abs(np.random.randn(200)) * 1.2,
        'close': close,
    }, index=rng)

    fig, ax = plot_patterns(df)
    plt.show()