import numpy as np
import pandas as pd
from scipy.stats import norm 


def blackScholesPrice(S,K,T,sigma,r,flag):
    
    d1 = ( np.log(S/K)+(r+sigma**2/2) * T ) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)

    price = flag*S*norm.cdf(flag*d1)-flag*K*np.exp(-r*T)*norm.cdf(flag*d2)
    
    return price


def runOptionBacktest(weeklyInputs,weeklyVol,freq,interest,currency,r,strike_otm,strategy,strike_rounding=False):
    # weeklyInputData Pandas dataframe, weekly frequency
    # Columns required, open,close,position
    
    outputData = pd.DataFrame(index=weeklyInputs.index)
    outputData['optionReturns'] = 0
    
    T = freq/365
    
    spotPrices = weeklyInputs.open
    
    if strike_rounding:
        callStrikes = round(spotPrices * (1+strike_otm)/100.0,0)*100.0
        putStrikes = round(spotPrices * (1-strike_otm)/100.0,0)*100.0
    else:
        callStrikes = spotPrices * (1+strike_otm)
        putStrikes = spotPrices * (1-strike_otm)
    
    outputData['sigma_open'] = weeklyVol.close.shift(fill_value=weeklyVol.close.iloc[0])/100
    outputData['sigma_close'] = weeklyVol.close/100
    
    
    outputData['callPrices'] = blackScholesPrice(spotPrices,callStrikes,T,outputData['sigma_open'],r,1)/spotPrices
    outputData['putPrices'] = blackScholesPrice(spotPrices,putStrikes,T,outputData['sigma_open'],r,-1)/spotPrices
    
    outputData['callPayoff'] = np.where(weeklyInputs.close > callStrikes,weeklyInputs.close - callStrikes,0)
    outputData['putPayoff'] = np.where(putStrikes > weeklyInputs.close,putStrikes - weeklyInputs.close,0)
        
    if strategy == 'optionBuyer':
        maskLong = (weeklyInputs.position > 0)
        maskShort = (weeklyInputs.position < 0)
        
        if currency == 'USD':
            outputData.loc[maskLong,'optionReturns'] = interest / (outputData.loc[maskLong,'callPrices']*weeklyInputs.loc[maskLong,'open']) * outputData.loc[maskLong,'callPayoff'] -interest
            outputData.loc[maskShort,'optionReturns'] = interest / (outputData.loc[maskShort,'putPrices']*weeklyInputs.loc[maskShort,'open']) * outputData.loc[maskShort,'putPayoff'] -interest
        else:
            print(currency+" is not a known currency")       
    else:
        print(strategy+" is not a known option strategy")
    
    alpha = outputData.optionReturns.sum() / (outputData.shape[0]/52)
    
    return outputData,alpha