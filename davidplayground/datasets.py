import numpy as np
import pandas as pd
from cbpro import PublicClient
from davidplayground.utils import *

class WienerDataset:
    def __init__(self, s0=1.0, nmu=0.0, nsigma=1.0):
        '''
        Initializes a Wiener process generator to use as a toy dataset for
        algorithms.

        :param s0: Value of coin at initial time t0
        :param nmu: Mean of normal increments in Wiener process
        :param nsigma: Stdev of normal increments in Wiener process
        '''
        self.s0 = s0
        self.nmu = nmu
        self.nsigma = nsigma
        self.treatments = []
        self.treatment_args = []

    def add_treatment(self, treatment, kwargs=None):
        '''
        Append a new treatment function to the post-processor for the dataset
        :param treatment: treatment function with first argument dataframe and
        return value dataframe.
        :param args: additional arguments to the treatment function
        '''
        if kwargs:
            self.treatment_args.append(kwargs)
        self.treatments.append(treatment)

    def generate(self, hours=1, seed=None, raw=False):
        '''
        Generates a Wiener process with the specified seed. Returns a DataFrame.

        :param n: Amount of datapoints to generate
        :param seed: Seed for random generation
        :return: DataFrame of data points.
        '''
        if seed is not None:
            np.random.seed(seed)
        st = self.s0
        t = datetime.now() - timedelta(hours=hours)
        n = hours * 60
        rows = []
        for i in range(n):
            newrow = {'time':t, 'close': st}
            st += np.random.normal(self.nmu, self.nsigma ** 2)
            t += timedelta(seconds=60)
            if st <= 0.0:
                st = 0.0001
            rows.append(newrow)
        df = pd.DataFrame(rows)
        if not raw:
            for t in range(len(self.treatments)):
                treatment = self.treatments[t]
                try:
                    args = self.treatment_args[t]
                    if args:
                        df = treatment(df, **args)
                    else:
                        df = treatment(df)
                except Exception as err:
                    print(f"FAILED TO APPLY TREATMENT: {treatment.__name__}")
                    raise err
        return df

class CoinDataset:
    def __init__(self, name='BTC'):
        '''
        Creates a dataset provider for the cryptocurrency with ticker `name`

        :param name: Crypto ticker
        '''
        self.name = name
        self.client = PublicClient()
        self.treatments = [convert_timestamps]
        self.treatment_args = [None]

    def add_treatment(self, treatment, kwargs=None):
        '''
        Append a new treatment function to the post-processor for the dataset
        :param treatment: treatment function with first argument dataframe and
        return value dataframe.
        :param args: additional arguments to the treatment function
        '''
        if kwargs:
            self.treatment_args.append(kwargs)
        self.treatments.append(treatment)

    def get(self, start, end, granularity=60, raw=False):
        '''
        Queries historical price data from cbpro api between ISO-format times
        `start` and `end` with the second-granularity provided by `granularity`.

        :param start: start date-time in ISO-8601
        :param end: end date-time in ISO-8601
        :param granularity: data granularity in seconds
        :param raw: whether or not to skip treatments on the dataset
        :return: dataframe containing the requested data
        '''
        df = pd.DataFrame(columns=['time', 'open', 'close', 'high', 'low', 'volume'])
        max_queries = 200
        curtime = datetime.fromisoformat(start)
        nexttime = curtime + timedelta(seconds=granularity*max_queries)
        endtime = datetime.fromisoformat(end)
        while curtime < endtime:
            if nexttime > endtime:
                nexttime = endtime
            query = self.client.get_product_historic_rates(f'{self.name}-USD', start=curtime.isoformat(),
                                                   end=nexttime.isoformat(), granularity=granularity)
            df = df.append(cbquery2df(query), sort=True)
            curtime = nexttime
            nexttime += timedelta(seconds=granularity*max_queries)

        if not raw:
            for t in range(len(self.treatments)):
                treatment = self.treatments[t]
                try:
                    args = self.treatment_args[t]
                    if args:
                        df = treatment(df, **args)
                    else:
                        df = treatment(df)
                except Exception as err:
                    print(f"FAILED TO APPLY TREATMENT: {treatment.__name__}")
                    raise err
        return df

    def sample_between(self, start, end, days=0, hours=0, granularity=60):
        '''
        Sample `days` worth of data at random from between start and end datetimes.
        :param start: early bound datetime
        :param end: late bound datetime
        :param days: number of days' worth of data to sample
        :param hours: number of hours' worth of data to sample
        :param granularity: granularity for data
        :return: dataframe dataset
        '''
        days_between = (end - start).days
        rand_day = np.random.randint(0, days_between)
        rand_sdate = start + timedelta(days=rand_day)
        rand_edate = rand_sdate + timedelta(days=days, hours=hours)
        result = self.get(rand_sdate.isoformat(), rand_edate.isoformat(), granularity=granularity)
        return result
