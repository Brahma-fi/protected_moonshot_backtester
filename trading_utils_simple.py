import numpy as np
# check when stop loss is hit, when profit taking is hit and when liquidation is hit. 
def checkLongExitSimple(row, prices, factors,interest):
    long_liq = factors[0]
    short_liq = factors[1]
    leverage = factors[2]

    liq_price = row.open*(1-long_liq)
        
    #check if liquidated
    if row.low < liq_price:
        trading_returns = -interest
        tag = 'liquidated'
    else:
        trading_returns = interest*leverage*row.price_change #in-range long return
        tag = 'in_range'
   
    return trading_returns, tag


            
def checkShortExitSimple(row, prices, factors,interest):

    long_liq = factors[0]
    short_liq = factors[1]
    leverage = factors[2]
    
    liq_price = row.open*(1+short_liq)
    
    #check if liquidated
    if row.high > liq_price:
        trading_returns = -interest
        tag = 'liquidated'
    else:
        trading_returns = -1*interest*leverage*row.price_change #in-range short return
        tag = 'in_range'
            
            
    return trading_returns, tag



def checkEntrySimple(hourlyData, location, row, leverage, mm_min):
    location = hourlyData.index.get_loc(location)
    moving_avg = hourlyData.close.iloc[location-24*5:location:24].mean() #average of previous 3 days close

    if row.close > moving_avg:
        position = 1
    else:
        position = -1


    short_liq = (1+leverage)/(leverage*(mm_min+1))-1+0.005 #adjustment from ftx high to perpV2
    long_liq = 1-(1-leverage)/(leverage*(mm_min-1))+0.005 #adjustment from ftx low to perpV2


    factors = [long_liq, short_liq, leverage]

    return position, factors



def backtestMoonshotSimple(hourlyData, weeklyData, capital, stables_yield, freq, leverage, mm_min):

    position = 0
    returns = 0
    interest = 0
    bench = capital


    for i,row in weeklyData.iterrows():

        weeklyData.loc[i,'capital'] = capital
        weeklyData.loc[i,'position'] = position
        weeklyData.loc[i,'interest'] = interest
        weeklyData.loc[i,'benchmark'] = bench

        #have a position from previous week, calc returns
        if abs(position) > 0:
            #get all hourly prices for the current trading week
            location = hourlyData.index.get_loc(i)
            weeksPrices = hourlyData[['close','high','low']].iloc[location-24*freq:location] 

            if position == 1:
                trading_returns, tag = checkLongExitSimple(row, weeksPrices, factors, interest)
            elif position == -1:
                trading_returns, tag = checkShortExitSimple(row, weeksPrices, factors, interest)

            weeklyData.loc[i,'flag'] = tag
            weeklyData.loc[i,'trading_returns'] = trading_returns
            weeklyData.loc[i,'returns'] = trading_returns + interest
            weeklyData.loc[i,'leverage'] = factors[2]
   
            capital += trading_returns + interest

        #signal logic for next weeks trade
        if weeklyData.index.get_loc(i) > 0: #only starts after 1 week of accruing interest
            position,factors = checkEntrySimple(hourlyData,i,row,leverage,mm_min)
        #interest for next weeks trade     
        interest = capital * stables_yield/365*freq 
        bench += bench*stables_yield/365*freq      

    finalCapital = weeklyData.loc[i,'capital'] + trading_returns + interest #add last period returns and current weeks interest 

    return weeklyData, finalCapital
