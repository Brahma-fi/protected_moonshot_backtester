import pandas as pd
import numpy as np


def runPerpBacktest(weeklyInputs,hourlyInputs,freq,leverage,mm_min,interest,currency,strategy,take_profit=0.15,stop_loss=0.05):
    # weeklyInputData Pandas dataframe, weekly frequency
    # Columns required, open,close,high,low,price_change,position
    outputData = weeklyInputs.copy()
    
    short_liq = (1+leverage)/(leverage*(mm_min+1))-1
    long_liq = 1-(1-leverage)/(leverage*(mm_min-1))

    if short_liq < stop_loss or long_liq < stop_loss:
        print("warning stop loss to low for leverage")
        stop_loss = min(short_liq,long_liq)/1.1
        
    if strategy == 'simple':
        outputData['liq_price'] = np.where(weeklyInputs.position>0,weeklyInputs.open*(1-long_liq),weeklyInputs.open*(1+short_liq))
        outputData['perpReturns'] = 0
        
        maskLongLiqs = ((weeklyInputs.position > 0) & (weeklyInputs.low < outputData.liq_price) )
        maskShortLiqs = ((weeklyInputs.position < 0) & (weeklyInputs.high > outputData.liq_price) )
        maskElse = (maskLongLiqs == False) & (maskShortLiqs == False) 
        
        if currency == 'USD':
            outputData.loc[(maskLongLiqs | maskShortLiqs),'perpReturns'] = -interest
            outputData.loc[maskElse,'perpReturns'] = interest*leverage*weeklyInputs.loc[maskElse,'position']*weeklyInputs.loc[maskElse,'price_change']
        else:
            print(currency+" is not a known currency")
            
            
    elif strategy == 'enhanced':
        #enhanced perp strategy returns
        outputData['take_profit'] = np.where(weeklyInputs.position>0,weeklyInputs.open*(1+take_profit),weeklyInputs.open*(1-take_profit))
        outputData['stop_loss'] = np.where(weeklyInputs.position>0,weeklyInputs.open*(1-stop_loss),weeklyInputs.open*(1+stop_loss))
        
        #find exit flag
        outputData['exit_flag'] = 0
        exit_flags = checkPerpExit(outputData, hourlyInputs,take_profit,stop_loss, long_liq,short_liq,freq) 
        outputData.loc[outputData.index,'exit_flag'] = exit_flags.copy()
        
        maskTakeProfit = (outputData.exit_flag == 'take_profit')
        maskStopLoss = (outputData.exit_flag == 'stop_loss')
        maskInRange = (outputData.exit_flag == 'in_range')
        
        if currency == 'USD':
            outputData.loc[maskTakeProfit,'perpReturns'] = interest*leverage*take_profit
            outputData.loc[maskStopLoss,'perpReturns'] = -interest*leverage*stop_loss
            outputData.loc[maskInRange,'perpReturns'] = interest*leverage*weeklyInputs.loc[maskInRange,'position']*weeklyInputs.loc[maskInRange,'price_change']
        else:
            print(currency+" is not a known currency")

    else:
        print(strategy+" is not a known perp strategy")
    
    alpha = outputData.perpReturns.sum() / (outputData.shape[0]/52)

    return outputData,alpha





def checkPerpExit(exitData, hourlyData,take_profit,stop_loss, long_liq,short_liq,freq):

    for i,row in exitData.iloc[0:,:].iterrows():
        flag = 0
        loc = hourlyData.index.get_loc(i)
        weeksPrices = hourlyData.close.iloc[loc-freq*24:loc]

        if row.position < 0:
            take_profitCount = np.sum( weeksPrices < row.open*(1-take_profit) , axis = 0)
            stop_lossCount = np.sum( weeksPrices > row.open*(1+stop_loss) , axis = 0)
    

            if take_profitCount + stop_lossCount == 0:
                flag = 'in_range'
            elif (take_profitCount+stop_lossCount) == take_profitCount:
                flag = 'take_profit'
                exitPrice = row.open*(1-take_profit)
            elif (take_profitCount+stop_lossCount) == stop_lossCount:
                flag = 'stop_loss'
                exitPrice = row.open*(1+stop_loss)
            else: #stop loss and takeprofit hit
                tp = (weeksPrices < row.take_profit).argmax(axis = 0)
                sl = (weeksPrices > row.stop_loss).argmax(axis = 0)
    
                if tp < sl:
                    flag = 'take_profit'
                    exitPrice = row.open*(1-take_profit)
                else:
                    flag = 'stop_loss'
                    exitPrice = row.open*(1+stop_loss)

        elif row.position > 0:
            take_profitCount = np.sum( weeksPrices > row.open*(1+take_profit) , axis = 0)    
            stop_lossCount = np.sum( weeksPrices < row.open*(1-stop_loss) , axis = 0)
    
            if take_profitCount + stop_lossCount == 0:
                flag = 'in_range'
            elif (take_profitCount+stop_lossCount) == take_profitCount:
                flag = 'take_profit'
                exitPrice = row.open*(1+take_profit)
            elif (take_profitCount+stop_lossCount) == stop_lossCount:
                flag = 'stop_loss'
                exitPrice = row.open*(1-stop_loss)
            else: #stop loss and takeprofit hit
                tp = (weeksPrices > row.take_profit).argmax(axis = 0)
                sl = (weeksPrices < row.stop_loss).argmax(axis = 0)
    
                if tp < sl:
                    flag = 'take_profit'
                    exitPrice = row.open*(1+take_profit)
                else:
                    flag = 'stop_loss'
                    exitPrice = row.open*(1-stop_loss)
        
        exitData.loc[i,'exit_flag'] = flag
    

    return exitData['exit_flag']



