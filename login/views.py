from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponse
from django.template import RequestContext, Template
from django.template import loader

import datetime,quandl
import numpy as np
import math
import time
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn import preprocessing,neighbors
from sklearn.model_selection import train_test_split
from bdateutil import isbday
import mpld3

import json
import requests

quandl.ApiConfig.api_key = "u4gsXN7UfB4piszvqjej"
def isNotHol(date):
	dates_list = ['2018-01-26','2018-02-13','2018-03-02',
			  '2018-03-29 ','2018-04-30','2018-05-01',
			  '2018-08-215','2018-08-22','2018-09-13',
			  '2018-09-20','2018-10-02','2018-11-07',
			  '2018-11-08','2018-11-23','2018-12-25']
	date = date.strftime('%Y-%m-%d')
	if date in dates_list:
		return False
	else :
		return True

def indicators(request):
	searchValue = request.session['search']
	historicData = requests.get('https://signals.pythonanywhere.com/getdata?val=' + searchValue)

def index(request):
	return render(request, 'login/base.html')

def macd(request):
	searchValue = request.session['search']
	request.session['search'] = searchValue
	try:
		resp = requests.get('http://signals.pythonanywhere.com/codes?val='+ searchValue)
	except:
		time.sleep(2)
	jData = resp.text
	jData = json.loads(jData)
	company_name = jData[0]["value"]
	t = loader.get_template('login/base2.html')
	c = {'search': searchValue,'cname':company_name}
	return HttpResponse(t.render(c, request))

def graph(request):
	searchValue = request.session.get('search', None)
	
def search1(request):
	searchValue = request.POST['search']
	print (searchValue)
	request.session['search'] = searchValue
	try:
		resp = requests.get('https://signals.pythonanywhere.com/codes?val='+ searchValue)
	except:
		print('Sleeping')
		time.sleep(2)
	jData = resp.text
	jData = json.loads(jData)
	company_name = jData[0]["value"]
	t = loader.get_template('login/base2.html')
	c = {'search': searchValue,'cname':company_name}
	return HttpResponse(t.render(c, request))

def search(request):
	searchValue = request.session['search']
	print (searchValue)
	request.session['search'] = searchValue
	df = quandl.get(searchValue)
	'''
	#Selection of equity
	url = 'http://signals.pythonanywhere.com/getfulldata?val=' + request.session.get('search',None)
	df = requests.get(url)
	#print (df.text)
	df = json.dumps(df.text)
	#print(df.tail())
	'''
	try:
		resp = requests.get('https://signals.pythonanywhere.com/codes?val='+ searchValue)
	except:
		time.sleep(2)
	jData = resp.text
	jData = json.loads(jData)
	company_name = jData[0]["value"]
	print(company_name)


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
	df2 = df[['Close']]
	df2 = df2[-forecast_out:-10]
	df2 = df2.to_html()

	#print('\n')
	#print(df)

	#Create arrays for features and labels

	X = np.array(df.drop(['label'],1))
	X = preprocessing.scale(X)
	X = X[:-forecast_out:]
	X_lately = X[-forecast_out:]
	
	df.dropna(inplace=True)
	y = np.array(df['label'])
	y = np.array(df['label'])
	#cross validate train, test variables
	
	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)   
	clf = neighbors.KNeighborsRegressor(weights='distance')
	clf.fit(X_train, y_train)
	accuracy = clf.score(X_test, y_test)
	print(accuracy)
	accuracy = str(accuracy * 100) + ' %'
	#print(df.tail(10))
	forecast_set = clf.predict(X_lately)
	print(forecast_set, accuracy, forecast_out)
	df['Forecast'] = np.nan
	
	last_date = df.iloc[-1].name
	last_unix = last_date.timestamp()
	one_day = 86400
	next_unix = last_unix + one_day
 
	for i in forecast_set:
		next_date = datetime.datetime.fromtimestamp(next_unix)
		next_unix += one_day
		if isbday(next_date) and isNotHol(next_date):
			df.loc[next_date] = [np.nan for _ in range(len(df.columns)-1)] + [i]
		else:
			continue
   
	df = df[['Forecast']]
	df = df[-forecast_out:]
	df = df.dropna() 
	df = df.to_html()
	t = loader.get_template('login/forecast.html')
	c = {'search': searchValue,'table':df,'accuracy':accuracy,'table2':df2,'cname':company_name}
	return HttpResponse(t.render(c, request))

def create(request):
	uname = request.POST.get('uname')
	pwd = request.POST.get('pwd')
	payload = {}
	payload['password'] = pwd
	payload['username'] = uname
	#jsonVal = json.loads(data)
	#data = dict(data)
	print(json.dumps(payload, indent=4, sort_keys=True))
	headers = {
		"content-type" : "application/json"
	}
	r = requests.post('https://signals.pythonanywhere.com/register', headers = headers, json=payload)
	print(r)
	
	if r.status_code == 200:
		messages.info(request,'Registered successfully.')
	else :
		messages.info(request,'Registration Failed.')
			
	return render(request, 'login/base.html')

def validate(request):
	uname = request.POST.get('uname')
	pwd = request.POST.get('psw')
	payload = {}
	payload['password'] = pwd
	payload['username'] = uname
	headers = {
		"content-type" : "application/json"
	}
	r = requests.post('https://signals.pythonanywhere.com/login', headers = headers, json=payload)
	print(r == 200)
	if r.status_code == 200:
		messages.info(request,'Hi ' + uname +' you are loggedin successfully.\nSearch for your desired company to view the results')
		return render(request, 'login/log.html')
	else :
		messages.info(request,'Login failed.')
		return render(request, 'login/base.html')

def updateSession(request):
	#request.session['macdData'] = request.POST['macdData']
	#request.session['rsiData'] = request.POST['rsiData']
	print('Updated successfully with ' + request.POST.get('macdData') + '\n' + request.POST.get('rsiData'))
	return HttpResponse('Success')

def pattern(request):
		searchValue = request.session['search']
		request.session['search'] = searchValue
		response = requests.get('http://signals.pythonanywhere.com/getdata?val=' + searchValue )#, proxies = {'http':'http://proxy.server:3128'})
		jsonData = response.text
		jsonData = json.loads(jsonData)
		#print(len(jsonData))
		try:
			resp = requests.get('https://signals.pythonanywhere.com/codes?val='+ searchValue)#, proxies = {'http':'http://proxy.server:3128'})
		except:
			time.sleep(2)
		jData = resp.text
		jData = json.loads(jData)
		company_name = jData[0]["value"]
		iterator = 1
		volumeAverage = 0
		
		
		for day in jsonData:
			if day[5] == None:
				continue
			else :
				volumeAverage = ( ( volumeAverage * (iterator-1) ) + day[5]) / iterator
				iterator = iterator + 1
		print(volumeAverage)
		request.session['volumeAverage'] = volumeAverage

		t1 = jsonData[0]
		t2 = jsonData[1]
		t3 = jsonData[2]
		#print('Day - 1 - ' + str(t1) + '\n' +
						#'Day - 2 - ' + str(t2) + '\n' +
						#'Day - 3 - ' + str(t3))
						
		o1 = t1[1]
		h1 = t1[2]
		l1 = t1[3]
		c1 = t1[4]

		o2 = t2[1]
		h2 = t2[2]
		l2 = t2[3]
		c2 = t2[4]

		o3 = t3[1]
		h3 = t3[2]
		l3 = t3[3]
		c3 = t3[4]
						
		matchingPatterns = {"Bullish Marubozu":["No","Positive"],"Bearish Marubozu":["No","Negative"],"Top":["No","Neutral"],"Doji":["No","Neutral"],
												"Bullish Engulfing":["No","Positive"],"Bearish Engulfing":["No","Negative"],"Bullish Piercing":["No","Positive"],"Bearish Piercing":["No","Negative"],"Bullish Harami":["No","Positive"],"Bearish Harami":["No","Negative"],"Gap up":["No","Positive"],"Gap down":["No","Negative"],
												"Morning Star":["No","Positive"],"Evening Star":["No","Negative"]}

		###Single day patterns
												
		##Marubozu Check

		#Bullish
		if((c1 * 0.0008) < ((o1-l1)/c1)*100 < (c1 * 0.0012) and (c1 * 0.0008) < ((h1-c1)/c1)*100 < (c1 * 0.0012)):
				matchingPatterns['Bullish Marubozu'][0] = "Yes"
		#Bearish
		if((c1 * 0.0008) < ((l1-c1)/c1)*100 < (c1 * 0.0012) and (c1 * 0.0008) < ((h1-o1)/c1)*100 < (c1 * 0.0012)):
				matchingPatterns['Bearish Marubozu'][0] = "Yes"
				
		##Top Check
		if((c1 * 0.0045) < abs(((o1-c1)/c1)*100) < (c1 * 0.0055) and ((h1-l1)/c1)*100 >= (c1 * 0.008)):
				matchingPatterns['Top'][0] = "Yes"
				
		##Doji Check
		if((c1 * 0.0008) < abs(((o1-c1)/c1)*100) < (c1 * 0.0012) and ((h1-l1)/c1)*100 >= (c1 * 0.008)):
				matchingPatterns['Top'][0] = "Yes"
				
		###Two day patterns

		##Engulfing Check

		##Bullish
		if((c1-o2) > 0 and (o1-c2) < 0):
				matchingPatterns['Bullish Engulfing'][0] = "Yes"
		##Bearish
		if((o1-c2) > 0 and (c1-o2) < 0):
				print((o1-c2) > 0 and (c1-o2) < 0)
				matchingPatterns['Bearish Engulfing'][0] = "Yes"

		##Piercing

		#Bullish
		if((o2-c2) > ((c1-c2)/(o2-c2))*100 >= (o2-c2)*0.5):
				matchingPatterns['Bullish Piercing'][0] = "Yes"
		#Bearish
		if((c2-o2) > ((o1-o2)/(c2-o2))*100 >= (c2-o2)*0.5):
				matchingPatterns['Bearish Piercing'][0] = "Yes"
				
		##Harami
		#print(c1-o2)
		#print(o1-c2)
		#Bullish
		if((c1-o2)<0 and (o1-c2)>0 and o1 < c1):
				matchingPatterns['Bullish Harami'][0] = "Yes"
		#Bearish
		if((o1-c2)<0 and (c1-o2)>0 and o1 > c1):
				matchingPatterns['Bearish Harami'][0] = "Yes"

		##Gap up
		if(c2 < o1 and o1 < c1):
				matchingPatterns["Gap up"][0] = "Yes"

		##Gap down
		if(c2 > o1 and c1 < o1):
				matchingPatterns["Gap down"][0] = "Yes"
				
		###Three day patterns

		#Morning Star

		if((o3-c3) > 0 and ((c1 * 0.0045) < abs(((o1-c1)/c1)*100) < (c1 * 0.0055) and ((h1-l1)/c1)*100 >= (c1 * 0.008) or (c1 * 0.0008) < abs(((o1-c1)/c1)*100) < (c1 * 0.0012) and ((h1-l1)/c1)*100 >= (c1 * 0.008)) and (c1-o1) > 0):
				matchingPatterns['Morning Star'][0] = "Yes"

		#Evening Star
				
		if((o3-c3) < 0 and ((c1 * 0.0045) < abs(((o1-c1)/c1)*100) < (c1 * 0.0055) and ((h1-l1)/c1)*100 >= (c1 * 0.008) or (c1 * 0.0008) < abs(((o1-c1)/c1)*100) < (c1 * 0.0012) and ((h1-l1)/c1)*100 >= (c1 * 0.008)) and (c1-o1) < 0):
				matchingPatterns['Evening Star'][0] = "Yes"

		df= pd.DataFrame(matchingPatterns)
		df=df.to_html()
		t = loader.get_template('login/pattern.html')
		c = {'pattern':df,'search': searchValue,'cname':company_name,'volumeAverage':volumeAverage}
		return HttpResponse(t.render(c, request))

