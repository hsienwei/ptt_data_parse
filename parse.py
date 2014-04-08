# coding=utf8

import mechanize
import time
from bs4 import BeautifulSoup, SoupStrainer
import urllib
import re
import json


def formProcess2(url):
	global br
	global pageCount
	global groupData
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
	for recordDiv in soup.findAll("div", {"class":"r-ent"}):
		titleDiv = recordDiv.find("div", {"class":"title"})
		metaDiv = recordDiv.find("div", {"class":"meta"})

		titleLink = titleDiv.find('a', href=True);
		if not titleLink is None:
			print '==='
			print titleLink['href']
			print titleLink.string.encode('utf8')
			contentGet('http://www.ptt.cc' + titleLink['href'])

			keyString = '';
			if titleLink.string.encode('utf8').find('Re: ') != -1:  #回覆
				keyString = titleLink.string.encode('utf8')[4:];
			else:
				keyString = titleLink.string.encode('utf8');

			if keyString in groupData.keys():
				groupData[keyString]['groupList'].append({'title': titleLink.string.encode('utf8'), 'link':'http://www.ptt.cc' + titleLink['href']})
			else:
				groupData[keyString] = {'groupList':[{'title': titleLink.string.encode('utf8'), 'link':'http://www.ptt.cc' + titleLink['href']}]}

		dateDiv = metaDiv.find('div', {"class":"date"})	
		authorDiv = metaDiv.find('div', {"class":"author"})
		print dateDiv.string
		print authorDiv.string	

	pageCount = pageCount -1
	if pageCount != 0:
		formProcess2(nextLink)


def contentGet(contentLink):
	global br
	global linkData
	global contextData
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
		pushData = { 'g' : pushGoodCount, 'b': pushBadCount, 'n':pushNormalCount}
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
				try:
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
				except:		
					contenturl = link['href']

				links.append(contenturl)

				if contenturl in linkData:
					linkData[contenturl] = linkData[contenturl] + pushGoodCount + pushBadCount + pushNormalCount;
				else:
					linkData[contenturl] = pushGoodCount + pushBadCount + pushNormalCount;

		contextData[contentLink]['link'] = links			
					

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
			print '--' + data['title'] + ":" + data['link'].encode('utf8')

	jsonStr = json.dumps(contextData, indent=4)
	with open("contextData.json", "w") as f:
		f.write(jsonStr)	
	jsonStr = json.dumps(linkData, indent=4)
	with open("linkData.json", "w") as f:
		f.write(jsonStr)  
	jsonStr = json.dumps(groupData, indent=4)
	with open("groupData.json", "w") as f:
		f.write(jsonStr)       	
			