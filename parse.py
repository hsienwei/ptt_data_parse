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

def formProcess2(url):
	global br
	global pageCount
	global groupData
	global contextData2
	print 'process list:' + url
	print str(pageCount)
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
	nextLink = None


	soup = BeautifulSoup(response);

	#下一頁面連結取得
	pageLinkDiv = soup.find("div", {"class":"btn-group pull-right"})
	for pageLink in pageLinkDiv.findAll('a', href=True):
		if pageLink.string.encode('utf8').find('上頁') != -1:
			nextLink = 'http://www.ptt.cc' + pageLink['href']

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
				contextData2[id] = object

			object['link'] = 'http://www.ptt.cc' + titleLink['href']
		
	
			contentGet(id, 'http://www.ptt.cc' + titleLink['href'])
	
			keyString = '';
			if titleLink.string.encode('utf8').find('Re: ') != -1:  #回覆
				keyString = titleLink.string.encode('utf8')[4:];
			else:
				keyString = titleLink.string.encode('utf8');

			if keyString in groupData.keys():
				groupData[keyString]['groupList'].append(id)
			else:
				groupData[keyString] = {'groupList':[id]}

		dateDiv = metaDiv.find('div', {"class":"date"})	
		authorDiv = metaDiv.find('div', {"class":"author"})
		print dateDiv.string
		print authorDiv.string	

		if flagStop:
			break

	print '----====----==----'
	print flagStop
	if flagStop != True:
		formProcess2(nextLink)


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
		soup = BeautifulSoup(response2)
		pushGoodCount = 0
		pushBadCount = 0
		pushNormalCount = 0
		for pushdiv in soup.findAll("div", {"class":"push"}):
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
		pushData = { 'all':pushGoodCount + pushBadCount + pushNormalCount,  'g' : pushGoodCount, 'b': pushBadCount, 'n':pushNormalCount}
		object = contextData2[id]
		object['push'] = pushData
		contextData[contentLink] = { 'push': pushData}
					
		links = []			
		for link in soup.findAll('a', href=True):
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

		contextData[contentLink]['link'] = links			
		
		#時間
		#<span class="article-meta-value">Tue Apr 15 00:07:21 2014</span>
		for metaDiv in soup.findAll('div',  {"class":"article-metaline"}):
			metaDivTag = metaDiv.find('span',  {"class":"article-meta-tag"})
			metaDivValue = metaDiv.find('span',  {"class":"article-meta-value"})
			if metaDivTag.string.encode('utf8').find('時間') != -1:
				print metaDivValue.string
				print parser.parse(metaDivValue.string)
				object['time'] = parser.parse(metaDivValue.string).strftime("%Y-%m-%d %H:%M:%S")

				contextTime = time.mktime(time.strptime(object['time'], '%Y-%m-%d %H:%M:%S'))
				print contextTime
				print endTime
				if contextTime < endTime:
					print '===end'
					flagStop = True

			if metaDivTag.string.encode('utf8').find('標題') != -1:
				object['title'] = metaDivValue.string


if __name__ == "__main__":
	global br
	global linkData
	linkData = {}
	global contextData
	contextData = {}
	global groupData
	groupData = {}
	global pageCount
	pageCount = 30
	global contextData2
	contextData2 = {}

	global curTime
	global endTime
	global flagStop
	flagStop = False
	curTime = time.time()
	print '=== start time ==='
	print curTime
	print datetime.datetime.fromtimestamp(curTime).strftime('%Y-%m-%d %H:%M:%S')
	endTime = curTime - 60 * 30#60 * 60 * 24
	print datetime.datetime.fromtimestamp(endTime).strftime('%Y-%m-%d %H:%M:%S')
	print '=================='

	br = mechanize.Browser()
	br.set_handle_robots(False) # ignore robots
    #dataCollect();
	formProcess2("http://www.ptt.cc/bbs/Gossiping/index.html")#HatePolitics
	for key in linkData.keys():
		print key.encode('utf8') + ':' + str(linkData[key])
	for key in contextData.keys():
		print key.encode('utf8') + ':' + str(contextData[key]['push']) + ' - ' + str(contextData[key]['push']['g'] + contextData[key]['push']['b'] + contextData[key]['push']['n'])
		for link in contextData[key]['link']:
			print '-- link:' + link
	for key in groupData.keys():
		print key 
		
		for data in groupData[key]['groupList']:
			print '--' + data

	jsonStr = json.dumps(contextData, indent=4)
	with open("contextData.json", "w") as f:
		f.write(jsonStr)	
	jsonStr = json.dumps(linkData, indent=4)
	with open("linkData.json", "w") as f:
		f.write(jsonStr)  
	jsonStr = json.dumps(groupData, indent=4)
	with open("groupData.json", "w") as f:
		f.write(jsonStr) 
	jsonStr = json.dumps(contextData2, indent=4)
	with open("contextData2.json", "w") as f:
		f.write(jsonStr)	      	
			
	rankdata = {}
	rankdata['g'] = sorted(contextData2.items(), key=lambda t: t[1]['push']['g'], reverse=True)[:10]
	rankdata['b'] = sorted(contextData2.items(), key=lambda t: t[1]['push']['b'], reverse=True)[:10]
	rankdata['t'] = sorted(contextData2.items(), key=lambda t: t[1]['push']['all'], reverse=True)[:10]
	jsonStr = json.dumps(rankdata, indent=4)
	with open("rankdata.json", "w") as f:
		f.write(jsonStr) 
	