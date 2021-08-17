import numpy as np
import pandas as pd

class TechnicalIndicators:

    '''
    Supported indicators:
        + Trend
            - MACD(x,y,z)
        + Momentum
            - Williams
            - RSI
            - Balance of Power
        + Volatility
            - Average True Range
            - Bollinger
        + Price Transform
            - Average Price
            - Median Price
            - Typical Price
            - Weighted Close Price

    add sortino, sharpe?

    It is assumed that the passed input data has the attributes, in order,
        --> 'time', 'low', 'high', 'open', 'close', 'volume'
    '''

    def __init__(self, data, **kwargs):
        self.df = data

        if not kwargs:
            print('No technical indicators specified.')
            return

        for k, v in kwargs:
            if k == 'trend':
                for x in v:
                    if x.lower() == 'macd':
                        self._addMACD()
            elif k == 'momentum':
                for x in v:
                    if x.lower() == 'rsi':
                        self._addRSI()
                    elif x.lower() == 'williams':
                        self._addWilliams()
                    elif x.lower() == 'bop':
                        self._addBOP()
                    elif x.lower() == 'gc':
                        self._addGoldenCross()
            elif k == 'volatility':
                for x in v:
                    if x.lower() == 'bbands':
                        self._addBBands()
                    elif x.lower() == 'atr':
                        self._addATR()
            elif k == 'price_transform':
                O, H, L, C = self.df.open, self.df.high, self.df.low, self.df.close
                # average
                if v.lower() == 'a':
                    self.df['ap'] = (O + H + L + C) / 4
                # median
                elif v.lower() == 'median':
                    self.df['mp'] = (H + L) / 2
                # typical
                elif v.lower() == 'typical':
                    self.df['tp'] = (H + L + C) / 3
                # weighted
                elif v.lower() == 'weighted':
                    self.df['wp'] = (2 * C + H + L) / 4
                else:
                    print('Price transform value not recognized.')
            elif k == 'sma':
                for x in v:
                    self.df['sma_' + str(x)] = self.df.close.rolling(x).mean()
                
            
                

    # Trend Indicators

    def _addMACD(self, slower=12, slowest=26, slow=9):
        pass
        
    # Momentum Indicators

    def _addRSI(self, period=14):
        '''
        ___________________________________________________________________
        
        Description
            Generates a value ranging [0, 100] measuring the ratio
            of average price moves, indicating biases toward the buy
            and sell side.
        
        Interpretation
            RSI > 70: asset is overbought
            RSI < 30: asset is oversold

        Formula
            RSI = 100 - 1 / (1 + RS)
            RS = Average Gain over Period / Average Loss over Period

        ___________________________________________________________________
        '''
        pass
    
    def _addWilliams(self, lookback=14):
        '''
        ___________________________________________________________________

        Description
            Percentage ranging between 0% and -100%, measuring the current
            close price in comparison to the high-low range over a certain
            time period.

        Interpretation
            %R =
               0: asset is overbought and in a strong uptrend
            -100: asset is oversold and in a strong downtrend
        
        Formula
            %R = -100 * [(Highest High - Close) / (Highest High - Lowest Low)]
        ___________________________________________________________________
        '''
        window = self.df[-lookback:]
        hh, ll = max(window.high), min(window.low)
        self.df['Williams %R'] = -100 * ((hh - window.close) / (hh - ll))
        

    def _addBOP(self, period=12):
        '''
        ___________________________________________________________________

        Description
            Evaluates the struggle between buyers and selleers, fluctuating
            between -1 and +1.

        Interpretation
            BOP > 0 means buying power is more powerful and BOP < 0 means 
            there is a strong sell pressure. BOP = 0 indicates a a balanced
            buy and sell pressure.

        Formula
            BOP = SMA[(Close - Open) / (High - Low)]
        ___________________________________________________________________
        '''
        # Consider use of EMA over SMA since we are interested in the
        # imminent future
        C, O, H, L = self.df.close, self.df.open, self.df.high, self.df.low
        self.df['BOP'] = pd.Series((C - O)/(H - L)).rolling(period).mean()

    # Volatility Indicators

    def _addBBands(self):
        '''
        ___________________________________________________________________
        
        Description
            Bollinger Bands study upper and lower envelope bands around the
            price of an instrument. The width of the bands is based on the 
            standard deviation of the closing prices from a moving average
            of price.

        Interpretation
            Two outputs from this indicator: the upper and lower bands, or
            UBB and LBB, respectively. Close value > UBB is a sell signal,
            and close value < LBB is a buy signal. Close values between the
            bands are considered a hold signal.

        Formula
            UBB, LBB = SMA(Close, period=20) +/- StDev(Typical Price)
        ___________________________________________________________________
        '''
        _tp = pd.Series((self.df.high + self.df.low + self.df.close) / 3)
        
        pass

    def _addGoldenCross(self):
        '''
        '''
        _tp = pd.Series()
        sma_50 = self.df.close.rolling(20).mean()
        sma_50

    def _addATR(self):
        pass

    # Price Transforms


        


