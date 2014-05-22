# coding=utf8

import mechanize
import time
from bs4 import BeautifulSoup, SoupStrainer
import urllib
import re
import json
from dateutil import parser
import time
import datetime
import pymongo
import copy
import platform
import jieba
import jieba.analyse
import sys
import tweepy

def formProcess2(url):
	global br
	global groupData
	global contextData2
	global listLink
	global features
	global curTime
	global flagStop
	
	print 'process list:' + url

	try_time = 0
	response = None
	time.sleep(1)
	while (response is None):
		try:
			if try_time > 50:
				flagStop = True
				break
			response = br.open(url)
		except:	
			print 're Try'
			response = None	
		try_time = try_time + 1	
		time.sleep(3)	

	if flagStop:
		return	

	if response.geturl().find('over18') != -1:
		print 'over 18 page process'
		br.select_form(nr=0)
		response = br.submit(name='yes', label='yes')

	nextIdx = 0;
	#nextLink = None

	only_div_btngroup = SoupStrainer("div", {"class":"btn-group pull-right"})
	only_div_r_ent = SoupStrainer("div", {"class":"r-ent"})
	#response2 = copy.copy(response)
	soup = BeautifulSoup(copy.copy(response), features=features, parse_only=only_div_btngroup);
	soup2 = BeautifulSoup(copy.copy(response), features=features, parse_only=only_div_r_ent);

	#下一頁面連結取得
	pageLinkDiv = soup.find("div", {"class":"btn-group pull-right"})
	for pageLink in pageLinkDiv.findAll('a', href=True):
		if pageLink.string.encode('utf8').find('上頁') != -1:
			listLink = 'http://www.ptt.cc' + pageLink['href']

	#文章列表

	for recordDiv in reversed(soup2.findAll("div", {"class":"r-ent"})):
		titleDiv = recordDiv.find("div", {"class":"title"})
		metaDiv = recordDiv.find("div", {"class":"meta"})

		titleLink = titleDiv.find('a', href=True);
		if not titleLink is None:
			print '==='
			print titleLink['href']
			print titleLink.string.encode('utf8')
			
            
			m = re.search('\/bbs\/([A-Za-z0-9]+)\/([A-Za-z0-9\.]+)\.html', titleLink['href'])
			print m.groups()[0]
			id = m.groups()[1]
			contentLink = 'http://www.ptt.cc' + titleLink['href']
			

			content_obj = contentGet(id, 'http://www.ptt.cc' + titleLink['href'])

			if not content_obj is None:
				
				if id in contextData2:
					object = contextData2[id]
				else:
					object = {}
					object['id'] = id
					contextData2[id] = object
				
				#內文title抓不到 用列表的
				if 'title' in content_obj:
					object['title'] = content_obj['title']
				else:
					object['title'] = titleLink.string.encode('utf8')
				#內文時間抓不到 用現在時間頂替	
				if 'time' in content_obj:	
					object['time'] = content_obj['time']
				else:
					object['time'] = curTime
				#內文推文抓不到  用預設為0
				if 'push' in content_obj:	
					object['push'] = content_obj['push']
				else:
					object['push'] = { 'g': 0, 'b': 0, 'all': 0 }
				object['link'] = contentLink

				if 'extra_push_point' in content_obj:	
					object['extra_push_point'] = content_obj['extra_push_point']
				else:
					object['extra_push_point'] = 0

				time.sleep(0.2)
			
	
				keyString = '';
				if titleLink.string.encode('utf8').find('Re: ') != -1:  #回覆
					keyString = titleLink.string.encode('utf8')[4:];
				else:
					keyString = titleLink.string.encode('utf8');

				if keyString in groupData.keys():
					groupData[keyString]['groupList'].append(id)
				else:
					groupData[keyString] = {'key':keyString, 'groupList':[id]}

				dateDiv = metaDiv.find('div', {"class":"date"})	
				authorDiv = metaDiv.find('div', {"class":"author"})
				print dateDiv.string
				print authorDiv.string	

				#if flagStop:
				#	break

	print '----====----==----'
	print flagStop
	#if flagStop != True:
	#	formProcess2(nextLink)


def contentGet(id, contentLink):
	global br
	global linkData
	global contextData
	global contextData2
	global endTime
	global flagStop
	global features
	global sixHourBeforeTime
	print contentLink
	try:
		response = br.open(contentLink)
		print 'contentGet:' + response.geturl()
	except:	
		response = None

	content_obj = None

	if not response is None:
		only_div_push = SoupStrainer("div", {"class":"push"})
		soup = BeautifulSoup(copy.copy(response), features=features, parse_only=only_div_push)
		pushGoodCount = 0
		pushBadCount = 0
		pushNormalCount = 0
		print 'contentGet start parse push'
		pushTmpMonth = 0
		pushTmpYearOffset = 0
		extraPushPoint = 0
		for pushdiv in soup.findAll("div", {"class":"push"}):
			print 'contentGet parse push'
			#print pushdiv
			#push
			#推噓判定
			pushTag = pushdiv.find("span", {"class":"hl push-tag"})
			if pushTag is None:
				pushTag = pushdiv.find("span", {"class":"f1 hl push-tag"})
			if not pushTag is None: 

				if pushTag.string.encode('utf8').find('推') != -1:
					pushGoodCount = pushGoodCount + 1
				elif pushTag.string.encode('utf8').find('噓') != -1:
					pushBadCount = pushBadCount + 1	
				else:
					pushNormalCount = pushNormalCount + 1	
			#推文時間
			pushTime = pushdiv.find("span", {"class":"push-ipdatetime"})
			#推文時間可能會是ip與時間的集合  僅抽出時間  183.4.230.250 05/22 00:57
			m = re.search('([0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3} )?([0-9]{2}/[0-9]{2} [0-9]{2}:[0-9]{2})', pushTime.string)
			print '--- push time---'
			for match in m.groups():
				print match
			print '--- push time end---'

			parsedTime = parser.parse(m.groups()[1])
			#if pushTmpYearOffset > 0:
			#	parsedTime = parsedTime.replace(year=parsedTime.year+pushTmpYearOffset)
			parsedTimeStr = parsedTime.strftime("%Y-%m-%d %H:%M:%S")
			parsedTimeStamp = time.mktime(time.strptime(parsedTimeStr, '%Y-%m-%d %H:%M:%S'))
			if parsedTimeStamp > sixHourBeforeTime:
				extraPushPoint = extraPushPoint + 1;
			print type(parsedTime)
			print type(parsedTimeStr)
			print parsedTimeStr
			if pushTmpMonth > parsedTime.month:
				pushTmpYearOffset = pushTmpYearOffset + 1
			pushTmpMonth = parsedTime.month
		print 'pushAllCount ' + str(pushGoodCount + pushBadCount + pushNormalCount)
		print 'extraPushPoint ' + str(extraPushPoint)

		print 'contentGet end parse push'
		pushData = { 'all':pushGoodCount + pushBadCount + pushNormalCount,  'g' : pushGoodCount, 'b': pushBadCount, 'n':pushNormalCount}
		pushExtraData = {   'all':pushData['all'] + extraPushPoint,  
							'g' : pushData['g'] + extraPushPoint, 
							'b': pushData['b'] + extraPushPoint, 
							'n':pushData['n'] + extraPushPoint  }
		#object = contextData2[id]
		#object['push'] = pushData
		content_obj = {}
		content_obj['push'] = pushData
		content_obj['extra_push_point'] = pushExtraData
		contextData[contentLink] = { 'push': pushData}
					
		links = []		
		only_link = SoupStrainer('a', href=True)
		soup = BeautifulSoup(copy.copy(response), features=features, parse_only=only_link)
		print 'contentGet start parse link'	
		for link in soup.findAll('a', href=True):
			print 'contentGet parse link'
			m = re.search('http://.+', link['href'])
			if not m is None:

				if link['href'] == contentLink:
					continue
				if link['href'].find('http://www.ptt.cc/') != -1:
					continue	

				print '--' +  link['href'].encode('utf8')

				contenturl = link['href']

				links.append(contenturl)

				if contenturl in linkData:
					linkData[contenturl] = linkData[contenturl] + pushGoodCount + pushBadCount + pushNormalCount;
				else:
					linkData[contenturl] = pushGoodCount + pushBadCount + pushNormalCount;
		print 'contentGet end parse link'
		contextData[contentLink]['link'] = links			
		
		#時間
		#<span class="article-meta-value">Tue Apr 15 00:07:21 2014</span>
		only_div_acticlemeta = SoupStrainer('div',  {"class":"article-metaline"})
		soup = BeautifulSoup(copy.copy(response), features=features, parse_only=only_div_acticlemeta)
		print 'contentGet start parse time'
		for metaDiv in soup.findAll('div',  {"class":"article-metaline"}):
			print 'contentGet parse time'
			metaDivTag = metaDiv.find('span',  {"class":"article-meta-tag"})
			metaDivValue = metaDiv.find('span',  {"class":"article-meta-value"})
			if metaDivTag.string.encode('utf8').find('時間') != -1:
				print metaDivValue.string
				print parser.parse(metaDivValue.string)
				#object['time'] = parser.parse(metaDivValue.string).strftime("%Y-%m-%d %H:%M:%S")
				#contextTime = time.mktime(time.strptime(object['time'], '%Y-%m-%d %H:%M:%S'))
				parsedTimeStr = parser.parse(metaDivValue.string).strftime("%Y-%m-%d %H:%M:%S")
				contextTime = time.mktime(time.strptime(parsedTimeStr, '%Y-%m-%d %H:%M:%S'))
				#object['time'] = contextTime
				content_obj['time'] = contextTime

				print contextTime
				print endTime
				if contextTime < endTime:
					print '===end'
					flagStop = True

			if metaDivTag.string.encode('utf8').find('標題') != -1:
				#object['title'] = metaDivValue.string
				content_obj['title'] = metaDivValue.string
		print 'contentGet stop parse time'	
		
	return content_obj		


def boardProcess(boardData):
	global linkData
	global contextData
	global groupData
	global contextData2
	
	global curTime
	global endTime
	global flagStop
	global listLink
	global db_address
	global sixHourBeforeTime

	linkData = {}
	contextData = {}
	groupData = {}
	contextData2 = {}
	flagStop = False
	curTime = time.time()
	print '=== start time ==='
	print curTime
	print datetime.datetime.fromtimestamp(curTime).strftime('%Y-%m-%d %H:%M:%S')
	endTime = curTime - 60 * 60 * boardData['parseHour'] 
	rangeDay = curTime - 60 * 60 * boardData['rankHour']
	sixHourBeforeTime = curTime - 60 * 60 * 6
	print datetime.datetime.fromtimestamp(endTime).strftime('%Y-%m-%d %H:%M:%S')
	print '=================='

    #dataCollect();
	#board = 'beauty'#'Gossiping'
	listLink = "http://www.ptt.cc/bbs/" + boardData['name'] + "/index.html"
	while flagStop is False:
		formProcess2(listLink)#HatePolitics

	#print
	for key in linkData.keys():
		print key.encode('utf8') + ':' + str(linkData[key])
	for key in contextData.keys():
		print key.encode('utf8') + ':' + str(contextData[key]['push']) + ' - ' + str(contextData[key]['push']['g'] + contextData[key]['push']['b'] + contextData[key]['push']['n'])
		for link in contextData[key]['link']:
			print '-- link:' + link.encode('utf8')
	
	jsonStr = json.dumps(contextData, indent=4)
	with open("contextData.json", "w") as f:
		f.write(jsonStr)	
	jsonStr = json.dumps(linkData, indent=4)
	with open("linkData.json", "w") as f:
		f.write(jsonStr)  
	jsonStr = json.dumps(contextData2, indent=4)
	with open("contextData2.json", "w") as f:
		f.write(jsonStr)	      	
	

	for key in groupData.keys():
		print key 
		push = {"all": 0, "b": 0, "g": 0, "n": 0}
		for data in groupData[key]['groupList']:
			if not contextData2[data] is None:
				print '--' + data
				print contextData2[data]
				if not contextData2[data]['push'] is None:
					print contextData2[data]['push']
					push['b'] = push['b'] + contextData2[data]['push']['b']
					push['g'] = push['g'] + contextData2[data]['push']['g']
					push['n'] = push['n'] + contextData2[data]['push']['n']
					push['all'] = push['all'] + contextData2[data]['push']['all']
		groupData[key]['push'] = push

	#save to file
	jsonStr = json.dumps(groupData, indent=4)
	with open("groupData.json", "w") as f:
		f.write(jsonStr) 
		
	
	#save to db
	#conn=pymongo.Connection('54.251.147.205',27017)
	conn=pymongo.Connection(db_address,27017)
	db = conn[boardData['name']]#conn['Gossiping']

	#單一文章
	for key in contextData2.keys():
		findDoc = db.single.find_one({'id': key})
		if findDoc is None:
			db.single.insert(contextData2[key])
		else:
			findDoc['push'] = contextData2[key]['push']
			db.single.save(findDoc)

	#群組文章
	for key in groupData.keys():
		findDoc = db.group.find_one({'key': key})
		if findDoc is None:
			groupData[key]['time'] = curTime
			db.group.insert(groupData[key])
		else:
			#data reset
			for recId in groupData[key]['groupList']:
				if not recId in findDoc['groupList']:
					findDoc['groupList'].append(recId)
					findDoc['time'] = curTime

			print findDoc['groupList']
					
			pushData = { 'g': 0, 'b': 0, 'n': 0, 'all': 0 }	
			for rec in db.single.find({"id":{"$in":findDoc['groupList']}}):
				pushData['g'] += rec['push']['g']
				pushData['n'] += rec['push']['n']
				pushData['b'] += rec['push']['b']
			pushData['all'] = pushData['g'] + pushData['n'] + pushData['b']
			findDoc['push'] = pushData
			db.group.save(findDoc)	
			
	#排行資料
	
	#文章資料
	'''		
	rankdata = {}
	rankdata['g'] = sorted(contextData2.items(), key=lambda t: t[1]['push']['g'], reverse=True)[:10]
	rankdata['b'] = sorted(contextData2.items(), key=lambda t: t[1]['push']['b'], reverse=True)[:10]
	rankdata['t'] = sorted(contextData2.items(), key=lambda t: t[1]['push']['all'], reverse=True)[:10]
	rankdata['gg'] = sorted(groupData.items(), key=lambda t: t[1]['push']['g'], reverse=True)[:10]
	rankdata['gb'] = sorted(groupData.items(), key=lambda t: t[1]['push']['b'], reverse=True)[:10]
	rankdata['gt'] = sorted(groupData.items(), key=lambda t: t[1]['push']['all'], reverse=True)[:10]
	jsonStr = json.dumps(rankdata, indent=4)
	with open("rankdata.json", "w") as f:
		f.write(jsonStr) 
		'''

	#資料庫資料
	rankdata = {}
	rankdata['t'] = list(db.single.find({'time':{"$gte":rangeDay}}, { '_id': 0}) \
					  .sort([('push.all', pymongo.DESCENDING)]) \
					  .limit(50))	
	rankdata['g'] = list(db.single.find({'time':{"$gte":rangeDay}}, { '_id': 0}) \
					  .sort([('push.g', pymongo.DESCENDING)]) \
					  .limit(50))
	rankdata['b'] = list(db.single.find({'time':{"$gte":rangeDay}}, { '_id': 0}) \
					  .sort([('push.b', pymongo.DESCENDING)]) \
					  .limit(50))

	rankdata['gt'] = list(db.group.find({'time':{"$gte":rangeDay}}, { '_id': 0}) \
					  .sort([('push.all', pymongo.DESCENDING)]) \
					  .limit(50))

	for gData in rankdata['gt']:
		gData['groupListData'] = list(db.single.find({"id":{"$in":gData['groupList']}}, { '_id': 0}) \
					  				.sort([('time', pymongo.ASCENDING)]) \
					  				.limit(50))

	rankdata['gg'] = list(db.group.find({'time':{"$gte":rangeDay}}, { '_id': 0}) \
					  .sort([('push.g', pymongo.DESCENDING)]) \
					  .limit(50))
	for gData in rankdata['gg']:
		gData['groupListData'] = list(db.single.find({"id":{"$in":gData['groupList']}}, { '_id': 0}) \
					  				.sort([('time', pymongo.ASCENDING)]) \
					  				.limit(50))
	rankdata['gb'] = list(db.group.find({'time':{"$gte":rangeDay}}, { '_id': 0}) \
					  .sort([('push.b', pymongo.DESCENDING)]) \
					  .limit(50))
	for gData in rankdata['gb']:
		gData['groupListData'] = list(db.single.find({"id":{"$in":gData['groupList']}}, { '_id': 0}) \
					  				.sort([('time', pymongo.ASCENDING)]) \
					  				.limit(50))
	rankdata['time'] = curTime


	

	jsonStr = json.dumps(rankdata, indent=4)
	with open("rankdata.json", "w") as f:
		f.write(jsonStr) 	
	db.rank.insert(rankdata)

	#link get
	'''try:
					if link['href'].find('ppt.cc') != -1:
						response3 = br.open(link['href'])
						print 'ppt.cc : ' +  response3.geturl()
						contenturl = response3.geturl()
					elif link['href'].find('goo.gl') != -1: 
						response3 = br.open(link['href'])
						print 'goo.gl : ' +  response3.geturl()
						contenturl = response3.geturl()	
					elif link['href'].find('tinyurl.com') != -1: 
						response3 = br.open(link['href'])
						print 'tinyurl.com : ' +  response3.geturl()
						contenturl = response3.geturl()	
					elif link['href'].find('bit.ly') != -1: 
						response3 = br.open(link['href'])
						print 'bit.ly : ' +  response3.geturl()
						contenturl = response3.geturl()		
					else:
						contenturl = link['href']
				except:		'''
	'''			
	for key in linkData.keys():
		print '=========='
		link = str(key.encode('utf8'))
		print '1 ' + link

		try:
			response3 = br.open(link)
			contenturl = response3.geturl()
			contenttitle = br.title()
			print '2 ' + contenturl	
			print '3 ' + contenttitle		
		except:	
			print 'error'
	'''		


def parseKeyword(board_data):
	global br
	global db_address

	conn=pymongo.Connection(db_address,27017)
	db = conn[board_data['name']]

	rank_data = list(db.single.find({}, { '_id': 0}) \
						    .sort([('push.all', pymongo.DESCENDING)]) \
							.limit(50))	
	keywords = {}
	links_data = []

	for data in rank_data:
		
		response = None
		try:
			#response = br.open('http://www.ptt.cc/bbs/Gossiping/M.1398786724.A.D29.html')
			response = br.open(data['link'])
			print data['link']
		
			if response.geturl().find('over18') != -1:
				print 'over 18 page process'
				br.select_form(nr=0)
				response = br.submit(name='yes', label='yes')
		except:	
			response = None	
			
		if response is None:	
			continue 

		#取連結
		only_link = SoupStrainer('a', href=True)
		soup = BeautifulSoup(copy.copy(response), features=features, parse_only=only_link)
		print 'contentGet start parse link'	
		for link in soup.findAll('a', href=True):
			m = re.search('http://.+', link['href'])
			if not m is None:

				print '-origin-:' +  link['href'].encode('utf8')

				contenturl = link['href'].encode('utf8')

				response_link = None
				try:
					response_link = br.open(contenturl, timeout=30.0)
				except:	
					response_link = None		

				if not response_link is None:
					link_data = {}
					print response_link.geturl()
					link_data['origin'] = contenturl
					link_data['real'] = response_link.geturl()

					if link_data['real'] == data['link']:
						continue
					if link_data['real'].find('http://www.ptt.cc/') != -1:
						continue

					title = None
					try:
						print sys.getdefaultencoding()
						print 'a'
						if isinstance(br.title(), unicode):
							print 'a-1'
							title =  br.title().encode('utf8')
						else: 
							print 'a-2'
							title =  br.title().decode(sys.getdefaultencoding()).encode('utf8')
					except:	
						try:
							print 'b'
							soup2 = BeautifulSoup(copy.copy(response_link), features=features)
							print type(soup2.title.string)
							#title = soup2.title.string.decode(sys.getdefaultencoding()).encode('utf8')
							if isinstance(soup2.title.string, unicode):
								print 'b-1'
								title = soup2.title.string.encode('utf8')
							else: 
								print 'b-2'
								title = soup2.title.string.decode(sys.getdefaultencoding()).encode('utf8')
						except:		
							print 'c'
							title = link_data['real']	
					
					link_data['title'] = title	
					link_data['idx'] = data['push']['all']	
					link_data['from'] = data['link']
					print '>>>>>>>>>>>>>>>>>>>'
					print link_data['title'] 
					print link_data['real'] 
					print link_data['idx']
					print '<<<<<<<<<<<<<<<<<<<'
					links_data.append(link_data)

		#取keyword
		only_div_acticlemeta = SoupStrainer('div',  {"class":"article-metaline"})
		soup = BeautifulSoup(copy.copy(response), features=features, parse_only=only_div_acticlemeta)
		div = soup.find('div',  {"class":"bbs-screen bbs-content"})

		titles = soup.findAll('div',  {"class":"article-metaline"})
		[title.extract() for title in titles]
		titles2 = soup.findAll('div',  {"class":"article-metaline-right"})
		[title.extract() for title in titles2]
		pushs = soup.findAll('div',  {"class":"push"})
		[push.extract() for push in pushs]
		spans = soup.findAll('span',  {"class":"f2"})
		[span.extract() for span in spans]

		if not div is None:
			contenttext = ''
			for str in div.strings:
				contenttext += str
		
			tags = jieba.analyse.extract_tags( contenttext, topK=10)
			for tag in tags:
				if tag in keywords.keys():
					keywords[tag] = keywords[tag] + 1
				else:
					keywords[tag] = 1	

	sort_dict= sorted(keywords.iteritems(), key=lambda d:d[1], reverse = True)
	
	#for key in sort_dict:
	#	print key[0]

	for keyword_data in sort_dict:
		keyword = keyword_data[0].encode('utf8')
		count = keyword_data[1]
		findData = db.keyword.find_one({'keyword': keyword})
		if findData is None:
			db.keyword.insert({'keyword': keyword, 'count': count})
		else:
			findData['count'] = count
			db.keyword.save(findData)

	db.links.drop()
	for link_data in links_data:
		db.links.insert(link_data)
		

	jsonStr = json.dumps(sort_dict, indent=4)
	with open("keyword.json", "w") as f:
		f.write(jsonStr) 

if __name__ == "__main__":
	
	global br
	global features
	if platform.system() == 'Windows':
		features = 'html5lib'
	else:
		features = 'lxml'
	print 'use features: ' + features

	global db_address
	db_address = '127.0.0.1'
	#db_address = '54.251.147.205'
	
	#parse
	br = mechanize.Browser()
	br.set_handle_robots(False) # ignore robots
	br.set_handle_refresh(False)

	auth = tweepy.OAuthHandler('5As2TTlHzlSMto0elUTHFnyyT', 'YsEZpqKaAzlJN7FqyKgTLEzluNfeR4i39ICgmgh39OhMxWsnZl')
	auth.set_access_token('17033508-DshqArq0fbT7Qh2ALofLNehxOntA53VYvFvrKuFWk', 'MLEM2MuLKjd9kHvVjCsH8hcF65GZvDAwtDEgeU2skn9rV')
	api = tweepy.API(auth)		

	processBoard = [{'name': 'Gossiping'   , 'parseHour':24, 'rankHour':72 },  \
					{'name': 'beauty'      , 'parseHour':72, 'rankHour':72},  \
					{'name': 'joke'      , 'parseHour':72, 'rankHour':72},  \
					{'name': 'StupidClown'      , 'parseHour':72, 'rankHour':72},  \
					{'name': 'sex'      , 'parseHour':72, 'rankHour':72}]

	pre_time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
	tag = '#pttwatcher'
	api.update_status('ptt bbs data parse start.\n' + pre_time + '\n' + tag)			
	for boardData in processBoard:
		print '********* process' + boardData['name'] + '*********'
		#boardProcess(boardData)
		api.update_status( boardData['name'] + 'board rank data parse over.\n' + pre_time + '\n' + tag)				
		#parseKeyword(boardData)＃
		api.update_status( boardData['name'] + 'board other data parse over.\n' + pre_time + '\n' + tag)				
		
	
	conn=pymongo.Connection(db_address,27017)

	db = conn['setting']
	db.board_list.drop()
	for boardData in processBoard:
		boardName = boardData['name']
		db.board_list.insert({'board':boardName})
		
	api.update_status('ptt bbs data parse all over.\n' + pre_time + '\n' + tag)	
	
	

			 
	 

					  	
		
				