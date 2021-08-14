import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
from datetime import timedelta, datetime

DEFAULT_STYLE = {
    'downcolor': 'r',
    'upcolor': 'g'
}

def candlestick(ohlc, ax=None, style={}):
    '''
    Create a candlestick plot from the provided dataset
    :param ohlc: Dataset with OHLC columns
    :param ax: Matplotlib axes
    :param style: Style modifications
    '''
    if not ax:
        ax = plt.gca()
    if not all([n in ohlc.columns for n in ['open', 'high', 'low', 'close']]):
        raise Exception("OHLC argument must have OHLC columns.")
    for s in style:
        DEFAULT_STYLE[s] = style[s]
    dt = ohlc.loc[1,'time'] - ohlc.loc[0,'time']
    w, sw = (0.75, 0.125)
    for i in range(len(ohlc)):
        o, h, l, c = ohlc.loc[i,'open'], ohlc.loc[i,'high'], ohlc.loc[i,'low'], ohlc.loc[i,'close']
        t = ohlc.loc[i,'time']
        down = c < o
        color = DEFAULT_STYLE['upcolor'] if not down else DEFAULT_STYLE['downcolor']
        candle = Rectangle((t - dt*w*0.5, c), w*dt, o-c, facecolor=color, alpha=0.5, edgecolor='None')
        wick = Line2D([t, t], [l, h], marker='None', color=color, alpha=0.5)

        ax.add_patch(candle)
        ax.add_line(wick)
