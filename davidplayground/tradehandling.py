import pandas as pd
import numpy as np


class TradeHandler:
    '''
    Superclass for trading algorithms
    '''
    def __init__(self, logic, initial_capital=1000.0, trade_fee=0.005):
        '''
        Initialize the trading algorithm with an initial balance.
        :param initial_capital: Amount in USD to start with
        '''
        self.wallets = {'USD': initial_capital}
        self.prices = {'USD': 1.0} # "last known prices" used for valuing portfolio
        self.fee = trade_fee
        self.logic = logic

    def portfolio_value(self):
        total = 0.0
        for name in self.wallets:
            total += self.prices[name] * self.wallets[name]
        return total

    def act_on(self, df, name):
        '''
        Feed in a historic dataset, it will return trade information
        :param df: DataFrame dataset
        :param name: string name of the coin
        :return: trades to be made by timestamp
        '''
        assert isinstance(df, pd.DataFrame)

        for i, row in df.iterrows():
            self.act(row, name)

    def act(self, row, name):
        '''
        Choose how to act on a given slice of a dataset. This is the
        prime method to override in designing a trading agent.
        :param row: a row of a dataframe dataset
        :param name: name of the coin
        '''
        self.prices[name] = row['close']
        return

    def _buy(self, price, amt, name):
        '''
        Buy an amount of a coin at a given price
        :param price: USD price of coin
        :param amt: Amount of coin
        :param name: Name of coin
        :return: Resulting action dictionary
        '''
        if price * amt * (1.0 + self.fee) > self.wallets['USD']:
            return False
        self.wallets[name] += amt
        self.wallets['USD'] -= price * amt * (1.0 + self.fee)
        return dict(action='buy', amt=amt, name=name, price=price)

    def _sell(self, price, amt, name):
        '''
        Sell an amount of a coin at a given price
        :param price: USD price of coin
        :param amt: Amount of coin
        :param name: Name of coin
        :return: Resulting action dictionary
        '''
        if self.wallets[name] < amt:
            return False
        self.wallets['USD'] += price * amt * (1.0 - self.fee)
        self.wallets[name] -= amt
        return dict(action='sell', amt=amt, name=name, price=price)

