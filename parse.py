import mechanize
from bs4 import BeautifulSoup, SoupStrainer
import urllib
import re


def formProcess2(url):
	global br
	global pageCount
	response = br.open(url)

	if response.geturl().find('over18') != -1:
		br.select_form(nr=0)
		response = br.submit(name='yes', label='yes')

	nextIdx = 0;
	nextLink = None
	for link in BeautifulSoup(response).findAll('a', href=True):
		m = re.search('.+\w\.\w{10}\.\w\.\w{3}\.html', link['href'])
		if not m is None:
			contentGet('http://www.ptt.cc' + link['href'])
		else:
			m = re.search('.+index([0-9]+).html', link['href'])
			if not m is None:
				idx = m.groups()[0]
				print 'find ' + idx
				if int(idx) != 1:
					print int(idx)
					if nextIdx == 0:
						nextIdx = int(idx)
						nextLink = 'http://www.ptt.cc' + link['href']
					elif nextIdx > int(idx):
						nextIdx = int(idx); 	
						nextLink = 'http://www.ptt.cc' + link['href']
	print nextLink	
	print nextIdx	
	print type(nextIdx)	
	pageCount = pageCount -1
	if pageCount != 0:
		formProcess2(nextLink)



def contentGet(contentLink):
	global br
	global linkData
	print contentLink
	try:
		response2 = br.open(contentLink)
		print response2.geturl()
	except:	
		response2 = None

	if not response2 is None:
	 
		for link in BeautifulSoup(response2).findAll('a', href=True):
			m = re.search('http://.+', link['href'])
			if not m is None:
				print '--' +  link['href']

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
					else:
						contenturl = link['href']
				except:		
					contenturl = link['href']

				if contenturl in linkData:
					linkData[contenturl] = linkData[contenturl] + 1
				else:
					linkData[contenturl] = 1				

if __name__ == "__main__":
	global br
	global linkData
	linkData = {}
	global pageCount
	pageCount = 10

	br = mechanize.Browser()
	br.set_handle_robots(False) # ignore robots
    #dataCollect();
	formProcess2("http://www.ptt.cc/bbs/Gossiping/index.html")

	for key in linkData.keys():
		print key + ':' + str(linkData[key])