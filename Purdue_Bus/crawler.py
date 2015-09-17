# -*- coding: utf-8 -*-
# Python 3
# author: Lucius Lee
# email: luciusregulas@gmail.com
# created: 2015-8-22 22:23:52
# modified: 2015-8-24 16:14:18
# D:
# "D:\Program Files\Projects\Purdue_Bus\goagent\local\goagent.exe"
# cd D:\ProgrammeFiles\Python 3.3
# python

import os,sys
import urllib,urllib.request
import re
import bs4
from pprint import pprint
import json
import time

os.chdir(r'D:\Program Files\Projects\Purdue_Bus')

from Google_polyline import encode, decode

response = []
headers = {
	'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6' # pretend as Mozilla Browser
}
proxy_handler = urllib.request.ProxyHandler({'http':'127.0.0.1:1358'})	# using goagent proxy deployed on Google AppEngine
opener = urllib.request.build_opener(proxy_handler, urllib.request.HTTPHandler)
urllib.request.install_opener(opener)



def get_page(url):
# request and parse page
	global response
	# req = urllib.request.Request(url=urllib.parse.quote(url,safe='/:'),headers=headers)
	req = urllib.request.Request(url=url,headers=headers)
	try:
		response = urllib.request.urlopen(req)
	except urllib.request.URLError:
		return(None)
	# except ConnectionResetError:
		# pass
	# skip big files which are possibly pdf wmv zi etc.
	if response.length != None and response.length > 10485760:
		return(None)
	page = response.read()
	response.close()
	page_soup = bs4.BeautifulSoup(page)
	return(page_soup)

def get_links(soup):
# extract links in page
	links = soup.find_all("a")
	links = [link.get('href') for link in links]
	#for xx in x:
			#print(xx)
	links = list(l for l in links if l!=None and l!='')
	if len(links) == 0:
		return([])
	return(fill_url(links,get_url_base(soup)))

def get_url_base(soup):
# get base of all links
	if (soup.find("base") != None and
		soup.find("base").get("href") != None and
		soup.find("base").get("href") != ''):
		base_url = soup.find("base").get("href")
	else:
		base_url = re.search(r"^http.?://.+?/",response.geturl()+'/').group()
	if base_url[-1] == '/':
		base_url = base_url[:-1]
	return(base_url)

def fill_url(links,base_url):
# fill links without domain
	x = list(filter(lambda xx : xx[0] == '/', links))
	links = list(filter(lambda xx : xx[:4] == 'http', links))
	if len(x)>0:
		x = list(map(lambda xx : base_url + xx, x))
		links.extend(x)
	return(list(set(links)))

def text(s):
	alphabetics = ''.join([char for char in s if char.isalpha() or char.isnumeric() or char in [' ','\\','/']])
	elimited_space = ' '.join(alphabetics.split())
	return(elimited_space)


def get_stop_url(stop_id):
	url = 'http://myride.gocitybus.com/public/laf/web/default.aspx'
	page_soup = get_page(url)
	form = {}
	for x in page_soup.form.find_all('input'):
		if x.attrs['type'] == 'text':
			form[x.attrs['name']] = stop_id
		else:
			form[x.attrs['name']] = x.attrs['value']
	
	header = {
	'Cache-Control': 'max-age=0',
	'Connection': 'keep-alive',
	'Host': 'myride.gocitybus.com',
	'Origin': 'http://myride.gocitybus.com',
	'Referer': 'http://myride.gocitybus.com/public/laf/web/',
	'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'}
	
	postdata = urllib.parse.urlencode(form).encode('utf-8')
	
	req = urllib.request.Request(url=url, data=postdata, headers=headers, origin_req_host='http://myride.gocitybus.com', method='POST')
	response = urllib.request.urlopen(req)
	url = response.geturl()
	response.close()
	if url == 'http://myride.gocitybus.com/public/laf/web/default.aspx':	#BUS125
		return('')
	else:
		# 'http://myride.gocitybus.com/public/laf/web/ViewStopNew.aspx?sp=61d6a153-df7f-4a6e-93d1-85df7f9819f3&pt=30&r=60'
		return(url.split('=')[1].split('&')[0])


# Get Lon Lat via Google Geocode
Geocode_count = 0
def get_geocode(StopDesc):
	global Geocode_count
	Geocode = get_page('http://maps.google.com/maps/api/geocode/json?address='+urllib.parse.quote_plus(StopDesc)+',+West+Lafayette,+IN&sensor=false')
	Geocode = json.loads(Geocode.text)
	# use following in debugs for saving Google Geocode quota
	# Geocode = '''{
				   # "results" : [
					  # {
						 # "address_components" : [
							# {
							   # "long_name" : "240",
							   # "short_name" : "240",
							   # "types" : [ "street_number" ]
							# },
							# {
							   # "long_name" : "Northwestern Avenue",
							   # "short_name" : "Northwestern Ave",
							   # "types" : [ "route" ]
							# },
							# {
							   # "long_name" : "West Lafayette",
							   # "short_name" : "West Lafayette",
							   # "types" : [ "locality", "political" ]
							# },
							# {
							   # "long_name" : "Wabash",
							   # "short_name" : "Wabash",
							   # "types" : [ "administrative_area_level_3", "political" ]
							# },
							# {
							   # "long_name" : "Tippecanoe County",
							   # "short_name" : "Tippecanoe County",
							   # "types" : [ "administrative_area_level_2", "political" ]
							# },
							# {
							   # "long_name" : "Indiana",
							   # "short_name" : "IN",
							   # "types" : [ "administrative_area_level_1", "political" ]
							# },
							# {
							   # "long_name" : "United States",
							   # "short_name" : "US",
							   # "types" : [ "country", "political" ]
							# },
							# {
							   # "long_name" : "47906",
							   # "short_name" : "47906",
							   # "types" : [ "postal_code" ]
							# }
						 # ],
						 # "formatted_address" : "240 Northwestern Avenue, West Lafayette, IN 47906, USA",
						 # "geometry" : {
							# "bounds" : {
							   # "northeast" : {
								  # "lat" : 40.4262752,
								  # "lng" : -86.9085348
							   # },
							   # "southwest" : {
								  # "lat" : 40.426266,
								  # "lng" : -86.9085487
							   # }
							# },
							# "location" : {
							   # "lat" : 40.4262752,
							   # "lng" : -86.9085348
							# },
							# "location_type" : "RANGE_INTERPOLATED",
							# "viewport" : {
							   # "northeast" : {
								  # "lat" : 40.4276195802915,
								  # "lng" : -86.9071927697085
							   # },
							   # "southwest" : {
								  # "lat" : 40.4249216197085,
								  # "lng" : -86.90989073029151
							   # }
							# }
						 # },
						 # "partial_match" : true,
						 # "place_id" : "EjYyNDAgTm9ydGh3ZXN0ZXJuIEF2ZW51ZSwgV2VzdCBMYWZheWV0dGUsIElOIDQ3OTA2LCBVU0E",
						 # "types" : [ "street_address" ]
					  # }
				   # ],
				   # "status" : "OK"
				# }
				# '''
	# Geocode = json.loads(Geocode)
	# print(Geocode_count)
	Geocode_count += 1
	coordinates = Geocode['results'][0]['geometry']['location']
	time.sleep(0.25)
	return(coordinates)


Google_directions_count = 0
Google_directions_cache = {}

def get_Google_Direction(start, end, departure_time = 1442419259):
	# Google Format: Lat,Lon
	# start = "40.4254466548828,-86.9257054880682"
	# end = "40.4272692160171,-86.9222226394548"
	# wed_1200 = 1441209659
	# wed_0730 = 1441193459	# for 8 Willowbrook Klondike Express AM
	# wed_1645 = 1441226759	# for 8 Willowbrook Klondike Express PM
	# wed_1800 = 1441231259	# for 14 Black Loop
	# sat_1200 = 1441468859	# for 5B Northwestern Saturday Inbound
	# sat_1830 = 1441491659	# for 1B Salisbury Evening Saturday Inbound
	# sat_2300 = 1441508459	# for 18 NightRider
	
	# global steps
	this_steps = []
	# global stop_to_stop
	global Google_directions_count
	global Google_directions_cache
	url = 'https://maps.googleapis.com/maps/api/directions/json?%s' % urllib.parse.urlencode((
				('origin', start),
				('destination', end),
				# ('mode', 'drive'),
				('mode', 'transit'),
				('key','AIzaSyDM2N6wqPbDSCTsPzuP3PAkTVA7sXC00wM'),
				('departure_time',departure_time),
				('transitOptions', ['bus']),
				# ('routingPreference ', 'LESS_WALKING'),
				('routingPreference ', 'FEWER_TRANSFERS'),
				('unit_system', 0),
				('alternatives','true'),
				('sensor','false')
	 ))
	if url not in Google_directions_cache:
		result = json.loads(urllib.request.urlopen(url).read().decode('utf-8'))
		Google_directions_count += 1
		if result['status'] == 'OK':
			Google_directions_cache[url] = result
		else:
			print('Google Direction Error')
			return([])
			# url = 'https://maps.googleapis.com/maps/api/directions/json?%s' % urllib.parse.urlencode((
						# ('origin', start),
						# ('destination', end),
						# ('mode', 'drive'),
						# # ('mode', 'transit'),
						# # ('key','AIzaSyDM2N6wqPbDSCTsPzuP3PAkTVA7sXC00wM'),
						# # ('departure_time',time),
						# # ('transitOptions', ['bus']),
						# # ('routingPreference ', 'FEWER_TRANSFERS'),
						# ('unit_system', 0),
						# ('alternatives','true'),
						# ('sensor','false')
			 # ))
			# Google_directions_cache[url] = result
	result = Google_directions_cache[url]
	
	for route in result['routes']:
		for leg in route['legs']:
			for step in leg['steps']:
				if step['travel_mode'] == 'TRANSIT': # and step['transit_details']['num_stops'] == 1:
					this_step = {}
					this_step['distance'] = step['distance']['value']	# meters
					this_step['polyline'] = step['polyline']['points']
					this_step['start'] = step['transit_details']['departure_stop']
					this_step['end'] = step['transit_details']['arrival_stop']
					# this_step['end'] = {'Lon':step['end_location']['lng'],'Lat':step['end_location']['lat']}
					# this_step['duration'] = step['transit_details']['arrival_time']['value'] - step['transit_details']['departure_time']['value']	# seconds
					this_step['duration'] = step['duration']['value']	# seconds
					this_step['route_ID'] = step['transit_details']['line']['short_name']
					this_steps.append(this_step)
					# {'distance': {'value': 3188, 'text': '2.0 mi'}, 
					# 'start_location': {'lng': -86.9140218, 'lat': 40.4240009}, 
					# 'polyline': {'points': '_ivuFrknqOPqIzIWHyJ{EImR?uGLjEkGN}CHwL`AmM`CwPx@gIb@y`@PqAr@i@x@@pDfDzA\\dNJ@~B'}, 
					# 'transit_details': {
					# 'departure_time': {'value': 1440599520,'time_zone': 'America/Indianapolis', 'text': '10:32am'}, 
					# 'num_stops': 6, 
					# 'arrival_stop': {'location': {'lng': -86.8948909, 'lat': 40.4206938}, 'name': 'CityBusCenter: BUS215'}, 
					# 'arrival_time': {'value': 1440600000, 'time_zone': 'America/Indianapolis', 'text': '10:40am'}, 
					# 'line': {'name': 'Purdue West', 'vehicle': {'name': 'Bus', 'type': 'BUS', 'icon': '//maps.gstatic.com/mapfiles/transit/iw2/6/bus.png'}, 'short_name': '4B', 'agencies': [{'name': 'CityBus', 'phone': '1 765-742-7433', 'url': 'http://www.gocitybus.com/'}], 'text_color': '#ffffff', 'color': '#006400'}, 
					# 'departure_stop': {'location': {'lng': -86.9140218, 'lat': 40.4240009}, 'name': 'State St & Marsteller St (SW Corner): BUS313SW'}, 
					# 'headsign': 'Purdue West to Campus & CityBus Center'}, 
					# 'html_instructions': 'Bus towards PurdueWest to Campus & CityBus Center', 
					# 'duration': {'value': 480, 'text': '8 mins'},
					# 'end_location': {'lng': -86.8948909, 'lat': 40.4206938}, 
					# 'travel_mode': 'TRANSIT'}
	return(this_steps)

# a = {'Lon':'0.652230', 'Lat':'100.405892'}
# b = {'Lon':'0.652457', 'Lat':'100.406192'}


# for route in routes:
	# for (i,stop) in enumerate(route['stops'],1):
		# print(stop,':',dist(stops[route['stops'][0]], stops[stop]))
	# print('\n',route['ID'])
	# _ = sys.stdin.readline()

# loops need to append fist stop to the end of ['stops']: 8, 12, 13, 16, 17, 20, 23
# loops already complete: 14, 15, 18, 19, 21, 27


# loops = ['8','12','13','14','15','16','17','18','19','20','21','23','27']

def get_polyline(start,end):
	if start=='BUS373':
		start_address = 'Tippecanoe Mall Entrance E: BUS373'
	elif start=='BUS215':
		start_address = 'CityBus Center: BUS215'
	else:
		start_address = ','.join([stops[start]['Lat'], stops[start]['Lon']])
	if end=='BUS373':
		end_address = 'Tippecanoe Mall Entrance E: BUS373'
	elif end=='BUS215':
		end_address = 'CityBus Center: BUS215'
	else:
		end_address = ','.join([stops[end]['Lat'], stops[end]['Lon']])
	this_steps = get_Google_Direction(start_address, end_address, departure_time)
	for this_step in this_steps:
		if ( this_step['route_ID'] == route['ID'] or
			(this_step['route_ID'] == '1B' and route['ID'] == '1A')):	# Wrong label in Google Direction
			if this_step['start']['name'].endswith(start) and this_step['end']['name'].endswith(end):
				return(this_step['polyline'])
			elif start=='BUS373' and this_step['start']['name'].endswith('BUS676') and this_step['end']['name'].endswith(end):
				# error in Google Direction planning: cannot start with BUS373 on line 3
				return(encode([(stops['BUS373']['Lat'],stops['BUS373']['Lon'])]+decode(this_step['polyline'])))	# add 'BUS373' manually
			elif end=='BUS403' and this_step['end']['name'].endswith('BUS641') and this_step['start']['name'].endswith(start):
				# error in Google Direction planning: cannot start with BUS403 on line 1B
				return(encode(decode(this_step['polyline']) + decode('}c}uFl`sqOmAdMfBdAcAwA~A}NWsF}@iEhIoF')))	# add 'BUS403' to 'BUS641' manually
	print(this_step['start']['name'], '\n', this_step['end']['name'])
	print(this_step['route_ID'],':', this_step['distance'],'m', this_step['duration'],'s\n')
	raise(Exception('Stops not match'))

def get_polyline_with_middlepoint(start, middle, end):
	dist(stops[start],stops[middle])>300
	x = get_polyline(start,middle)
	
	dist(stops[middle],stops[end])>300
	y=get_polyline(middle,end)
	
	return(encode(decode(x)+decode(y)))


from math import sin, cos, sqrt, atan2, radians

def dist(a,b):
	'''the distance in meters between a & b (coordinates)'''
	# return((float(a['Lon'])-float(b['Lon']))**2+(float(a['Lat'])-float(b['Lat']))**2)
	
	# http://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude-python
	# approximate radius of earth in meters
	# using EPSG:3857 as earth model https://en.wikipedia.org/wiki/Web_Mercator#WKT_Definition
	R = 6378137.298257223563
	
	lat1 = radians(float(a['Lat']))
	lon1 = radians(float(a['Lon']))
	lat2 = radians(float(b['Lat']))
	lon2 = radians(float(b['Lon']))
	
	dlon = lon2 - lon1
	dlat = lat2 - lat1
	
	a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
	c = 2 * atan2(sqrt(a), sqrt(1 - a))
	
	return(R * c)

# a = {'Lat':52.2296756, 'Lon':21.0122287}
# b = {'Lat':52.406374, 'Lon':16.9251681}
# dist(a,b)

# a = {'Lat':5, 'Lon':-5}
# b = {'Lat':76, 'Lon':-26}
# dist(a,b)


# def distToSegment(p, v, w)
	# var l2 = dist(v, w);
	# if (l2 == 0) return dist(p, v);
	# var t = ((p['Lon'] - v['Lon']) * (w['Lon'] - v['Lon']) + (p['Lat'] - v['Lat']) * (w['Lat'] - v['Lat'])) / l2;
	# if (t < 0) return dist(p, v);
	# if (t > 1) return dist(p, w);
	# return dist(p, { x: v['Lon'] + t * (w['Lon'] - v['Lon']),
					# y: v['Lat'] + t * (w['Lat'] - v['Lat']) })

def dist_to_line(x,a,b):
	'''the distance in meters from x to line (a,b) (all in coordinates)'''
	# x_a = dist(x,a)
	# x_b = dist(x,b)
	# mid = {'Lon':(a['Lon']+b['Lon'])/2, 'Lat':(a['Lat']+b['Lat'])/2}
	# if x_a == x_b:
		# return((x_a+x_b)/2, mid)
	# elif x_a < x_b:
		# return(dist_to_line(x,a,mid))
	# elif x_a > x_b:
		# return(dist_to_line(x,mid,b))
	while True:
		x_a = dist(x,a)
		x_b = dist(x,b)
		mid = {'Lon':(a['Lon']+b['Lon'])/2, 'Lat':(a['Lat']+b['Lat'])/2}
		if abs(x_a - x_b)<0.1:
			return((x_a+x_b)/2, mid)
		elif x_a < x_b:
			b = mid
		else:
			a = mid

# x = {'Lat':52.3, 'Lon':18.2}
# a = {'Lat':52.2296756, 'Lon':21.0122287}
# b = {'Lat':52.406374, 'Lon':16.9251681}
# dist_to_line(x,a,b)

near_by = 10	# 10 meters

def path_length(line):
	length = 0
	for a,b in zip(line[:-1],line[1:]):
		length += dist(a,b)
	return(length)


class Line:
	"""
	Store the information of a bus Line
	Initialize using Line(url)
	
	example
	url: http://www.gocitybus.com/Maps-Schedules/ID/16/5A-Happy-Hollow
	ID: 5A
	name: Happy Hollow
	map: http://www.gocitybus.com/Portals/0/Maps/CityBus-5A-Happy-Hollow-map.jpg
	schedule: http://www.gocitybus.com/Portals/0/Schedules/CityBus-5A-Happy-Hollow-schedule.gif
	bus_stops: list of stops
	
	"""
	
	def __init__(self, url):
		self.url = url
		self.get_name()
		self.bus_stops = {}
		self.get_route()
				
	def get_name(self):
		name = self.url.split(r'/')[-1].replace('-',' ')
		ID = name.split()[0]
		
		if ID[0].isnumeric():	# named by number
			name = ' '.join(name.split()[1:])
		
		if ID == '6A': # '6A South 4th Street to Walmart South'
			name = 'South 4th Street'
		
		if ID == '7': # '7 South Street (formerly State Road 26 E)'
			name = 'South Street'
		
		if ID == '13': # '13 Silver Loop (Click to see more)'
			name = 'Silver Loop'
		
		if ID == '27': # '27 Outer Loop (REVERSE DIRECTION)'
			name = 'Outer Loop'
		
		if ID == 'The': # 'The Connector FREE FOR ALL'
			ID = '23'
			name = 'Connector Line'
		
		self.ID = ID
		self.name = name
	
	def get_route(self):
		page_soup = get_page(self.url)
		table_names = {name.attrs['href'].split('#')[1]:name.text for name in page_soup.find('ul', attrs={'class':"nav nav-tabs"}).find_all('a') if isinstance(name, bs4.element.Tag)}
		# if not 'tab1' in table_names.keys(): # bug on http://www.gocitybus.com/Maps-Schedules/ID/33/14-Black-Loop
		if not 'Schedule' in table_names.values(): # bug on http://www.gocitybus.com/Maps-Schedules/ID/33/14-Black-Loop
			table_names['tab1'] = 'Schedule'
		tables = {table.attrs['id']:table for table in page_soup.find('div', attrs={'class':"tab-content"}).children if isinstance(table, bs4.element.Tag)}
		for tab,name in table_names.items(): # bug on http://www.gocitybus.com/Maps-Schedules/ID/33/14-Black-Loop
			if name == 'Map' and tab not in tables:
				del table_names[tab]
				self.map = get_url_base(page_soup)+ page_soup.find('ul',attrs={'class':'nav-tabs'}).img.attrs['src']	# bug on http://www.gocitybus.com/Maps-Schedules/ID/9/2A-Schuyler
				break
		tables = {table_names[tab]:tables[tab] for tab in table_names}
		
		def parse_stops(tab):
			stops = {}
			# more than 3 cols (eliminate bad tables) http://www.gocitybus.com/Maps-Schedules/ID/16/5A-Happy-Hollow
			# and less that 5 http://www.gocitybus.com/Maps-Schedules/ID/19/The-Connector-FREE-FOR-ALL
			# and not empty (http://www.gocitybus.com/Maps-Schedules/ID/17/3-Lafayette-Square   Inbound)
			lines = [tr for tr in tab.find_all('tr') if len(tr.find_all('td')) in (3,4,5) and text(tr.text) != '']
			
			header = [text(col.text) for col in lines[0].find_all('td')]	  # header = ['MyRide QuickCode', 'STOP DESCRIPTION', 'Google Transit']
			try:
				QuickCode_id = header.index('MyRide QuickCode')
				StopDesc_id = header.index('STOP DESCRIPTION')
				# GoogleUrl_id = header.index('Google Transit')
				GoogleUrl_id = [col.startswith('Google Transit') for col in header].index(True)	# bug on http://www.gocitybus.com/Maps-Schedules/ID/20/13-Silver-Loop-Click-to-see-more
			except ValueError:
				# http://www.gocitybus.com/Maps-Schedules/ID/40/27-Outer-Loop-REVERSE-DIRECTION
				QuickCode_id = header.index([col for col in header if col.startswith('BUS')][0])
				StopDesc_id = QuickCode_id+1
				GoogleUrl_id = QuickCode_id+2
				lines = ['']+lines	# include the first row in bus_stops
			
			for (i,line) in enumerate(lines[1:],1):
				cols = line.find_all('td')
				QuickCode = text(cols[QuickCode_id].text)
				# if QuickCode == 'BUS375W':
					# 1+''
				StopDesc = text(cols[StopDesc_id].text)
				if cols[GoogleUrl_id].text == '' or cols[GoogleUrl_id].a == None:  # http://www.gocitybus.com/Maps-Schedules/ID/4/1A-Market-Square  "Coming soon"/"NEW" has no <a></a>
					stops[i] = {'QuickCode': QuickCode, 'StopDesc': StopDesc}
				else:
					# Get Google Map URL from webpage link
					GoogleUrl = cols[GoogleUrl_id].a.attrs['href']					
					# resolve two types of Google Map URLs
					if GoogleUrl.startswith('http://maps.google.com/maps?t=h&ie=UTF8&ll='):
						# http://maps.google.com/maps?t=h&ie=UTF8&ll=40.420845,-86.9232137157448&spn=0.001369,0.001985&z=18&iwloc=lyrftr:unknown,0x8812e2c7e299d379:0x60227fc4ef7b3d60,
						Lat,Lon = [p[3:].split(',') for p in GoogleUrl.split('&') if p[:3] == 'll='][0]
						GoogleUrl = GoogleUrl.replace('?t=h&ie=UTF8&ll=','?ll=')
					else:
						# https://www.google.com/maps/place/Creasy+Ln+&+Bonlou+(Menards+Entrance):+BUS941NW/@40.3873633079149,-86.8404313528795,18z
						Lat,Lon = GoogleUrl.split('@')[1].split(',')[:2]
					stops[i] = {'QuickCode': QuickCode, 'StopDesc': StopDesc, 'GoogleUrl': GoogleUrl, 'Lat': Lat, 'Lon': Lon}
					# print(Lat, Lon)
			
			return stops
		
		for tab in tables:			  
			print(tab)
			
			if tab == 'Inbound Bus Stops':
				self.bus_stops['inbound'] = parse_stops(tables[tab])
			elif tab == 'Outbound Bus Stops':
				self.bus_stops['outbound'] = parse_stops(tables[tab])
			elif tab == 'Bus Stops':
				self.bus_stops['round'] = parse_stops(tables[tab])
			elif tab == 'Evening / Saturday Inbound':	# 1B
				self.bus_stops['eve_sat_inbound'] = parse_stops(tables[tab])
			elif tab == 'Evening / Saturday Outbound':	# 1B
				self.bus_stops['eve_sat_outbound'] = parse_stops(tables[tab])
			elif tab == 'Weekday / Sunday Inbound':		# 1B
				self.bus_stops['week_sun_inbound'] = parse_stops(tables[tab])
			elif tab == 'Weekday / Sunday Outbound':	# 1B
				self.bus_stops['week_sun_outbound'] = parse_stops(tables[tab])
			elif tab == 'Inbound M-F':	# 5B
				self.bus_stops['week_inbound'] = parse_stops(tables[tab])
			elif tab == 'Outbound M-F': # 5B
				self.bus_stops['week_outbound'] = parse_stops(tables[tab])
			elif tab == 'Inbound Sat':	# 5B
				self.bus_stops['sat_inbound'] = parse_stops(tables[tab])
			elif tab == 'Outbound Sat': # 5B
				self.bus_stops['sat_outbound'] = parse_stops(tables[tab])
			elif tab == 'Map':
				self.map = get_url_base(page_soup)+tables['Map'].p.img.attrs['src']
			elif tab == 'Schedule':
				self.schedule = get_url_base(page_soup)+tables['Schedule'].p.img.attrs['src']
			elif tab == 'Lefts & Rights':
				pass
			else:
				print('=============del ',tab)
				# print(tables[tab].text)
		
		# complete the loops unconnected
		if self.ID in ['8', '12', '13', '16', '17', '20', '23']:
			i = len(self.bus_stops['round'])
			self.bus_stops['round'][str(i+1)] = self.bus_stops['round'][1]
	
	def to_dict(self):
		bus_operation_time = {
		'1A_inbound':{'Weekday':('06:14','23:40'), 'Sat':('07:02','19:40'), 'Sun':('10:02','18:40')},
		'1A_outbound':{'Weekday':('06:10','00:23'), 'Sat':('06:45','19:23'), 'Sun':('09:45','18:23')},
		'1B_eve_sat_inbound':{'Weekday':('18:15','00:40'), 'Sat':('07:11','19:40'), 'Sun':('00:00','00:00')},
		'1B_eve_sat_outbound':{'Weekday':('18:15','00:11'), 'Sat':('06:45','19:11'), 'Sun':('00:00','00:00')},
		'1B_week_sun_inbound':{'Weekday':('06:10','18:15'), 'Sat':('00:00','00:00'), 'Sun':('09:11','19:40')},
		'1B_week_sun_outbound':{'Weekday':('06:10','18:15'), 'Sat':('00:00','00:00'), 'Sun':('08:45','19:11')},
		'2A_inbound':{'Weekday':('06:25','18:10'), 'Sat':('07:55','18:10'), 'Sun':('00:00','00:00')},
		'2A_outbound':{'Weekday':('06:15','17:55'), 'Sat':('07:45','17:55'), 'Sun':('00:00','00:00')},
		'2B_inbound':{'Weekday':('06:25','18:10'), 'Sat':('07:25','17:55'), 'Sun':('00:00','00:00')},
		'2B_outbound':{'Weekday':('06:15','17:40'), 'Sat':('07:15','17:25'), 'Sun':('00:00','00:00')},
		'3_inbound':{'Weekday':('06:20','21:40'), 'Sat':('06:41','19:10'), 'Sun':('11:11','18:40')},
		'3_outbound':{'Weekday':('06:15','21:11'), 'Sat':('06:15','18:41'), 'Sun':('10:45','18:11')},
		'4A_inbound':{'Weekday':('06:23','23:40'), 'Sat':('06:23','21:40'), 'Sun':('10:23','18:40')},
		'4A_outbound':{'Weekday':('06:15','23:02'), 'Sat':('06:45','21:02'), 'Sun':('09:45','18:02')},
		'4B_inbound':{'Weekday':('06:32','23:40'), 'Sat':('08:41','19:40'), 'Sun':('10:11','18:40')},
		'4B_outbound':{'Weekday':('06:15','00:11'), 'Sat':('08:15','19:11'), 'Sun':('09:45','18:30')},
		'5A_inbound':{'Weekday':('05:50','18:37'), 'Sat':('00:00','00:00'), 'Sun':('00:00','00:00')},
		'5A_outbound':{'Weekday':('06:20','19:30'), 'Sat':('00:00','00:00'), 'Sun':('00:00','00:00')},
		'5B_week_inbound':{'Weekday':('06:00','19:20'), 'Sat':('00:00','00:00'), 'Sun':('00:00','00:00')},
		'5B_week_outbound':{'Weekday':('06:07','19:00'), 'Sat':('00:00','00:00'), 'Sun':('00:00','00:00')},
		'5B_sat_inbound':{'Weekday':('00:00','00:00'), 'Sat':('07:40','18:10'), 'Sun':('00:00','00:00')},
		'5B_sat_outbound':{'Weekday':('00:00','00:00'), 'Sat':('07:15','17:40'), 'Sun':('00:00','00:00')},
		'6A_inbound':{'Weekday':('06:36','21:40'), 'Sat':('07:36','18:40'), 'Sun':('10:06','18:40')},
		'6A_outbound':{'Weekday':('06:15','21:06'), 'Sat':('07:15','18:06'), 'Sun':('09:45','18:06')},
		'6B_inbound':{'Weekday':('06:29','18:40'), 'Sat':('07:29','18:10'), 'Sun':('00:00','00:00')},
		'6B_outbound':{'Weekday':('06:15','18:29'), 'Sat':('07:15','17:59'), 'Sun':('00:00','00:00')},
		'7_inbound':{'Weekday':('06:16','00:40'), 'Sat':('07:16','18:40'), 'Sun':('09:16','18:40')},
		'7_outbound':{'Weekday':('06:15','00:16'), 'Sat':('06:45','18:16'), 'Sun':('08:45','18:16')},
		'8_AM':{'Weekday':('07:05','08:50'), 'Sat':('00:00','00:00'), 'Sun':('00:00','00:00')},
		'8_PM':{'Weekday':('16:15','18:00'), 'Sat':('00:00','00:00'), 'Sun':('00:00','00:00')},
		'12_round':{'Weekday':('06:57','18:12'), 'Sat':('00:00','00:00'), 'Sun':('00:00','00:00')},
		'13_round':{'Weekday':('07:05','18:15'), 'Sat':('00:00','00:00'), 'Sun':('00:00','00:00')},
		'14_round':{'Weekday':('17:25','23:45'), 'Sat':('00:00','00:00'), 'Sun':('17:25','23:45')},
		'15_round':{'Weekday':('07:00','18:00'), 'Sat':('00:00','00:00'), 'Sun':('00:00','00:00')},
		'16_round':{'Weekday':('07:05','18:10'), 'Sat':('00:00','00:00'), 'Sun':('00:00','00:00')},
		'17_round':{'Weekday':('07:00','18:00'), 'Sat':('00:00','00:00'), 'Sun':('00:00','00:00')},
		'18_round':{'Weekday':('00:00','00:00'), 'Sat':('21:55','01:55'), 'Sun':('00:00','00:00')},
		'19_round':{'Weekday':('07:15','18:03'), 'Sat':('00:00','00:00'), 'Sun':('00:00','00:00')},
		'20_round':{'Weekday':('07:25','17:50'), 'Sat':('00:00','00:00'), 'Sun':('00:00','00:00')},
		'21_round':{'Weekday':('07:07','21:27'), 'Sat':('21:27','02:12'), 'Sun':('07:07','02:12')},	# Special treatment: special hours Thur and Fri: stored in Sun http://www.gocitybus.com/Maps-Schedules/ID/31/21-The-Avenue-North-and-South
		'27_round':{'Weekday':('07:05','18:03'), 'Sat':('00:00','00:00'), 'Sun':('00:00','00:00')},
		'23_round':{'Weekday':('07:25','18:00'), 'Sat':('00:00','00:00'), 'Sun':('00:00','00:00')}	# http://www.gocitybus.com/Maps-Schedules/ID/19/The-Connector-FREE-FOR-ALL
		}
		bus_route_name = {
		'inbound': ' Inbound',
		'outbound': ' Outbound',
		'round': '',
		'eve_sat_inbound': ' Evening Saturday Inbound',
		'eve_sat_outbound': ' Evening Saturday Outbound',
		'week_sun_inbound': ' Weekday Sunday Inbound',
		'week_sun_outbound': ' Weekday Sunday Outbound',
		'week_inbound': ' Weekday Inbound',
		'week_outbound': ' Weekday Outbound',
		'sat_inbound': ' Saturday Inbound',
		'sat_outbound': ' Saturday Outbound'
		}
		
		if self.ID == '8':
			return([{'ID':self.ID,
					 'name':self.name+' AM',
					 'stops':[self.bus_stops['round'][stop]['QuickCode'] for stop in self.bus_stops['round']], 
					 'distance':[],
					 'duration':[[] for stop in self.bus_stops['round']], 
					 'operation_time':bus_operation_time['8_AM'],
					 'map':self.map,
					 'schedule':self.schedule},
					{'ID':self.ID,
					 'name':self.name+' PM',
					 'stops':[self.bus_stops['round'][stop]['QuickCode'] for stop in self.bus_stops['round']], 
					 'distance':[],
					 'duration':[[] for stop in self.bus_stops['round']],  
					 'operation_time':bus_operation_time['8_PM'],
					 'map':self.map,
					 'schedule':self.schedule}
					 ])
		
		routes = []
		for route in self.bus_stops:
			routes.append({'ID':self.ID,
						   'name':self.name+bus_route_name[route],
						   'stops':[self.bus_stops[route][stop]['QuickCode'] for stop in self.bus_stops[route]], 
						   'distance':[],	# distance in meters
						   'duration':[[] for stop in self.bus_stops[route]], 	# distance in seconds
						   'operation_time':bus_operation_time[self.ID+'_'+route],
						   'map':self.map,
						   'schedule':self.schedule})
		
		return routes



url = 'http://www.gocitybus.com/Maps-Schedules/'
page_soup = get_page(url)
links = [link for link in get_links(page_soup) if r'Maps-Schedules/ID' in link and 'System-Map' not in link and 'Campus-Loops-Map' not in link]
# pprint(sorted([link.split(r'/')[-1] for link in links]))
# len(links)

# names = [link.split(r'/')[-1].replace('-',' ') for link in links]
# IDs = [name.split()[0] for name in names]
# names = [name.split(r'-')[0] for name in names]

lines = []
for link in links:
	print(link)
	# if link.endswith('Green-Line'): # Revised map coming soon. http://gocitybus.com/Maps-Schedules/ID/37/Green-Line
		# continue
	# if link.endswith('Red-Line'): # Coming soon. http://www.gocitybus.com/Maps-Schedules/ID/35/Red-Line
		# continue
	if link.endswith('-Line'): # No Stops Info. http://www.gocitybus.com/Maps-Schedules/ID/36/Purple-Line
		continue
	lines.append(Line(link))

stops = {}
routes = []
for line in lines:
	# print(line.ID, [r for r in dir(line) if 'bound' in r or 'stops' in r])
	bus_stops = [line.bus_stops[route][stop_num] for route in line.bus_stops for stop_num in line.bus_stops[route]]
	for stop in bus_stops:
		if len(stop['QuickCode'])>10:
			1+''
		if stop['QuickCode'] in stops:
			if stop['QuickCode'] == 'BUS220NW' and line.ID == '16':	# http://www.gocitybus.com/Maps-Schedules/ID/23/16-Bronze-Loop 
				pass
			else:
				stops[stop['QuickCode']].update(stop)
		else:
			stops[stop['QuickCode']] = stop
	routes.extend(line.to_dict())

# pprint([(r['ID'],r['stops'][0],r['stops'][-1]) for r in routes])

routes.sort(key=lambda r:(int(''.join(filter(lambda x:x.isnumeric(),r['ID']))), ''.join(filter(lambda x:x.isalpha(),r['ID'])), r['name']))
# pprint([(r['ID'],r['name']) for r in routes])

# correct stops
for route in routes:
	if route['ID'] == '1A' and route['name'] == 'Market Square Inbound':
		route['stops'] = ["BUS373", "BUS676", "BUS671", "BUS437E", "BUS772", "BUS923", "BUS992", "BUS770SE", "BUS681", "BUS773", "BUS774S", "BUS766E", "BUS765NE", "BUS200N", "BUS775NE", "BUS539", "BUS763E", "BUS461", "BUS762", "BUS193W", "BUS302N", "BUS812", "BUS759E", "BUS920SE", "BUS341SE", "BUS757SE", "BUS407", "BUS778", "BUS526NE", "BUS780", "BUS231N", "BUS781", "BUS278NE", "BUS245NE", "BUS245NW", "BUS230N", "BUS330NE", "BUS750", "BUS508NE", "BUS296", "BUS422W", "BUS143", "BUS422E", "BUS960", "BUS987NW", "BUS292NW", "BUS380NW", "BUS367NW", "BUS783NW", "BUS220NW", "BUS748", "BUS410NE", "BUS492", "BUS215"]
	elif route['ID'] == '1A' and route['name'] == 'Market Square Outbound':
		route['stops'] = ["BUS215", "BUS744", "BUS410SW", "BUS745", "BUS746", "BUS328", "BUS380SE", "BUS292SE", "BUS987SE", "BUS512", "BUS422W", "BUS143", "BUS422E", "BUS508W", "BUS921", "BUS330SW", "BUS230S", "BUS245SW", "BUS245SE", "BUS278SW", "BUS453", "BUS231S", "BUS753", "BUS526SW", "BUS513", "BUS281", "BUS757NW", "BUS341NW", "BUS920NW", "BUS759W", "BUS820", "BUS302S", "BUS771", "BUS763W", "BUS775SW", "BUS200S", "BUS765NW", "BUS766W", "BUS774N", "BUS768", "BUS769NW", "BUS770NW", "BUS919W", "BUS499N", "BUS499", "BUS717", "BUS376", "BUS672", "BUS673", "BUS373"]
	elif route['ID'] == '1B' and route['name'] == 'Salisbury Weekday Sunday Outbound':
		route['stops'] = ["BUS215", "BUS396", "BUS287", "BUS122", "BUS156", "BUS581", "BUS304", "BUS433", "BUS271", "BUS313NE", "BUS560NE", "BUS389", "BUS563", "BUS530S", "BUS634SW", "BUS635SW", "BUS291SW", "BUS636SE", "BUS333SE", "BUS493", "BUS637SE", "BUS337NE", "BUS638", "BUS365SE", "BUS633SE", "BUS484", "BUS610", "BUS314", "BUS131E", "BUS138W", "BUS133N", "BUS541", "BUS218NE", "BUS455N", "BUS511NW", "BUS137", "BUS641", "BUS223", "BUS403"]
	elif route['ID'] == '1B' and route['name'] == 'Salisbury Evening Saturday Outbound':
		route['stops'] = ["BUS215", "BUS396", "BUS287", "BUS122", "BUS156", "BUS581", "BUS304", "BUS433", "BUS271", "BUS313NE", "BUS560NE", "BUS389", "BUS563", "BUS530S", "BUS634SW", "BUS635SW", "BUS291SW", "BUS636SE", "BUS333SE", "BUS493", "BUS637SE", "BUS337NE", "BUS638", "BUS365SE", "BUS633SE", "BUS484", "BUS604", "BUS609", "BUS925", "BUS595E", "BUS144E", "BUS926", "BUS267N", "BUS643", "BUS591N", "BUS593", "BUS138W", "BUS133N", "BUS541", "BUS218NE", "BUS455N", "BUS511NW", "BUS137", "BUS641", "BUS223", "BUS403"]
	elif route['ID'] == '3' and route['name'] == 'Lafayette Square Outbound':
		route['stops'] = ["BUS215", "BUS265", "BUS329", "BUS351", "BUS659", "BUS661", "BUS206", "BUS939", "BUS391NW", "BUS723", "BUS940", "BUS724W", "BUS495", "BUS725W", "BUS256S", "BUS726S", "BUS727", "BUS378SW", "BUS414", "BUS311", "BUS331", "BUS963", "BUS469S", "BUS315S", "BUS729", "BUS428S", "BUS730", "BUS416", "BUS155", "BUS344", "BUS807", "BUS865", "BUS354E", "BUS707S", "BUS449S", "BUS181", "BUS708", "BUS301S", "BUS710S", "BUS711S", "BUS404SW", "BUS142S", "BUS941SE", "BUS499", "BUS717", "BUS376", "BUS672", "BUS673", "BUS373"]
	elif route['ID'] == '3' and route['name'] == 'Lafayette Square Inbound':
		route['stops'] = ["BUS373", "BUS676", "BUS437W", "BUS719", "BUS941NW", "BUS142N", "BUS404NE", "BUS711N", "BUS710N", "BUS301N", "BUS720", "BUS449N", "BUS735E", "BUS736", "BUS731E", "BUS737", "BUS942", "BUS428N", "BUS315N", "BUS469N", "BUS739", "BUS187SE", "BUS467", "BUS466W", "BUS378NW", "BUS726N", "BUS256N", "BUS725E", "BUS724E", "BUS740", "BUS391NE", "BUS158", "BUS305", "BUS309", "BUS242", "BUS243N", "BUS674", "BUS675", "BUS188", "BUS214", "BUS215"]
	elif route['ID'] == '4A' and route['name'] == 'Tippecanoe Mall Outbound':
		route['stops'] = ["BUS215", "BUS265", "BUS329", "BUS351", "BUS659", "BUS661", "BUS206", "BUS939", "BUS391NW", "BUS444SW", "BUS482NW", "BUS947", "BUS216W", "BUS663SE", "BUS664SE", "BUS531SW", "BUS666", "BUS298", "BUS120", "BUS667", "BUS141", "BUS948", "BUS421SW", "BUS672", "BUS673", "BUS373"]
	elif route['ID'] == '4B' and route['name'] == 'Purdue West Klondike Outbound':
		route['stops'] = ["BUS215", "BUS396", "BUS287", "BUS122", "BUS156", "BUS581", "BUS304", "BUS433", "BUS271", "BUS313NE", "BUS547", "BUS520NE", "BUS898", "BUS517", "BUS566", "BUS501E", "BUS251E", "BUS906E", "BUS393", "BUS236E", "BUS103", "BUS106", "BUS463", "BUS308", "BUS300", "BUS905", "BUS498", "BUS904", "BUS195", "BUS268", "BUS481", "BUS464", "BUS204", "BUS317", "BUS342", "BUS170", "BUS283", "BUS179", "BUS390", "BUS250", "BUS137", "BUS403"]
	elif route['ID'] == '5A' and route['name'] == 'Happy Hollow Outbound':
		#pass	# no arrival info for some valid stops (5A both)
		route['stops'] = ["BUS111", "BUS439", "BUS332NW", "BUS345", "BUS313SW", "BUS154", "BUS184", "BUS135", "BUS950", "BUS951", "BUS602E", "BUS460", "BUS145E", "BUS600N", "BUS123E", "BUS605", "BUS599E", "BUS597E", "BUS361SE", "BUS595E", "BUS144E", "BUS926", "BUS613", "BUS936NE", "BUS614", "BUS615SE", "BUS616", "BUS927SE", "BUS928SE", "BUS929", "BUS930", "BUS931", "BUS932", "BUS933", "BUS928NE", "BUS927NW", "BUS617", "BUS618", "BUS619", "BUS620", "BUS621", "BUS153"]
	elif route['ID'] == '6A' and route['name'] == 'South 4th Street Inbound':
		route['stops'] = ["BUS893", "BUS889NW", "BUS887", "BUS889SE", "BUS791", "BUS880", "BUS881", "BUS875NE", "BUS916", "BUS917", "BUS883", "BUS884", "BUS870SE", "BUS990", "BUS354W", "BUS340N", "BUS705N", "BUS704N", "BUS767", "BUS702", "BUS700", "BUS336", "BUS343", "BUS239", "BUS222", "BUS208", "BUS974", "BUS975", "BUS976", "BUS258", "BUS653SW", "BUS907", "BUS910", "BUS652E", "BUS148", "BUS264E", "BUS121SE", "BUS979", "BUS912", "BUS424", "BUS657", "BUS911", "BUS310", "BUS991", "BUS356", "BUS165", "BUS172", "BUS185", "BUS188", "BUS214", "BUS215"]
	elif route['ID'] == '6B' and route['name'] == 'South 9th Street Outbound':
		route['stops'] = ["BUS215", "BUS265", "BUS329", "BUS351", "BUS698", "BUS683", "BUS253E", "BUS288", "BUS108", "BUS210", "BUS182", "BUS303", "BUS544NW", "BUS327SW", "BUS986S", "BUS198W", "BUS187NW", "BUS381", "BUS494", "BUS515", "BUS316", "BUS693W", "BUS679W", "BUS537S", "BUS521SW", "BUS682S"]
	elif route['ID'] == '7' and route['name'] == 'South Street Inbound':
		route['stops'] = ["BUS257", "BUS299", "BUS277N", "BUS386", "BUS406", "BUS806", "BUS377", "BUS193W", "BUS302N", "BUS811", "BUS475E", "BUS813E", "BUS552SE", "BUS793", "BUS382N", "BUS196W", "BUS507W", "BUS459NW", "BUS487W", "BUS116", "BUS542", "BUS545N", "BUS548NE", "BUS280N", "BUS798NE", "BUS797N", "BUS796N", "BUS794N", "BUS532NE", "BUS534N", "BUS549N", "BUS215"]
	elif route['ID'] == '12' and route['name'] == 'Gold Loop':
		route['stops'] = ["BUS217", "BUS456", "BUS249", "BUS543SE", "BUS319N", "BUS272N", "BUS483N", "BUS417NE", "BUS491E", "BUS470S", "BUS366", "BUS362E", "BUS201E", "BUS567", "BUS439", "BUS273", "BUS190", "BUS557", "BUS538", "BUS558", "BUS574", "BUS555", "BUS556", "BUS646", "BUS271", "BUS313NE", "BUS448", "BUS565N", "BUS560NW", "BUS547", "BUS520NE", "BUS289", "BUS470N", "BUS491W", "BUS417SW", "BUS217"]
	elif route['ID'] == '13' and route['name'] == 'Silver Loop':
		route['stops'] = ["BUS282NE", "BUS366", "BUS362E", "BUS201E", "BUS567", "BUS273", "BUS190", "BUS557", "BUS538", "BUS412", "BUS271", "BUS313NE", "BUS448", "BUS435", "BUS560NW", "BUS547", "BUS520NE", "BUS568", "BUS282NE"]
	elif route['ID'] == '14' and route['name'] == 'Black Loop':
		route['stops'] = ["BUS553", "BUS554W", "BUS562S", "BUS472S", "BUS509SW", "BUS213S", "BUS273", "BUS190", "BUS557", "BUS538", "BUS559", "BUS645", "BUS271", "BUS313NE", "BUS448", "BUS435", "BUS560NW", "BUS547", "BUS899", "BUS900", "BUS543NE", "BUS319N", "BUS272N", "BUS483N", "BUS417NE", "BUS346", "BUS282NE", "BUS366", "BUS362E", "BUS201E", "BUS509SE", "BUS472N", "BUS562N", "BUS554E", "BUS553"]
	elif route['ID'] == '15' and route['name'] == 'Tower Acres':
		route['stops'] = ["BUS553", "BUS554W", "BUS562S", "BUS472S", "BUS509SW", "BUS213S", "BUS273", "BUS190", "BUS557", "BUS538", "BUS412", "BUS271", "BUS313NE", "BUS448", "BUS565S", "BUS560NW", "BUS547", "BUS520NE", "BUS289", "BUS362E", "BUS201E", "BUS509SE", "BUS472N", "BUS562N", "BUS554E", "BUS553"]
	elif route['ID'] == '16' and route['name'] == 'Bronze Loop':
		route['stops'] = ["BUS152", "BUS960", "BUS987NW", "BUS292NW", "BUS380NW", "BUS367NW", "BUS783NW", "BUS220NW", "BUS748", "BUS410NE", "BUS492", "BUS564", "BUS519W", "BUS359", "BUS530N", "BUS557", "BUS538", "BUS950", "BUS402", "BUS360", "BUS143", "BUS422E", "BUS152"]
	elif route['ID'] == '18' and route['name'] == 'NightRider':
		route['stops'] = ["BUS553", "BUS554W", "BUS562S", "BUS472S", "BUS509SW", "BUS201W", "BUS362W", "BUS584NW", "BUS345", "BUS313SW", "BUS576", "BUS321", "BUS471", "BUS163", "BUS425S", "BUS229SW", "BUS400W", "BUS578", "BUS265", "BUS329", "BUS351", "BUS585", "BUS397SE", "BUS398", "BUS339", "BUS349", "BUS350", "BUS364", "BUS371", "BUS392", "BUS396", "BUS287", "BUS400E", "BUS229SE", "BUS425N", "BUS540", "BUS580E", "BUS581", "BUS304", "BUS433", "BUS271", "BUS313NE", "BUS560NE", "BUS389", "BUS486N", "BUS332N", "BUS107", "BUS362E", "BUS201E", "BUS509NE", "BUS472N", "BUS562N", "BUS554E", "BUS553"]
	elif route['ID'] == '19' and route['name'] == 'Inner Loop':
		route['stops'] = ["BUS249", "BUS543SE", "BUS440", "BUS324", "BUS570", "BUS448", "BUS565S", "BUS560NW", "BUS368", "BUS266", "BUS543NE", "BUS319N", "BUS272N", "BUS275", "BUS456", "BUS249"]
	elif route['ID'] == '21' and route['name'] == 'The Avenue North and South':
		pass
	elif route['ID'] == '27' and route['name'] == 'Outer Loop':
		route['stops'] = ["BUS249", "BUS543SE", "BUS440", "BUS324", "BUS598", "BUS320", "BUS154", "BUS184", "BUS295", "BUS111", "BUS286", "BUS413", "BUS201W", "BUS362W", "BUS470N", "BUS285", "BUS517", "BUS263", "BUS262", "BUS249"]
	route['duration'] = [[] for _ in route['stops']]
	for stop in route['stops']:
		StopDesc = {'BUS155':'Edgelea Elementary on 18th St',
					'BUS266':'Russell St and Harrison St NW Corner',
					'BUS281':'Shenandoah Drive at Munger Trail Crossing',
					'BUS289':'Jischke Dr and 3rd St SE Corner',
					'BUS299':'Meijer Ct and Meijer Dr (NE Corner)',
					'BUS302N':'SR 26 and Executive Dr West of',
					'BUS302S':'SR 26 and Executive Dr SE Corner',
					'BUS343':'McDonalds on Old 231',
					'BUS344':'Beck Ln and Cayuga Trail (NE Corner)',
					'BUS368':'SW of Russell St and State St',
					'BUS396':'2nd St and Main St (SW Corner)',
					'BUS407':'Shenandoah Dr at Munger Trail Crossing',
					'BUS412':'NW of Northwestern and Columbia',
					'BUS466W':'JR Hiatt Dr and 22nd St (NW Corner)',
					'BUS499N':'SR 38 and Creasy Ln West of',
					'BUS515':'Teal Rd and Crestview Ct NE Corner',
					'BUS521SW':'Beck Ln & Davis Dr (SW Corner)',
					'BUS537S':'Beck Ln & 9th St (Southeast of)',
					'BUS570':'Pao Hall on Marsteller St',
					'BUS679W':'Bishop Woods on 9th St (West Side)',
					'BUS681':'Amelia Ave and Creasy Ln NE Corner',
					'BUS693W':'9th St & Sarasota Dr (SW Corner)',
					'BUS772':'Northeast of Creasy Ln and SR 38',
					'BUS812':'Shenandoah Dr and Rome Dr NE Corner',
					'BUS820':'Shenandoah Dr and Rome Dr (West Side)',
					'BUS824':'Prophet Dr and Soldiers Home Rd (West)',
					'BUS919W':'St Elizabeth Hospital on CreasyNW Corner',
					'BUS923':'St Elizabeth Hospital on Creasy SE Corner',
					'BUS927NW':'Soldiers Home Rd & Broadview (NW Corner)',
					'BUS927SE':'Soldiers Home Rd & Broadview (SE Corner)',
					'BUS928NE':'Veterans Home Entrance (North Side)',
					'BUS928SE':'Veterans Home Entrance on Soldiers Home',
					'BUS929':'Lincoln Hall at Indiana Veterans Home',
					'BUS930':'Dehart Hall at Indiana Veterans Home',
					'BUS931':'Mitchell Hall at Indiana Veterans Home',
					'BUS932':'Pyle Hall at Indiana Veterans Home',
					'BUS933':'Ingersol Hall at Indiana Veterans Home',
					'BUS991':'South Tipp Park on 3rd St',
					'BUS992':'St Elizabeth Hospital'
					}
		if stop not in stops:
			stops[stop] = {'QuickCode':stop, 'StopDesc':StopDesc[stop]}


# stops['BUS820'] =  {'QuickCode':'BUS820', 'StopDesc':'Shenandoah Dr and Rome Dr (West Side)', 'url':get_stop_url('BUS820')}
# stops['BUS155'] =  {'QuickCode':'BUS155', 'StopDesc':'Edgelea Elementary on 18th St', 'url':get_stop_url('BUS155')}
# stops['BUS344'] =  {'QuickCode':'BUS344', 'StopDesc':'Beck Ln and Cayuga Trail (NE Corner)', 'url':get_stop_url('BUS344')}
# stops['BUS466W'] =  {'QuickCode':'BUS466W', 'StopDesc':'JR Hiatt Dr & 22nd St (NW Corner)', 'url':get_stop_url('BUS466W')}
# stops['BUS396'] =  {'QuickCode':'BUS396', 'StopDesc':'2nd St and Main St (SW Corner)', 'url':get_stop_url('BUS396')}
# stops['BUS299'] =  {'QuickCode':'BUS299', 'StopDesc':'Meijer Ct & Meijer Dr (NE Corner)', 'url':get_stop_url('BUS299')}

for i,stop_id in enumerate(stops,1):
	stops[stop_id]['url'] = get_stop_url(stop_id)
	print("\rCompleting stop url: %d/%d"%(i,len(stops)),end='')

len([stop for stop in stops if stops[stop]['url']==''])

stops_without_location = sorted([stop for stop in stops if not 'Lat' in stops[stop] or stops[stop]['Lat'] == ''])	# has no Google Map URL or bad formatted url (BUS375W    http://www.gocitybus.com/Maps-Schedules/ID/11/4B-Purdue-West-Klondike )
stop_desc = {s:stops[s]['StopDesc'] for s in stops_without_location}

# Correct stop coordinates
for s in stops:
	if   s == 'BUS125':
		GoogleUrl = 'https://www.google.com/maps/place/Bayley+Dr+at+Crosswinds+Apts+east+side%3ABUS125/@40.390131,-86.83392,18z'
	elif s == 'BUS155':
		GoogleUrl = 'https://www.google.ca/maps/place/Edgelea+Elementary+School:+BUS155/@40.3875562,-86.8766333,21z'
	elif s == 'BUS164':
		GoogleUrl = 'https://www.google.com/maps/place/St+Elizabeth+on+St+Francis+Way+north%3ABUS164/@40.392509,-86.836551,18z'
	elif s == 'BUS169':
		GoogleUrl = 'https://www.google.com/maps/place/Chelsea+Rd+%26+Northwestern+Ave+(West+Side):+BUS169/@40.434753,-86.915276,18z'
	elif s == 'BUS177':
		GoogleUrl = 'https://www.google.com/maps/place/Windmere+Dr+and+Bayley+Dr+NW+corner%3ABUS177/@40.388397,-86.834101,18z'
	elif s == 'BUS180':
		GoogleUrl = 'https://www.google.com/maps/place/St+Elizabeth+on+St+Fancis+Way+south%3ABUS180/@40.392509,-86.836551,18z'
	elif s == 'BUS183':
		GoogleUrl = 'https://www.google.com/maps/place/Bayley+Dr+at+Crosswinds+Apts+west+side%3ABUS183/@40.390131,-86.83392,18z'
	elif s == 'BUS214':
		GoogleUrl = 'https://www.google.com/maps/place/2nd+St+%26+Ferry+St+(SE+Corner):+BUS214/@40.4199571,-86.8953085,21z'
	elif s == 'BUS200S':
		GoogleUrl = 'https://www.google.com/maps/place/Julia+Ln+%26+Harper+(SW+Corner):+BUS200S/@40.406085,-86.8346916,21z'
	elif s == 'BUS215':
		GoogleUrl = 'https://www.google.com/maps/place/CityBus+Center:+BUS215/@40.4206872,-86.8949303,21z'
	elif s == 'BUS229SW':
		GoogleUrl = 'https://www.google.com/maps/place/Brown+St+%26+Tapawingo+Dr+(SW+Corner):+BUS229SW/@40.4219344,-86.8995287,21z'
	elif s == 'BUS266':
		GoogleUrl = 'https://www.google.com/maps/place/Russell+St+and+Harrison+St+NW+Corner:+BUS266/@40.420504,-86.919696,19z'
	elif s == 'BUS281':
		GoogleUrl = 'https://www.google.com/maps/place/Shenandoah+Drive+at+Munger+Trail+Crossing:+BUS050/@40.428907,-86.845145,18z'
	elif s == 'BUS289':
		GoogleUrl = 'https://www.google.com/maps/place/Jischke+Dr+and+3rd+St+SE+Corner:+BUS289/@40.42726,-86.921922,19z'
	elif s == 'BUS299':
		GoogleUrl = 'https://www.google.ca/maps/place/Meijer+Ct+%26+Meijer+Dr+(NE+Corner):+BUS299/@40.4167967,-86.8140011,20z'
	elif s == 'BUS322':
		GoogleUrl = 'https://www.google.com/maps/place/Grant+St+and+Harrison+St+NW+corner%3ABUS322/@40.420357,-86.910476,18z'
	elif s == 'BUS323':
		GoogleUrl = 'https://www.google.com/maps/place/West+of+Grant+St+and+Williams+St%3ABUS323/@40.418841,-86.910352,18z'
	elif s == 'BUS326':
		GoogleUrl = 'https://www.google.com/maps/place/Chauncey+Ave+and+Wood+St+SE+corner%3ABUS326/@40.421993,-86.907480,18z'
	elif s == 'BUS343':
		GoogleUrl = 'https://www.google.com/maps/place/McDonalds+on+Old+231:+BUS343/@40.3874532,-86.9047883,21z'
	elif s == 'BUS344':
		GoogleUrl = 'https://www.google.ca/maps/place/Beck+Ln+and+Cayuga+Tr+(NE+Corner):+BUS344/@40.388164,-86.8750763,21z'
	elif s == 'BUS363':
		GoogleUrl = 'https://www.google.com/maps/place/Main+St+and+5th+St+SW+corner%3ABUS363/@40.419010,-86.891943,18z'
	elif s == 'BUS375W':
		GoogleUrl = 'https://www.google.com/maps/place/Northwestern+Ave+and+Lindberg+Rd+West+of+Intersection%3ABUS375W/@40.4460412,-86.9219366,18z'
	elif s == 'BUS379':
		GoogleUrl = 'https://www.google.com/maps/place/Main+St+and+4th+St+SW+corner%3ABUS379/@40.419021,-86.893206,18z'
	elif s == 'BUS388':
		GoogleUrl = 'https://www.google.com/maps/place/State+St+%26+Gates+Rd+(West+of):+BUS388/@40.4241259,-86.9233762,21z'
	elif s == 'BUS396':
		GoogleUrl = 'https://www.google.ca/maps/place/2nd+St+%26+Main+St+(Lafayette+Savings+Bank):+BUS396/@40.4188847,-86.8955898,21z'
	elif s == 'BUS407':
		GoogleUrl = 'https://www.google.com/maps/place/Shenandoah+Dr+at+Munger+Trail+Crossing:+BUS051/@40.428976,-86.844671,18z'
	elif s == 'BUS422W':
		GoogleUrl = 'https://www.google.com/maps/place/(SW+of)+Canal+Rd+%26+9th+St+(1A+by+Request):+BUS422W/@40.4340726,-86.8876827,21z'
	elif s == 'BUS422E':
		GoogleUrl = 'https://www.google.com/maps/place/(SE+of)+Canal+Rd+%26+9th+St+(1A+by+Request):+BUS422E/@40.4338567,-86.8873166,21z'
	elif s == 'BUS425N':
		GoogleUrl = 'https://www.google.com/maps/place/Wabash+Landing+on+Brown+St:+BUS425N/@40.4222642,-86.9011179,21z'
	elif s == 'BUS425S':
		GoogleUrl = 'https://www.google.com/maps/place/Wabash+Landing+on+Brown+St+(at+Shelter):+BUS425S/@40.4219048,-86.9008121,21z'
	elif s == 'BUS466W':
		GoogleUrl = 'https://www.google.ca/maps/place/22nd+St+%26+JR+Hiatt+Dr+(NW+Corner):+BUS466W/@40.3976541,-86.8719034,21z'
	elif s == 'BUS472S':
		GoogleUrl = 'https://www.google.com/maps/place/Hilltop+Dr+%26+Tower+Dr+(SE+Corner):+BUS472S/@40.4330467,-86.9232112,20z'
	elif s == 'BUS491E':
		GoogleUrl = 'https://www.google.com/maps/place/McCutcheon+Hall+on+McCutcheon+(@Shelter):+BUS491E/@40.4256557,-86.9286923,20z'
	elif s == 'BUS509SW':
		GoogleUrl = 'https://www.google.com/maps/place/Jischke+Dr+%26+Tower+Dr+(SW+Corner):+BUS509SW/@40.4328283,-86.9217266,20z'
	elif s == 'BUS509SE':
		GoogleUrl = 'https://www.google.com/maps/place/Tower+Dr+%26+Jischke+Dr+(SE+Corner):+BUS509SE/@40.4328068,-86.9212331,20z'
	elif s == 'BUS511SW':
		GoogleUrl = 'https://www.google.com/maps/place/Cumberland+Ave+%26+Kent+Ave+(South+West+of):BUS511SW/@40.460494,-86.930092,18z'
	elif s == 'BUS512':
		GoogleUrl = 'https://www.google.com/maps/place/9th+St+%26+Greenbush+St+(SE+Corner):+BUS512/@40.4320429,-86.8870685,21z'
	elif s == 'BUS520SW':
		GoogleUrl = 'https://www.google.com/maps/place/State+St+%26+Jischke+Dr+(SW+Corner):+BUS520SW/@40.4241151,-86.921964,20z'
	elif s == 'BUS521SW':
		GoogleUrl = 'https://www.google.ca/maps/place/Beck+Ln+%26+Davis+Dr+(SW+Corner):+BUS521/@40.3879009,-86.8818328,21z'
	elif s == 'BUS524':
		GoogleUrl = 'https://www.google.com/maps/place/Harrison+St+and+Grant+St+NE+corner%3ABUS524/@40.420342,-86.910212,18z'
	elif s == 'BUS537S':
		GoogleUrl = 'https://www.google.ca/maps/place/Beck+Ln+%26+9th+St+(East+of):+BUS537/@40.3878688,-86.8852016,20z'
	elif s == 'BUS541':
		GoogleUrl = 'https://www.google.com/maps/place/Cumberland+Ave+%26+Browning+St+(NE+Corner):+BUS541/@40.4607705,-86.9210961,67m'
	elif s == 'BUS543NE':
		GoogleUrl = 'https://www.google.com/maps/place/Gates+Rd+%26+Nimitz+Dr+(NE+Corner):+BUS543NE/@40.4210599,-86.9232608,20z'
	elif s == 'BUS554W':
		GoogleUrl = 'https://www.google.com/maps/place/Alpha+Chi+on+David+Ross+Rd+(West):+BUS554W/@40.4344697,-86.9260517,19z'
	elif s == 'BUS558':
		GoogleUrl = 'https://www.google.com/maps/place/North+St+(East+of+Northwestern+Ave):+BUS558/@40.4262332,-86.9082956,18z'
	elif s == 'BUS562S':
		GoogleUrl = 'https://www.google.com/maps/place/Theta+Chi+on+Tower+Dr+(South):+BUS562S/@40.4330682,-86.9258545,21z'
	elif s == 'BUS646':
		GoogleUrl = 'https://www.google.com/maps/place/Northwestern+and+Columbia+St+NE+corner%3ABUS646/@40.424987,-86.907903,18z'
	elif s == 'BUS679W':
		GoogleUrl = 'https://www.google.ca/maps/place/Bishop+Woods+on+9th+St+(West+Side):+BUS679/@40.3897064,-86.886009,19z'
	elif s == 'BUS693W':
		GoogleUrl = 'https://www.google.ca/maps/place/9th+St+%26+Sarasota+Dr+(SW+Corner):+BUS693/@40.3931022,-86.8860666,19z'
	elif s == 'BUS716SE':
		GoogleUrl = 'https://www.google.com/maps/place/North+of+Haggarty+Ln+and+SR+2538%3ABUS716SE/@40.386710,-86.833729,18z'
	elif s == 'BUS716NE':
		GoogleUrl = 'https://www.google.com/maps/place/SR+2538+and+Haggarty+Ln+NE+corner%3ABUS716NE/@40.386710,-86.833729,18z'
	elif s == 'BUS765NW':
		GoogleUrl = 'https://www.google.com/maps/place/Sickle+Ct+%26+Julia+Ln+(NW+Corner):+BUS765NW/@40.4051343,-86.8353769,21z'
	elif s == 'BUS808':
		GoogleUrl = 'https://www.google.com/maps/place/Marketplace+Blvd+%26+Commerce+(NE+Corner):+BUS808/@40.4153845,-86.8267053,21z'
	elif s == 'BUS820':
		GoogleUrl = 'https://www.google.ca/maps/place/Rome+Dr+%26+Shenandoah+Dr+(SE+at+Shelter)/@40.4205852,-86.8461929,21z'
	elif s == 'BUS824':
		GoogleUrl = 'https://www.google.ca/maps/place/Soldiers+Home+Rd+%26+Prophet+Dr:+BUS824/@40.4643816,-86.8998612,21z'
	elif s == 'BUS894':
		GoogleUrl = 'https://www.google.com/maps/place/The+Avenue+North:+BUS894/@40.472177,-86.9474139,18z'
	elif s == 'BUS900':
		GoogleUrl = 'https://www.google.com/maps/place/Discovery+Learning+Center:+BUS900/@40.4208358,-86.9219103,19z'
	elif s == 'BUS923':
		GoogleUrl = 'https://www.google.com/maps/place/St+Elizabeth+Hospital+on+Creasy+(SE+Corner):BUS923/@40.3922125,-86.8381704,21z'
	elif s == 'BUS927NW':
		GoogleUrl = 'https://www.google.ca/maps/place/Broadview+Rd+%26+Soldiers+Home(NW+Corner):+BUS927NW/@40.4728375,-86.8968143,20z'
	elif s == 'BUS927SE':
		GoogleUrl = 'https://www.google.ca/maps/place/Broadview+Rd+%26+Soldiers+Home(SE+Corner):+BUS927SE/@40.4725049,-86.8964146,20z'
	elif s == 'BUS928NE':
		GoogleUrl = 'https://www.google.ca/maps/place/Veterans+Home+Entrance+(North+Side):+BUS928NE/@40.4744371,-86.8951687,19z'
	elif s == 'BUS928SE':
		GoogleUrl = 'https://www.google.ca/maps/place/Veterans+Home+Entrance+(North+Side):+BUS928NE/@40.4744371,-86.8951687,19z'
	elif s == 'BUS929':
		GoogleUrl = 'https://www.google.ca/maps/place/Ingersol+Hall+at+Indiana+Veterans+Home:+BUS933/@40.4731497,-86.8924476,20z'
	elif s == 'BUS930':
		GoogleUrl = 'https://www.google.ca/maps/place/Dehart+Hall+at+Indiana+Veterans+Home:+BUS930/@40.4726401,-86.8886302,21z'
	elif s == 'BUS931':
		GoogleUrl = 'https://www.google.ca/maps/place/Mitchell+Hall+at+Indiana+Veterans+Home:+BUS931/@40.4707746,-86.8898083,21z'
	elif s == 'BUS932':
		GoogleUrl = 'https://www.google.ca/maps/place/Pyle+Hall+at+Indiana+Veterans+Home:+BUS932/@40.4717301,-86.8917402,18z'
	elif s == 'BUS933':
		GoogleUrl = 'https://www.google.ca/maps/place/Ingersol+Hall+at+Indiana+Veterans+Home:+BUS933/@40.4731497,-86.8924476,20z'
	elif s == 'BUS991':
		GoogleUrl = 'https://www.google.ca/maps/place/South+Tipp+Park:+BUS991/@40.4130845,-86.894073,20z'
	elif s == 'BUS992':
		GoogleUrl = 'https://www.google.com/maps/place/St.+Elizabeth+Hospital:+BUS992/@40.393968,-86.8369501,21z'
	elif s in stops_without_location:
		stop_desc[s] = stop_desc[s].replace(' NW corner','')
		stop_desc[s] = stop_desc[s].replace(' NE corner','')
		stop_desc[s] = stop_desc[s].replace(' SW corner','')
		stop_desc[s] = stop_desc[s].replace(' SE corner','')
		stop_desc[s] = stop_desc[s].replace(' NW Corner','')
		stop_desc[s] = stop_desc[s].replace(' NE Corner','')
		stop_desc[s] = stop_desc[s].replace(' SW Corner','')
		stop_desc[s] = stop_desc[s].replace(' SE Corner','')
		stop_desc[s] = stop_desc[s].replace(' east side','')
		stop_desc[s] = stop_desc[s].replace(' west side','')
		stop_desc[s] = stop_desc[s].replace(' West Side of Street','')
		stop_desc[s] = stop_desc[s].replace(' West of Intersection','')
		stop_desc[s] = stop_desc[s].replace(' WEST of Intersection','')
		stop_desc[s] = stop_desc[s].replace(' Way south',' Way')
		stop_desc[s] = stop_desc[s].replace('West of Grant','Grant')
		stop_desc[s] = stop_desc[s].replace('South of Chauncey','Chauncey')
		stop_desc[s] = stop_desc[s].replace('North of Haggarty','Haggarty')
		coordinates = get_geocode(stop_desc[s])
		GoogleUrl = 'https://www.google.com/maps/place/%s/@%f,%f,18z'%(urllib.parse.quote_plus(stops[s]['StopDesc']+':'+s), coordinates['lat'], coordinates['lng'])
		# https://www.google.com/maps/place/Main+St+and+9th+St%3ABUS334/@40.419134,-86.886803,18z
	else:
		GoogleUrl = stops[s]['GoogleUrl']
	
	if GoogleUrl.startswith('http://maps.google.com/maps?ll='):
		# http://maps.google.com/maps?t=h&ie=UTF8&ll=40.420845,-86.9232137157448&spn=0.001369,0.001985&z=18&iwloc=lyrftr:unknown,0x8812e2c7e299d379:0x60227fc4ef7b3d60,
		# Lat,Lon = [p[3:].split(',') for p in GoogleUrl.split('&') if p[:3] == 'll='][0]
		Lat,Lon = GoogleUrl.split('&')[0].split('maps?ll=')[1].split(',')
		GoogleUrl = GoogleUrl.replace('?t=h&ie=UTF8&ll=','?ll=')
	else:
		# https://www.google.com/maps/place/Creasy+Ln+&+Bonlou+(Menards+Entrance):+BUS941NW/@40.3873633079149,-86.8404313528795,18z
		Lat,Lon = GoogleUrl.split('/@')[1].split(',')[:2]
	stops[s]['GoogleUrl'] = GoogleUrl
	stops[s]['Lat'] = Lat
	stops[s]['Lon'] = Lon

# pprint(stops[s])


# steps = []
# stop_to_stop = {}
for route in routes:
	# s2s = [tuple(sorted(pair)) for pair in zip(route['stops'][:-1], route['stops'][1:])]
	# for start,end in s2s:
	
	departure_time = 1442419259	# wed_1200
	if route['name'] == 'Willowbrook Klondike Express AM':
		departure_time = 1442403059	# wed_0730 for 8 Willowbrook Klondike Express AM
	if route['name'] == 'Willowbrook Klondike Express PM':
		departure_time = 1442436359	# wed_1645 for 8 Willowbrook Klondike Express PM
	if route['name'] == 'Black Loop':
		departure_time = 1442440859	# wed_1800 for 14 Black Loop
	# if route['name'] == 'Market Square Outbound':
		# departure_time = 1442445659	# wed_1920 for 1A Market Square Outbound
	if route['name'] == 'Northwestern Saturday Inbound':
		departure_time = 1442678459	# sat_1200 for 5B Northwestern Saturday Inbound
	if route['name'] == 'Northwestern Saturday Outbound':
		departure_time = 1442678459	# sat_1200 for 5B Northwestern Saturday Outbound
	if route['name'] == 'Salisbury Weekday Sunday Inbound':
		departure_time = 1442311259	# wed_0600 for 1B Salisbury Weekday Sunday Inbound
	if route['name'] == 'Salisbury Evening Saturday Inbound':
		departure_time = 1442682059	# sat_1300 for 1B Salisbury Evening Saturday Inbound
	if route['name'] == 'Salisbury Evening Saturday Outbound':
		departure_time = 1442682059	# sat_1300 for 1B Salisbury Evening Saturday Outbound
	if route['name'] == 'NightRider':
		departure_time = 1442718059	# sat_2300 for 18 NightRider
	
	print(route['ID'], route['name'])
	print(route['stops'][0], route['stops'][-1])
	if route['ID'] == '1A' and route['name'] == 'Market Square Inbound':
		route['polyline'] = get_polyline_with_middlepoint(route['stops'][0], 'BUS200N', route['stops'][-1])
	elif route['ID'] == '1A' and route['name'] == 'Market Square Outbound':
		route['polyline'] = get_polyline_with_middlepoint(route['stops'][0], 'BUS200S', route['stops'][-1])
		# route['polyline'] = r"ituuF`tjqOm@@AmJcDB?}EEaFAs@iD?iCFgGFIkWeDCgKLiLNiN`@eOc@D~AnB|@~Cv@~XxViVuVkEcCyA?Ci@bM`@Dg\\JuO@qLBuW?wLB{MUiP?uRJe]Q}HJ_x@M}OxRPjASd@HXTdCvD^vCLh@\XrAP|HE|JAtDSxBqAt@[nAgAn@KfACBaPQ_Si@{E~GRfJO~LB~Yo@|\W?eDHwS??`B^|AhB|@|@hDeE|B?L`JJbOrLIzNy@vJBjZOIsb@dCc@HbEZn@d@RrQVA_BLaALq@\_@b@]lEnDgItTcE~KiIzUqJvT_HnKrBlD|@aA~AyBlAzEdAlC`CmC"
	elif route['ID'] == '3' and route['name'] == 'Lafayette Square Outbound':
		route['polyline'] = get_polyline_with_middlepoint(route['stops'][0], 'BUS708', route['stops'][-1])
	elif route['ID'] == '3' and route['name'] == 'Lafayette Square Inbound':
		route['polyline'] = get_polyline_with_middlepoint(route['stops'][0], 'BUS720', route['stops'][-1])
	elif route['ID'] == '6A' and route['name'] == 'South 4th Street Inbound':
		route['polyline'] = r"oyjuFv}cqO~EAdAyBQiPl`@FA{Vi@fT}_@EL`RaB`GoB`EuBbBuB@_G?@fRB|ODhNEhT@dHeD@wN?yTK_N`@aNCuPLDtETfc@aAdICvCEzCGhC{@vBw@zAcBzEsA`HGxJE~OCn@aFBuSPD~IBh]LhQpSFGjZ]vKcZ`HmQtFwCw@[Kz@mUb@yOjAgZiAq@m@}@}CgDkBeFwEyUcAuDeBeByIcDqEoBkOcEw@ImHA}JKDxB?jJPjMk@@_IBmBFg@W_BsD{@sBwG_H}@}@}@c@iOAcC@kOFQ?CdGgHMaF?qD?oC@?_B"
	elif route['ID'] == '6A' and route['name'] == 'South 4th Street Outbound':
		route['polyline'] = r"ituuF`tjqO@fCfJBtNI?eCB_C@{EzMEhF@dPBdGG~LAnF@xILnIDzARvAZhKxDhFhBbHxC`Bz@zA~CxDdTfBxF~BnDdDhCMfD}AhSu@jTYzISrE^bBtBJtCAzP_D~[eIWcEH}CPoCSuXGwBHmI^_DxBgHj@aD`@{EBoRA{CDiJLyHTaFx@wEjCuF|@wCf@iEKwE|@gHXkE?cPk@oQfSWbFEdNe@nGGpIFnLG|OI?uJ?yPEgOUwc@nA@nAMDsEAgF`EK"
	elif route['ID'] == '8':
		route['polyline'] = get_polyline_with_middlepoint(route['stops'][0], 'BUS271', route['stops'][-1])
	elif route['ID'] == '12':
		route['polyline'] = get_polyline_with_middlepoint(route['stops'][0], 'BUS557', route['stops'][-1])
	elif route['ID'] == '13':
		route['polyline'] = get_polyline_with_middlepoint(route['stops'][0], 'BUS538', route['stops'][-1])
	elif route['ID'] == '16':
		route['polyline'] = get_polyline_with_middlepoint(route['stops'][0], 'BUS538', route['stops'][-1])
	elif route['ID'] == '18':
		route['polyline'] = get_polyline_with_middlepoint(route['stops'][0], 'BUS329', route['stops'][-1])
	elif route['ID'] == '19':
		route['polyline'] = get_polyline_with_middlepoint(route['stops'][0], 'BUS565S', route['stops'][-1])
	elif route['ID'] == '21':
		# route['polyline'] = get_polyline_with_middlepoint(route['stops'][0], 'BUS271', route['stops'][-1])
		route['polyline'] = r"gv_vFzrtqOFl@V?LOB_@FSXIr@EzBEjA@nABf@N^ZdDjFXXb@PvDDx@BpAUV{@?uANoCCq@[YaB?@oJDqDL}CXkCf@gCbBkGfAcCdAkBjBaCvCiCpXeSpEtKfKcGUiAoJtFqD{IjLaIvEeC~DuAdCkAzFuGxD{DrRaPdXeSjM}Ip[aNpKuJjC{@bYcArDyD~DyEnIgJ`JoKfG}F`I@ShQ??IhME~FG|JiID}SNeLE{BBkCQkD|AkInA}GxC{KrBa@eHc^zNqLpIsl@`d@oY|R_QdMvE`LfKcGTdA_LtGqFiNyXhScDfD}CnEuBnEsAdFy@zFWdBKjCCrY{CRq@[mCgEa@m@g@a@k@GuGAsADc@LMj@"
	elif route['ID'] == '23':
		route['polyline'] = get_polyline_with_middlepoint(route['stops'][0], 'BUS282NE', route['stops'][-1])
	elif route['name'].endswith('bound'):	# other one way routes
		start = route['stops'][0]
		end = route['stops'][-1]
		dist(stops[start],stops[end])>300
		route['polyline'] = get_polyline(start,end)
	else:	# loops
		route['polyline'] = get_polyline_with_middlepoint(route['stops'][0], route['stops'][int(len(route['stops'])/2)], route['stops'][-1])


# get distance between each stops
for route in routes:
	route['distance'] = [0]
	polyline = []
	for lat,lon in decode(route['polyline']):
		polyline.append({'Lat':lat, 'Lon':lon})
	
	# print(route['stops'][0], dist(stops[route['stops'][0]], {'Lat':polyline[0]['Lat'],'Lon':polyline[0]['Lon']}))
	print(route['ID'], route['name'])
	
	for i,stop in enumerate(route['stops'][1:],1):
		d_min = 1e10
		h_min = {}
		j_min = 0
		for j,(a,b) in enumerate(zip(polyline[:-1],polyline[1:]),1):
			d,h = dist_to_line(stops[stop],a,b)
			if d < d_min:
				d_min = d
				h_min = h
				j_min = j
		# 1+'a'
		route['distance'].append(int(path_length(polyline[:j_min]+[h_min])))
		polyline = [h_min]+polyline[j_min:]
		if route['distance'][-1] == 0 or route['distance'][-1] > 1000:
		# if route['distance'][-1] < route['distance'][-2]:	# when testing the distance slicing, comment line: polyline = [h_min]+polyline[j_min:]
			print(i,stop, d_min)




# test if stops of routes with same ID overlap
s = [stop for r in routes for stop in r['stops'] if r['ID'] == '1A']
pprint([ss for ss in set(s) if s.count(ss)>1])

def match_route(stop_info, route_ID):
	'''Some routes appear wrong names at stop arrival query'''
	if stop_info.startswith('5A') and route_ID=='5B':
		return(True)
	elif stop_info.startswith(route_ID):
		return(True)
	return(False)

def get_arrival_times(stop):
	if stop not in stops:
		stops[stop] = {'QuickCode':stop, 'StopDesc':'enumerate', 'url':get_stop_url(stop)}
	if stops[stop]['url'] == '':
		return([])
	page_soup = get_page('http://myride.gocitybus.com/public/laf/web/ViewStopNew.aspx?sp='+stops[stop]['url'])
	tab = page_soup.find('table',attrs={'class':'GridView'})
	lines = [(text(tr.find_all('td')[1].text), text(tr.find_all('td')[3].text)) for tr in tab.find_all('tr')[1:]]	# select 1:end <tr> and 1,3 <td>
	return(lines)

def enumerate_stops():
	count=0
	for i in range(1,10):
		for j in range(0,10):
			for k in range(0,10):
				for NS in ['','N','S']:
					for WE in ['','W','E']:
						count = count+1
						yield(count,'BUS'+str(i)+str(j)+str(k)+NS+WE)


# find missing stops for each route by examining routes at each stop
missing_stops = []
for (index,stop) in enumerate_stops():
	print('\r',index,':',stop+'      ',end='')
	lines = get_arrival_times(stop)
	for line in lines:
		ID = ''
		name = ''
		missing = 0
		for route in routes:
			if route['ID'] != ID:
				if missing%16 and missing<16:
					missing_stops.append((ID, name, stop))
					print(name, stop, line)
				missing = 0
				ID = route['ID']
				name = route['name']
			if route['ID'] == ID and line[0].startswith(ID) and stop in route['stops']:
				missing += 16	# high bit: not missing stop
			if route['ID'] == ID and line[0].startswith(ID) and stop not in route['stops']:
				missing += 1	# low bit: missing stop

missing_stops = set(missing_stops)
list(missing_stops.sort())
pprint(missing_stops)
print(len(missing_stops))

# time.sleep(132*60)
for _ in range(50):
	# Store the time between stops in seconds
	for route in routes:
		last_arrival_times = []
		# new_route_stops = []
		print('\n',route['ID'],route['name'])
		for (index,stop) in enumerate(route['stops']):
			print('\r',index,'/',len(route['stops']),end='')
			lines = get_arrival_times(stop)
			arrival_times = [line[1].split()[0] for line in lines if match_route(line[0],route['ID'])]
			for i,time in enumerate(arrival_times):
				if time == 'DUE':
					time = 0
				else:
					time = int(time)*60
				arrival_times[i] = time
			if arrival_times:
			# if last_arrival_times:
				delta_times = []
				for i,time in enumerate(arrival_times):
					try:
						delta_times.append(arrival_times[i] - last_arrival_times[i])
					except IndexError:	# align
						break
				if delta_times:
					# new_route_stops.append((route['stops'][index], float(sum(delta_times))/len(delta_times)))
					route['duration'][index].extend(delta_times)
				# except ZeroDivisionError:	# no info
					# new_route_stops.append((route['stops'][index], 0))
				# else:
					# route['duration'][index].append(0)
				last_arrival_times = arrival_times
			# last_arrival_times = arrival_times
		# route['stops'] = new_route_stops



# start = "40.4254466548828,-86.9257054880682"
# end = "40.4272692160171,-86.9222226394548"
# start = ','.join([stops[start]['Lat'], stops[start]['Lon']])
# end = ','.join([stops[end]['Lat'], stops[end]['Lon']])

# 'http://www.gocitybus.com/Maps-Schedules/ID/16/5A-Happy-Hollow'




with open('data/stops.json','w+') as fp:
	# for stop_key in stops:
		# del stops[stop_key]['GoogleUrl']
		# del stops[stop_key]['StopDesc']
		# del stops[stop_key]['QuickCode']
	json.dump(stops,fp)

# with open('data/routes_raw.json','r+') as fp:
	# old_routes = json.load(fp)

# for (r,route) in enumerate(routes):
	# for (d,duration) in enumerate(route['duration']):
		# routes[r]['duration'][d].extend(old_routes[r]['duration'][d])

with open('data/routes_raw.json','w+') as fp:
	json.dump(routes,fp)

with open('data/routes.json','w+') as fp:
	for route in routes:
		duration = []
		for d in route['duration']:
			d = [dd for dd in d if dd>=0]
			if d:
				duration.append(int(sum(d)/len(d)))
			else:
				duration.append(0)
		route['duration'] = duration
	json.dump(routes,fp)



# with open('data/stops.json','w+') as fp:
	# # for stop_key in stops:
		# # del stops[stop_key]['GoogleUrl']
		# # del stops[stop_key]['StopDesc']
		# # del stops[stop_key]['QuickCode']
	# json.dump(stops,fp)

# with open('data/routes_raw.json','w+') as fp:
	# json.dump(routes,fp)

with open('data/stops.json','r+') as fp:
	stops = json.load(fp)

with open('data/routes_raw.json','r+') as fp:
	routes = json.load(fp)


from bottle import Bottle, route, run, template, request, response,  post, get, redirect, static_file, debug
app=Bottle()
debug(True)

@app.route('/')
def page():
	return template('template')

@app.route('/data/:filename#.+#')
def returnStatic(filename):
	return static_file(filename, root='./data/')

@app.route('/icon/:filename#.+#')
def returnStatic(filename):
	return static_file(filename, root='./icon/')

@app.route('/src/:filename#.+#')
def returnStatic(filename):
	return static_file(filename, root='./src/')


run(app,host='localhost', port=8080)
