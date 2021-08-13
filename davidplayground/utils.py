import pandas as pd
from datetime import datetime, date, timedelta
import numpy as np

def cbquery2df(query):
    '''
    Converts a list-like query result from cbpro api into a dataframe.
    :param query: returned query from cbpro api
    :return: dataframe representation of the query
    '''
    row_format = ['time', 'low', 'high', 'open', 'close', 'volume']
    rows = []
    for qi in query:
        items = dict(zip(row_format, qi))
        rows.append(items)
    return pd.DataFrame(rows)

def convert_timestamps(df):
    '''
    A treatment function for converting ordinal timestamps to datetimes.
    :param df: DataFrame dataset
    :return: treated dataset
    '''
    def subfunc(row):
        timedata = row['time']
        row['time'] = datetime.fromtimestamp(timedata)
        return row
    df = df.apply(subfunc, axis=1)
    df = df.sort_values('time', ascending=True)
    df = df.reset_index(drop=True)
    return df

def add_sma(df, dt=2, cols=['close']):
    '''
    A treatment function for adding simple moving average(s) as columns
    to the dataset.
    :param df: Dataframe dataset
    :param dt: Size of window for SMA
    :param cols: Which columns to compute SMA for
    :return: treated dataset
    '''
    for col in cols:
        sma_name = col + '_sma' + str(dt)
        sma_col = df[col].rolling(window=dt).mean()
        df[sma_name] = sma_col
    return df

def add_ema(df, dt=2, smoothing=2.0,cols=['close']):
    '''
    A treatment function for adding exponential moving average(s) as columns
    to the dataset.
    :param df: Dataframe dataset
    :param dt: Size of window for EMA
    :param cols: Which columns to compute EMA for
    :return: treated dataset
    '''
    for col in cols:
        ema0 = df[col][:dt].mean()
        if pd.isna(ema0):
            ema0 = 0.0
        ema_col = [None for _ in range(dt)]
        ema_name = col + '_ema' + str(dt)
        for index, row in df.iterrows():
            if index < dt:
                continue
            elif pd.isna(row[col]):
                ema_col.append(None)
                continue
            ema1 = row[col]*(smoothing/(1.0 + dt)) + ema0*(1 - smoothing/(1.0 + dt))
            ema_col.append(ema1)
            ema0 = ema1
        print(len(df),'vs',len(ema_col))
        df[ema_name] = ema_col
    return df

def add_bollinger(df, dt=2, K=2.0, middle='sma'):
    '''
    A treatment function for adding bollinger bands as columns
    to the dataset.
    :param df: Dataframe dataset
    :param dt: Size of window for BB
    :param K: Number of stdev's to adjust by
    :param middle: MA method to use
    :return: treated dataset
    '''
    if middle == 'sma':
        df = add_sma(df, dt=dt, cols=['close'])
    elif middle == 'ema':
        df = add_ema(df, dt=dt, smoothing=2.0, cols=['close'])
    else:
        raise Exception('Bollinger Bands require middle method to be in ["sma", "ema"]')
    stdev = df['close'].rolling(window=dt).std()
    df['bb_upper'] = stdev * K + df[f'close_{middle}{dt}']
    df['bb_lower'] = -stdev * K + df[f'close_{middle}{dt}']
    return df

def add_rsi(df, dt=2, middle='ema'):
    '''
    A treatment function for adding the relative-strength-index as
    a column to the dataset.
    :param df: Dataframe dataset
    :param dt: Window size
    :param middle: MA method
    :return: treated dataset
    '''
    if middle not in ['sma', 'ema']:
        raise Exception('RSI mean method must be either "sma" or "ema"')
    U = []
    D = []
    for i in range(len(df)):
        if i == 0:
            U.append(0)
            D.append(0)
            continue
        p0 = df.loc[i - 1]['close']
        p1 = df.loc[i]['close']
        U.append(max(p1 - p0, 0))
        D.append(max(p0 - p1, 0))
    dfc = df.copy()
    dfc['U'] = U
    dfc['D'] = D
    if middle == 'sma':
        dfc = add_sma(dfc, dt=dt, cols=['U', 'D'])
    elif middle == 'ema':
        dfc = add_ema(dfc, dt=dt, cols=['U', 'D'], smoothing=2.0)
    RS = dfc[f'U_{middle}{dt}'] / dfc[f'D_{middle}{dt}']
    RSI = 100.0 - 100.0/(1.0 + RS)
    df[f'rsi{dt}'] = RSI
    return df

def add_macd(df, a=12, b=26, c=9, middle='ema'):
    '''
    Treatment function for adding moving-average-convergence-divergence
    indicator as a column to the dataset
    :param df: DataFrame dataset
    :param a: Characteristic time a
    :param b: Characteristic time b
    :param c: Characteristic time c
    :param middle: MA method
    :return: treated dataset
    '''
    if middle not in ['ema', 'sma']:
        raise Exception("MA method 'middle' must be in ['sma', 'ema']")
    a_name = f"close_{middle}{a}"
    b_name = f"close_{middle}{b}"
    c_name = f"macd_{middle}{c}"
    if middle == 'sma':
        df = add_sma(df, dt=a, cols=['close'])
        df = add_sma(df, dt=b, cols=['close'])
        macd = df[a_name] - df[b_name]
        df['macd'] = macd
        df = add_sma(df, dt=c, cols=['macd'])
        df['macd_signal'] = df[c_name].copy()
        df['macd_hist'] = df['macd'] - df['macd_signal']
    elif middle == 'ema':
        df = add_ema(df, dt=a, smoothing=2.0, cols=['close'])
        df = add_ema(df, dt=b, smoothing=2.0, cols=['close'])
        macd = df[a_name] - df[b_name]
        df['macd'] = macd
        df = add_ema(df, dt=c, smoothing=2.0, cols=['macd'])
        df['macd_signal'] = df[c_name].copy()
        print(df['macd_signal'])
        df['macd_hist'] = df['macd'] - df['macd_signal']
    return df
