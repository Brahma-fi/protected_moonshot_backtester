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
    return outputData