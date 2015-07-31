# -*- coding: utf-8 -*-
## Twitter pickle to html
## 
## created on 2015-7-29 21:09:28 by Li
## last modified 2015-7-31 02:18:05 by Li

from bottle import Bottle, route, run, template, request, response,  post, get, redirect, static_file, debug
app=Bottle()
debug(True)

import os
os.chdir(r'D:/360Downloads/AMiner/leonade.github.io/Twitter_of_NCE_Researchers/')

import time

try: 
    from cPickle import load
except: 
    from pickle import load
	
with open('researcher_twitter_accounts_closure.pickle','r') as f:
    researcher_twitter_accounts = load(f)
# len(researcher_twitter_accounts)

with open('researcher_tweets.pickle','r') as f:
    researcher_tweets = load(f)
# len(researcher_tweets)

for account in researcher_twitter_accounts:
    account['tweets'] = []

for tweet in researcher_tweets:
    for researcher in researcher_twitter_accounts:
		if tweet['user_id'] == researcher['id']:
			tweet['id'] = str(tweet['id'])
			researcher['tweets'].append(tweet)

@app.route('/')
def page():
	return template('template')

@app.route('/fonts/:filename#.+#')
def returnStatic(filename):
	return static_file(filename, root='./fonts/')
	
# @app.route('/javascriptTest/:filename#.+#')
# def returnStatic(filename):
	# return static_file(filename, root='./web/javascriptTest/')

# researcher_twitter_accounts.sort(key=lambda r: r['researcher_name'])

for i in range(len(researcher_twitter_accounts)):
    researcher_twitter_accounts[i]['tweets'] = researcher_twitter_accounts[i]['tweets'][:10]

@app.route('/json')
def json():
	return {'data':researcher_twitter_accounts[:10], 'time': time.strftime("%b %d %H:%M:%S", time.localtime())}

run(app,host='localhost', port=8080)
