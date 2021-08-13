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

def add_sma(df, dt=2, cols=['open', 'close', 'high', 'low']):
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

def add_ema(df, dt=2, smoothing=2.0,cols=['open', 'close', 'high', 'low']):
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
        ema_col = [None for _ in range(dt)]
        ema_name = col + '_ema' + str(dt)
        for index, row in df.iterrows():
            if index < dt:
                continue
            ema1 = row[col]*(smoothing/(1.0 + dt)) + ema0*(1 - smoothing/(1.0 + dt))
            ema_col.append(ema1)
            ema0 = ema1
        df[ema_name] = ema_col
    return df

def add_bollinger(df, dt=2, K=2.0, middle='sma'):
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