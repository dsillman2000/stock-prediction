import cbpro, time

import numpy as np
import pandas as pd

from datetime import datetime, timedelta
from matplotlib import pyplot as plt

import tensorflow as tf
import tensorflow.keras as keras

from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, LSTM
from tensorflow.keras.optimizers import Adam
from tensorflow.keras import initializers

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

%matplotlib inline

pubclient = cbpro.PublicClient()
authclient = cbpro.AuthenticatedClient(
    key="36ffa4ceb691e6a40ff7293046dfed67", 
    b64secret="dU4s+DpDUJjeQZjA7rgU7E+NXcHmpb7spUArdNdTtwDcbRJM4S+bIgwNOktsyAk89EIwz1/9prOfDaGe1yJUTw==", 
    passphrase="0w1tih56rnvr", 
    api_url="https://api-public.sandbox.pro.coinbase.com"
)

class AlgoBot:

    "Name of the game -- strategic asset allocation"

    def __init__(self, product, initEquity):

        self.MAX_TRADING_SESSION: int = 192 # in hours, this is 8 days
        self.product = product

        self.data = None    # this best practice?
        self._loadData()
        self.lookback = 96

        self.initEquity = initEquity    # to monitor progress this should be remembered and not changed
        self.cash = initEquity
        self.unrealized_pl = 0
        self.netWorth = np.zeros(shape=self.MAX_TRADING_SESSION, dtype=np.float16)
        self.gNetWorth = []
        self.transactions = np.zeros(shape=self.MAX_TRADING_SESSION, dtype=object)
        self.gTransactions = []
        self.winRate = np.nan
        self.positionHeld = False

        self.commission = 0.005     # equivalent to 0.5% commission on every trade
        self.trailingStopRisk = 0.90    # ?

        # Kelly Criterion starting parameters
        self.W = 0.3
        self.R = 3.0

    def reset(self):
        self.gNetWorth.extend(self.netWorth)
        self.gTransactions.extend(self.transactions)
        self.netWorth = np.zeros(shape=self.MAX_TRADING_SESSION, dtype=np.float16)
        self.transactions = np.zeros(shape=self.MAX_TRADING_SESSION, dtype=object)

    def runSim(self):
        # 1. Initialize agent, load data, and train network.
        for i in range(self.MAX_TRADING_SESSION // 6):
            self.data.loc[len(self.data)] = self.getDataNow()
            self._addTechnicals()   # recompute technicals
            # 2. Make a prediction every 6 (?) hrs
            #   - at the start of each step, record net worth from previous transaction
            signal = None # return value of predict()
            if signal > 0:
                order = self.buy()
            elif signal < 0:
                order = self.sell()
            # add price to transaction entry for logging purposes
            order['price'] = self.getPrice()
            self.transactions[i] = order
            self.netWorth[i] = self.getNetWorth()

            # update KC parameters and winrate

            time.sleep(12 * 60 * 60)
        # 3. Track performance at every prediction, and 
        #   consider aggregating performance data by day
        #   as additional training data
        return

    def buy(self):
        '''
        Execute buy order
        '''
        price = self.getPrice()
        if self.cash > 0:
            position_size = self.computeKC() * self.cash
            order = authclient.place_market_order(self.product, 'buy', funds=position_size, overdraft_enabled=False)
            fees = order['fill_fees']
            self.cash -= (position_size - fees) # may need to manually compute
            self.unrealized_pl += (position_size - fees)
            self.positionHeld = True
        return order

    def sell(self):
        '''
        Execute sell order
        '''
        price = self.getPrice()
        if self.unrealized_pl > 0:
            # check if sale price exceeds last buy price at least enough to cover commissions
            lastBuy = self.getLastBuy()
            if (lastBuy is not None) and (price - lastBuy['price'] > lastBuy['fees'] + 0.005 * price):
                order = authclient.place_market_order(self.product, 'sell', funds=self.unrealized_pl)
                fees = order['fill_fees']
                self.cash += (self.unrealized_pl - fees)
                self.unrealized_pl = 0
                self.positionHeld = False
            else:
                print('Sale attempted but not worth it!')
        return order

            
    def getLastBuy(self):
        if self.transactions is None:
            # raise ValueError('No recorded transactions.')
            return None
        for x in reversed(self.transactions):
            if x['side'] == 'buy':
                return x

    def _create_model(self):
        # 1. data pre-processing
        # 2 create a model & train
        # 3. make future predictions
        '''
        add sortino or sharpe
        '''
        x = self.data[['close', 'MACD', 'MACDdiff', 'RSI', 'trix', 'bolu_sd1', 'boll_sd1', 'bolu_sd2', 'boll_sd2']]
        y = self.data['target']
        x, y = x.to_numpy(), y.to_numpy()

        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=69)

        epochs = 25
        batch_size = 10

        model = Sequential()
        '''///'''
        
        self.model = model


    def forecast(self, data):
        # predict closing price
        yhat = [0]
        return yhat


    def _loadData(self, technicals=True):
        '''
        get 300 data points at selected granularity at time interval of 6 hours
        
        FIX: adjust for variable granularity

        Note: currently uses 1 hr granularity
        '''
        get_time = lambda z: z.strftime('%Y-%m-%d %H:%M:%S').replace(' ', 'T') + 'Z'
        queries = []
        for k in range(timedelta(days = 180) // timedelta(hours = 300)):
            queries.append(pd.DataFrame(
                data = authclient.get_product_historic_rates(
                    self.product,
                    start=get_time(datetime.now() - k * timedelta(hours=300)),
                    end=get_time(datetime.now() - (k - 1) * timedelta(hours=300)),
                    granularity=3600
                ), 
                columns = ['time', 'low', 'high', 'open', 'close', 'volume'],
                dtype = object
            ))
        self.data = pd.concat(queries)[::-1].dropna().reset_index()
        # if technicals:
        #    self._addTechnicals()

        "MOST RECENT DATA AT BOTTOM OKAY?"

        # create target signal, what we will train on!
        #   signal indicator:
        #      whenever the 6hr future price exceeds the current price by at least 10% for a buy signal, 
        #      and a drawdown of the same magnitude for a sell signal
        shifted = self.data['close'].shift(12)      # 12 hr
        self.data['target'] = np.select(
            [self.data['close'] > 1.1 * shifted, self.data['close'] < 0.9 * shifted],
            [1, -1],
            default = 0
        )


    def _addTechnicals(self):
        """
        Augments the HLOCV ("lock-vee" -- the H is silent) data with technical indicators for:
            - trend,
            - momentum,
            - volume, and
            - volatility.
        """
        pass


    def computeKC(self):
        return self.W - (1 - self.W) / self.R

    def updateKC(self):
        '''
        needs implemented!
        '''
        winrate = float()
        winloss = float()
        return winloss * winrate - (1 - winrate)

    def getPrice(self):
        return float(authclient.get_product_ticker(self.product)['price'])   

    def getDataNow(self):
        return authclient.get_product_historic_rates(
            product_id=self.product,
            start=datetime.now()-timedelta(minutes=1),
            end=datetime.now()
        )[0]
    
    def render(self):
        '''
        needs more! nice graph would be cool
        '''
        plt.plot(self.netWorth)

        
    def getNetWorth(self):
        return self.unrealized_pl + self.cash