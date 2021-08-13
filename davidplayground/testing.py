from davidplayground.datasets import CoinDataset
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from pandas.plotting import register_matplotlib_converters
from davidplayground.utils import *

start = datetime(year=2021,month=1,day=1,hour=0,minute=0,second=0)
end = datetime(year=2021,month=8,day=7,hour=0,minute=0,second=0)
cd = CoinDataset(name='ALGO')
cd.add_treatment(add_sma, kwargs={'dt':60, 'cols':['close']})
cd.add_treatment(add_sma, kwargs={'dt':120, 'cols':['close']})
df = cd.sample_between(start, end)

register_matplotlib_converters()
sns.set()
plt.title("ALGO Closing Price w/ SMA")
plt.plot(df['time'], df['close'], c='#333333', linewidth=0.5, label='close')
plt.plot(df['time'], df['close_SMA60'], c='#882222', linewidth=0.7, label='SMA_60')
plt.plot(df['time'], df['close_SMA120'], c='#222288', linewidth=0.7, label='SMA_120')
plt.xticks(rotation=90)
plt.tight_layout()
plt.legend()
plt.gcf().set_size_inches((12.0,6.0))
plt.savefig('test.png')