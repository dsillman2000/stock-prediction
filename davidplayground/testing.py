from davidplayground.datasets import *
from datetime import datetime
from davidplayground.plotting import *
import matplotlib.pyplot as plt
import seaborn as sns
from pandas.plotting import register_matplotlib_converters
from davidplayground.utils import *

# start = datetime(year=2021,month=1,day=1,hour=0,minute=0,second=0)
# end = datetime(year=2021,month=8,day=7,hour=0,minute=0,second=0)
# cd = CoinDataset(name='ALGO')
# cd.add_treatment(add_ema, kwargs={'dt':60, 'smoothing':2.0, 'cols':['close']})
# cd.add_treatment(add_macd, kwargs={'a':60, 'b':120, 'c':30, 'middle':'ema'})
# df = cd.sample_between(start, end, days=7)
#
register_matplotlib_converters()
# sns.set()
# fig, (ax0, ax1) = plt.subplots(2, 1, sharex=True)
# fig.suptitle("ALGO Market Indicators")
# ax0.plot(df['time'], df['close'], c='#333333', linewidth=0.7)
# ax0.plot(df['time'], df['close_ema60'], c='#000099', linewidth=0.7)
# ax1.plot(df['time'], df['macd'], c='#882222', linewidth=0.7)
# ax1.plot(df['time'], df['macd_signal'], c='#228822', linewidth=0.7)
# ax1.plot(df['time'], df['macd_hist'], c='#222288', linewidth=0.7)
# plt.xticks(rotation=90)
# plt.show()

sns.set()
fig, ax = plt.subplots()
W = WienerDataset(s0=1.0, nsigma=0.1)
W.add_treatment(add_ema, kwargs={'dt':30, 'smoothing':2.0, 'cols': ['close']})
W.add_treatment(add_ema, kwargs={'dt':120, 'smoothing':2.0, 'cols': ['close']})
X = W.generate(hours=24, seed=None)
ax.plot(X['time'], X['close'], c='#555555', linewidth=0.7, label='Close')
ax.plot(X['time'], X['close_ema30'], c='#555599', linewidth=0.7, label='EMA30')
ax.plot(X['time'], X['close_ema120'], c='#995555', linewidth=0.7, label='EMA120')
trade_times = []
print(X.loc[0, 'time'])
for i in range(len(X['time'])):
    if X.loc[i, 'time'].minute % 60 == 0:
        trade_times.append(X.loc[i, 'time'])
ax.vlines(trade_times, ymin=ax.get_ylim()[0], ymax=ax.get_ylim()[1], linestyles='dotted', linewidth=0.7)
plt.xticks(rotation=90)
plt.show()
