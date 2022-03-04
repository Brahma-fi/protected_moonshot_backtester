

def getSignalMACD(priceHistory,fast_length,slow_length,signal_length):

    hourlyPriceHistory = priceHistory.set_index('endTime').copy()    
    dailyPrices = pd.DataFrame(columns = ['close','fast_ma','slow_ma','macd','macd_signal','macd_hist'])
    
    dailyPrices['close'] = hourlyPriceHistory.close.resample('1d',offset ='8h').last()   
    dailyPrices['fast_ma'] = dailyPrices.close.rolling(fast_length).mean()
    dailyPrices['slow_ma'] = dailyPrices.close.rolling(slow_length).mean()
    dailyPrices['macd'] = dailyPrices.fast_ma - dailyPrices.slow_ma
    dailyPrices['macd_signal'] = dailyPrices['macd'].rolling(signal_length).mean()
    dailyPrices['macd_hist'] = dailyPrices['macd'] - dailyPrices['macd_signal']    

    if dailyPrices['macd_hist'].iloc[-1] > dailyPrices['macd_hist'].iloc[-2].mean():
        signal = 1
    else:
        signal = -1
        
    return signal


def rsi_calc(prices):
    returns = prices.pct_change().dropna()
    up_avg = returns[returns>0].mean()
    down_avg = abs(returns[returns<0].mean())
    rs = up_avg / down_avg  
    return 100 - (100/ (1+rs))


def get_hurst_exponent(time_series, max_lag=20):
    """Returns the Hurst Exponent of the time series"""

    lags = range(2, max_lag)

    # variances of the lagged differences
    tau = [np.std(np.subtract(time_series[lag:], time_series[:-lag])) for lag in lags]

    # calculate the slope of the log plot -> the Hurst Exponent
    reg = np.polyfit(np.log(lags), np.log(tau), 1)

    return reg[0]