import datetime,quandl
import numpy as np
import math
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn import preprocessing, cross_validation, neighbors
import json
import requests



#searchValue = request.POST['search']
#print (searchValue)
#request.session['search'] = searchValue
df = quandl.get("NSE/TATACHEM")
'''
#Selection of equity
url = 'http://signals.pythonanywhere.com/getfulldata?val=' + request.session.get('search',None)
 df = requests.get(url)
#print (df.text)
df = json.dumps(df.text)
 #print(df.tail())
'''

#High/Low, pct calculation

df = df[['Open','High','Low','Close']]
df['HL_pct'] = ((df['High'] - df['Low']) / df['Close']) * 100.0
df['pct_ch'] = ((df['Close'] - df['Open']) / df['Open']) * 100.0

df = df[['Close','HL_pct','pct_ch']]
#forecast label by 1% of df length

forecast_col = 'Close'
df.fillna('-1', inplace=True)
#print(len(df))
forecast_out = int(math.ceil(0.01*len(df)))
df['label'] = df[forecast_col].shift(-forecast_out)

#print('\n')
#print(df.tail(10))

#Create arrays for features and labels
X = np.array(df.drop(['label'],1))
X = preprocessing.scale(X)
X = X[:-forecast_out:]
X_lately = X[-forecast_out:]

df.dropna(inplace=True)
y = np.array(df['label'])
y = np.array(df['label'])
#cross validate train, test variables

X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=0.2)

#clf = neighbors.KNeighborsClassifier()
clf = LinearRegression(n_jobs=-1)
clf.fit(X_train, y_train)
accuracy = clf.score(X_test, y_test)

print(accuracy)

forecast_set = clf.predict(X_lately)
print(forecast_set)
df['Forecast'] = np.nan

last_date = df.iloc[-1].name
last_unix = last_date.timestamp()
one_day = 86400
next_unix = last_unix + one_day

for i in forecast_set:
    next_date = datetime.datetime.fromtimestamp(next_unix)
    next_unix += one_day
    df.loc[next_date] = [np.nan for _ in range(len(df.columns)-1)] + [i]
df = df[['Forecast']]
df = df[-forecast_out:]
print(df)

