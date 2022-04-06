import pandas as pd
from datetime import timedelta

def ftxTransformer(data):
    data['endTime'] =  (pd.to_datetime(data['startTime'].copy())+timedelta(seconds =3600))
    data.drop(['Unnamed: 0','volume','startTime'],axis=1,inplace=True)
    cols = ['endTime','open','high','low','close']
    outputData = data[cols].copy()
    outputData.sort_values(by=['endTime'],inplace=True)
    outputData.set_index('endTime',inplace=True)
    outputData['volatility'] = outputData.close.pct_change().ewm(alpha=0.4).std()
    
    weeklyData = outputData.resample('7d',offset = '8h',label='right').agg({'open':'first','close':'last','high':'max','low':'min'})
    
    # drop this as last week data is extrapolated
    weeklyData.drop(index=weeklyData.index[-1], 
        axis=0, 
        inplace=True)
    weeklyData['price_change'] = weeklyData['close'] / weeklyData['open']  - 1
    weeklyData = weeklyData.dropna()

    return outputData,weeklyData










def chainlinkTransformer(data):
    data['endTime'] =  (pd.to_datetime(data['updatedAt'].copy(),unit='s'))
    data.drop(['updatedAt','startedAt','roundId','roundId.1'],axis=1,inplace=True)
    data['price'] = data['price'].copy() / 1e8
    data.sort_values(by=['endTime'],inplace=True)
    data.set_index('endTime',inplace=True)
    data['index_twap'] = data.rolling('15min').mean()
    
    #generate weeklyData
    opens = data.price.resample('7d',offset = '8h',label='right').first()
    opens.rename('open',inplace=True)
    mins = data.index_twap.resample('7d',offset = '8h',label='right').min()
    mins.rename('low',inplace=True)
    maxs = data.index_twap.resample('7d',offset = '8h',label='right').max()
    maxs.rename('high',inplace=True)
    
    weeklyData = pd.concat([opens,maxs,mins],axis=1)
    weeklyData['close'] = weeklyData.open.shift(-1)
    weeklyData = weeklyData[['open','close','high','low']]
    # drop this as last week data is extrapolated
    weeklyData.drop(index=weeklyData.index[-1], 
            axis=0, 
            inplace=True)
    
    weeklyData['price_change'] = weeklyData['close'] / weeklyData['open']  - 1
    

    #generate hourlyData
    opens = data.price.resample('1h',offset = '8h',label='right').first()
    opens.rename('open',inplace=True)
    mins = data.index_twap.resample('1h',offset = '8h',label='right').min()
    mins.rename('low',inplace=True)
    maxs = data.index_twap.resample('1h',offset = '8h',label='right').max()
    maxs.rename('high',inplace=True)
    
    hourlyData = pd.concat([opens,maxs,mins],axis=1)
    hourlyData['close'] = hourlyData.open.shift(-1)
    hourlyData = hourlyData[['open','close','high','low']]
    # drop this as last week data is extrapolated
    hourlyData.drop(index=hourlyData.index[-1], 
            axis=0, 
            inplace=True)
    
    
    
    
    
    return data,weeklyData,hourlyData


def dvolTransformer(data):
    data['endTime'] = pd.to_datetime(data['date'].copy(),utc=True)
    data.set_index('endTime',inplace=True)
    data.rename(columns = {'open':'dvol_open','close':'dvol_close'},inplace=True)
    data.drop(['date','high','low'],axis=1,inplace=True)
    hourlyData = data.copy()
    
    weeklyData = hourlyData.resample('7d',offset = '8h',label='right').agg({'dvol_open':'first','dvol_close':'last'})

    #drop last row which is interpolated
    weeklyData.drop(index=weeklyData.index[-1], 
        axis=0, 
        inplace=True)


    return hourlyData,weeklyData


def skewDataTransformer(data):
    data['endTime'] = pd.to_datetime(data['DateTime'].copy(),utc=True)
    data.set_index('endTime',inplace=True)
    data.drop(['DateTime'],axis=1,inplace=True)
    data.rename(columns={'1wk ATM Vol':'open'},inplace=True)
    data['close'] = data.open.shift(-1) 
    hourlyData = data.copy()
    
    weeklyData = hourlyData.resample('7d',offset = '8h',label='right').agg({'open':'first','close':'last'})

    #drop last row which is interpolated
    weeklyData.drop(index=weeklyData.index[-1], 
        axis=0, 
        inplace=True)


    return hourlyData,weeklyData