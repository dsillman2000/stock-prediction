import pandas as pd
from datetime import datetime, date, timedelta

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
    A treatment function or adding simple moving average(s) as columns
    to the dataset.
    :param df: Dataframe dataset
    :param dt: Size of window for SMA
    :param cols: Which columns to compute SMA for
    :return: treated dataset
    '''
    for col in cols:
        sma_name = col + '_SMA' + str(dt)
        sma_col = df[col].rolling(window=dt).mean()
        df[sma_name] = sma_col
    return df
