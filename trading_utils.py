import numpy as np
# check when stop loss is hit, when profit taking is hit and when liquidation is hit. 
def checkLongExit(row, prices, factor,interest):
    take_profit = factor[0]
    stop_loss = factor[1]
    long_liq = factor[2]
    leverage = factor[4]

    
    take_profit_price = row.open*(1+take_profit)
    stop_loss_price = row.open*(1-stop_loss)
    liq_price = row.open*(1-long_liq)

    profit_trigger = prices.high[prices.high > take_profit_price]
    stop_trigger = prices.low[prices.low < stop_loss_price]
    
    #check which triggered first
    if (not profit_trigger.empty) & (not stop_trigger.empty):
        if profit_trigger.index.values[0] < stop_trigger.index.values[0]:
            trading_returns = interest*leverage*take_profit
            tag = 'take_profit'
        else:
            trading_returns = interest*leverage*-stop_loss
            tag = 'stop_loss'
        
    #in-between range double check if not liquidated
    elif (profit_trigger.empty) & (stop_trigger.empty):
        if row.low < liq_price:
            trading_returns = -interest
            tag = 'liquidated'
        else:
            trading_returns = interest*leverage*row.price_change #in-range long return
            tag = 'in_range'
            
    elif  not profit_trigger.empty:
        trading_returns = interest*leverage*take_profit
        tag = 'take_profit'
    elif not stop_trigger.empty:
        trading_returns = interest*leverage*-stop_loss
        tag = 'stop_loss'
        
    return trading_returns, tag


            
def checkShortExit(row, prices, factors,interest):
    take_profit = factors[0]
    stop_loss = factors[1]
    long_liq = factors[2]
    short_liq = factors[3]
    leverage = factors[4]
    
    take_profit_price = row.open*(1-take_profit)
    stop_loss_price = row.open*(1+stop_loss)
    liq_price = row.open*(1+short_liq)

    profit_trigger = prices.low[prices.low < take_profit_price]
    stop_trigger = prices.high[prices.high > stop_loss_price]
    
    #check which triggered first
    if (not profit_trigger.empty) & (not stop_trigger.empty):
        if profit_trigger.index.values[0] < stop_trigger.index.values[0]:
            trading_returns = interest*leverage*take_profit
            tag = 'take_profit'
        else:
            trading_returns = interest*leverage*-stop_loss
            tag = 'stop_loss'
        
    #in-range double check if not liquidated
    elif (profit_trigger.empty) & (stop_trigger.empty):
        if row.high > liq_price:
            trading_returns = -interest
            tag = 'liquidated'
        else:
            trading_returns = -1*interest*leverage*row.price_change #in-range short return
            tag = 'in_range'
            
    elif  not profit_trigger.empty:
        trading_returns = interest*leverage*take_profit
        tag = 'take_profit'
    elif not stop_trigger.empty:
        trading_returns = interest*leverage*-stop_loss
        tag = 'stop_loss'
            
    return trading_returns, tag



def checkEntry(hourlyData, location, row, leverage, take_profit, stop_loss, mm_min):
    location = hourlyData.index.get_loc(location)
    moving_avg = hourlyData.close.iloc[location-24*5:location:24].mean() #average of previous 3 days close

    if row.close > moving_avg:
        position = 1
    else:
        position = -1

    #leverage sizing based on realised volatility
    weekCloses = hourlyData.close.iloc[location-24*7:location:24]
    sigma = np.log(1+weekCloses.pct_change().dropna()).std()*np.sqrt(7)
    
    if sigma < 0.1:
        leverage = 8.5
    else:
        leverage = 7.5
    

    short_liq = (1+leverage)/(leverage*(mm_min+1))-1 #+0.005 #adjustment from ftx high to perpV2
    long_liq = 1-(1-leverage)/(leverage*(mm_min-1)) #+0.005 #adjustment from ftx low to perpV2

    if stop_loss > short_liq:
        stop_loss = (short_liq)/1.1
    
    if stop_loss > long_liq:
        stop_loss = long_liq/1.1
        
        
    factors = [take_profit, stop_loss, long_liq, short_liq, leverage, sigma]

    return position, factors



def moonshot_backtest(hourlyData, weeklyData, capital, stables_yield, freq, leverage, take_profit, stop_loss, mm_min):

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
                trading_returns, tag = checkLongExit(row, weeksPrices, factors, interest)
            elif position == -1:
                trading_returns, tag = checkShortExit(row, weeksPrices, factors, interest)

            weeklyData.loc[i,'flag'] = tag
            weeklyData.loc[i,'trading_returns'] = trading_returns
            weeklyData.loc[i,'returns'] = trading_returns + interest
            weeklyData.loc[i,'take_profit'] = factors[0]
            weeklyData.loc[i,'stop_loss'] = factors[1]
            weeklyData.loc[i,'leverage'] = factors[4]
            weeklyData.loc[i,'sigma'] = factors[5]
            capital += trading_returns + interest

        #signal logic for next weeks trade
        if weeklyData.index.get_loc(i) > 0: #only starts after 1 week of accruing interest
            position,factors = checkEntry(hourlyData,i,row, leverage,take_profit,stop_loss,mm_min)
        #interest for next weeks trade     
        interest = capital * stables_yield/365*freq 
        bench += bench*stables_yield/365*freq      

    finalCapital = weeklyData.loc[i,'capital'] + trading_returns + interest #add last period returns and current weeks interest 

    return weeklyData, finalCapital
