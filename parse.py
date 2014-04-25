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

def formProcess2(url):
	global br
	global groupData
	global contextData2
	global listLink
	print 'process list:' + url

	response = None
	time.sleep(1)
	while (response is None):
		try:
			response = br.open(url)
		except:	
			print 're Try'
			response = None	
		time.sleep(3)	

	if response.geturl().find('over18') != -1:
		print 'over 18 page process'
		br.select_form(nr=0)
		response = br.submit(name='yes', label='yes')

	nextIdx = 0;
	#nextLink = None


	soup = BeautifulSoup(response, features='lxml');

	#下一頁面連結取得
	pageLinkDiv = soup.find("div", {"class":"btn-group pull-right"})
	for pageLink in pageLinkDiv.findAll('a', href=True):
		if pageLink.string.encode('utf8').find('上頁') != -1:
			listLink = 'http://www.ptt.cc' + pageLink['href']

	#文章列表
	for recordDiv in reversed(soup.findAll("div", {"class":"r-ent"})):
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
			
			if id in contextData2:
				object = contextData2[id]
			else:
				object = {}
				object['id'] = id
				contextData2[id] = object

			object['link'] = 'http://www.ptt.cc' + titleLink['href']
		
			time.sleep(0.2)
			contentGet(id, 'http://www.ptt.cc' + titleLink['href'])
	
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

		if flagStop:
			break

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
	print contentLink
	try:
		response2 = br.open(contentLink)
		print 'contentGet:' + response2.geturl()
	except:	
		response2 = None

	if not response2 is None:
		soup = BeautifulSoup(response2, features='lxml')
		pushGoodCount = 0
		pushBadCount = 0
		pushNormalCount = 0
		print 'contentGet start parse push'
		for pushdiv in soup.findAll("div", {"class":"push"}):
			print 'contentGet parse push'
			#print pushdiv
			#push
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
		print 'contentGet end parse push'
		pushData = { 'all':pushGoodCount + pushBadCount + pushNormalCount,  'g' : pushGoodCount, 'b': pushBadCount, 'n':pushNormalCount}
		object = contextData2[id]
		object['push'] = pushData
		contextData[contentLink] = { 'push': pushData}
					
		links = []		
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

				contenturl = ''
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
				object['time'] = contextTime

				print contextTime
				print endTime
				if contextTime < endTime:
					print '===end'
					flagStop = True

			if metaDivTag.string.encode('utf8').find('標題') != -1:
				object['title'] = metaDivValue.string
		print 'contentGet stop parse time'		


def boardProcess(boardData):
	global linkData
	global contextData
	global groupData
	global contextData2
	
	global curTime
	global endTime
	global flagStop
	global listLink

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
			print '--' + data
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
	conn=pymongo.Connection('54.251.147.205',27017)
	#conn=pymongo.Connection('127.0.0.1',27017)
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

if __name__ == "__main__":
	
	global br
	
	#parse
	br = mechanize.Browser()
	br.set_handle_robots(False) # ignore robots

	processBoard = [{'name': 'Gossiping'   , 'parseHour':24, 'rankHour':72 },  \
					{'name': 'beauty'      , 'parseHour':72, 'rankHour':72}]

	for boardData in processBoard:
		print '********* process' + boardData['name'] + '*********'
		boardProcess(boardData)

					  	
		
				