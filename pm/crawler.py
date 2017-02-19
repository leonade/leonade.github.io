## PubMed Central crawler
# Python: Python 2.7
# Author: Li
# Date: 2017-02-18

import urllib2
import re
import bs4	# need package BeautifulSoup4, install with '$apt-get install python-bs4' or '$pip install beautifulsoup4'
import json
import csv
from nltk import word_tokenize
from nltk.corpus import stopwords
import time

stop = set(stopwords.words('english'))

USE_PROXY = False
response = []
headers = {
	'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6' # pretend as Mozilla Browser
}
if(USE_PROXY):
	install_proxy();

def install_proxy(protocol='http',url='127.0.0.1:8080'):
	'''use proxy'''
	proxy = urllib2.ProxyHandler({protocol:url})
	opener = urllib2.build_opener(proxy)
	urllib2.install_opener(opener)

def get_page(url):
	'''request and parse page into BeautifulSoup tree'''
	global response
	req = urllib2.Request(url=url,headers=headers)
	# try:
	response = urllib2.urlopen(req)
	# except urllib2.HTTPError:
		# return(None)
	# except ConnectionResetError:
		# pass
	# skip big files which are possibly pdf wmv zip etc.
	try:
		response_length = response.headers['content-length']
	except KeyError:
		# if not having 'content-length', set to arbitrary value
		response_length = 1
	if response_length != None and response_length > 10485760:
		return(None)
	page = response.read()
	response.close()
	page_soup = bs4.BeautifulSoup(page)
	return(page_soup)

def text(soup):
	if soup is None:
		return('')
	s = soup.text
	# alphabetics = ''.join([char for char in s if char.isalpha() or char.isnumeric() or char in [' ',',','.','?','!','-','(',')''/','\\','\n']])
	alphabetics = ''.join([char for char in s if char not in ['\t']])
	elimited_space = ' '.join(alphabetics.split())
	return(elimited_space)


def parse_paper(pmcid):
	page_soup = get_page('http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=' + pmcid)
	
	figtags = page_soup.find_all('fig')
	figs = [{'caption':text(fig.find('caption')), 
		'url':'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC' + pmcid + '/bin/' + fig.find('graphic').get('xlink:href') + '.jpg'} 
		for fig in figtags if fig.find('graphic') is not None]
	# https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4673271/bin/oncotarget-06-21369-g001.jpg
	
	_ = [x.extract() for x in figtags]
	body_text = word_tokenize(text(page_soup.find('body')))
	for fig in figs:
		fig_text = word_tokenize(fig['caption'])
		co_occurrence = []
		for word in set(fig_text):
			# has letters &! stopword && in <B>
			if any([c.isalpha() for c in word]) and word not in stop and word in body_text:
				co_occurrence.append({'word':word, 'fig':fig_text.count(word), 'body': body_text.count(word)})
		
		co_occurrence.sort(key=lambda x: x['body']*x['fig'], reverse=True)
		fig['co_occurrence'] = co_occurrence
	return(figs)



if __name__ == "__main__":
	# pmcid = '2172346'
	with open('pmcids.txt','r') as fp:
		pmcids = fp.readlines()
		pmcids = [x.strip() for x in pmcids[1:]]
	
	result = []
	for i,pmcid in enumerate(pmcids[:100]):
		print '\r%s\t%d/10000'%(time.ctime(),i),
		result.append([pmcid, parse_paper(pmcid)])
	
	result = dict(result)
	with open('papers.json','w+') as fp:
		json.dump(result,fp)
	
	with open('papers.csv', 'w+') as f:
		fp = csv.writer(f)
		fp.writerow(['pcmid','caption','url','word','fig_count','body_count'])
		for pcmid in result:
			for fig in result[pcmid]:
				caption = fig['caption'].encode('utf8')
				url = fig['url']
				for cooc in fig['co_occurrence']:
					word = cooc['word'].encode('utf8')
					fig_count = cooc['fig']
					body_count = cooc['body']
					fp.writerow([pcmid, caption, url, word, fig_count, body_count])

