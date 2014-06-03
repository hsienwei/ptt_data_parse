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

import facebook
import urllib
import urlparse
import subprocess
import warnings
import subprocess


class TwitterRecorder:
	def	__init__(self):
		twitter_data = None
		with open("twitter_setting.json", "r") as f:
			twitter_data = f.read() 
		twitter_obj = json.loads(twitter_data)	
		auth = tweepy.OAuthHandler(twitter_obj['consumer_key'], twitter_obj['consumer_secret'])
		auth.set_access_token(twitter_obj['access_token'], twitter_obj['access_token_secret'])
		self.twitter_api = tweepy.API(auth)

		

	def twitter_update(self, msg):
		if not self.twitter_api is None:
			self.twitter_api.update_status(msg)


class PttWebParser	:
	def __init__(self):
		self.br = br = mechanize.Browser()
		self.br.set_handle_robots(False) # ignore robots
		self.br.set_handle_refresh(False)
		self.sixHourBeforeTime = time.time() - 60 * 60 * 6
		self.db_address = '127.0.0.1' #'54.251.147.205'

		if platform.system() == 'Windows':
			self.features = 'html5lib'
		else:
			self.features = 'lxml'

		oauth_args = dict(client_id     = '482698495096073',
	                  client_secret = '8c58b055fcb762a9780638dc401c85e2',
	                  grant_type    = 'client_credentials')

		oauth_curl_cmd = ['curl',
		                  'https://graph.facebook.com/oauth/access_token?' + urllib.urlencode(oauth_args)]
		oauth_response = subprocess.Popen(oauth_curl_cmd,
		                                  stdout = subprocess.PIPE,
		                                  stderr = subprocess.PIPE).communicate()[0]
		print oauth_curl_cmd
		print str(oauth_response)
		try:
		    oauth_access_token = urlparse.parse_qs(str(oauth_response))['access_token'][0]
		    self.graph = facebook.GraphAPI(oauth_access_token)
		except KeyError:
		    print('Unable to grab an access token!')
	
	def context_list_parse(self, link):

		flagStop = False
		list_detail = {}
		
		print 'process list:' + link
	
		try_time = 0
		response = None
		time.sleep(1)
		while (response is None):
			try:
				if try_time > 50:
					flagStop = True
					break
				response = self.br.open(link)
			except:	
				print 're Try'
				response = None	
			try_time = try_time + 1	
			time.sleep(3)	
	
		if flagStop:
			return list_detail
	
		if response.geturl().find('over18') != -1:
			print 'over 18 page process'
			self.br.select_form(nr=0)
			response = self.br.submit(name='yes', label='yes')
	
		nextIdx = 0;
		#nextLink = None
	
		only_div_btngroup = SoupStrainer("div", {"class":"btn-group pull-right"})
		only_div_r_ent = SoupStrainer("div", {"class":"r-ent"})
		#response2 = copy.copy(response)
		soup = BeautifulSoup(copy.copy(response), features=self.features, parse_only=only_div_btngroup);
		soup2 = BeautifulSoup(copy.copy(response), features=self.features, parse_only=only_div_r_ent);
	
		#下一頁面連結取得
		pageLinkDiv = soup.find("div", {"class":"btn-group pull-right"})
		for pageLink in pageLinkDiv.findAll('a', href=True):
			if pageLink.string.encode('utf8').find('上頁') != -1:
				# listLink = 'http://www.ptt.cc' + pageLink['href']
				list_detail['next_list'] = 'http://www.ptt.cc' + pageLink['href']

	
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
				
				if 'context_list' in list_detail:
					list_detail['context_list'].append({'title': titleLink.string.encode('utf8'), 'link': contentLink, 'cid': id})
				else:
					list_detail['context_list'] = []

		return list_detail		

	def context_parse(self, content_link):
		response = None
		print content_link
		try:
			response = self.br.open(content_link)
			print 'contentGet:' + response.geturl()

			if response.geturl().find('over18') != -1:
				print 'over 18 page process'
				self.br.select_form(nr=0)
				response = self.br.submit(name='yes', label='yes')
		except:	
			response = None

		content_obj = None
	
		if not response is None:
			only_div_push = SoupStrainer("div", {"class":"push"})
			soup = BeautifulSoup(copy.copy(response), features=self.features, parse_only=only_div_push)
			pushGoodCount = 0
			pushBadCount = 0
			pushNormalCount = 0
			print 'contentGet start parse push'
			pushTmpMonth = 0
			pushTmpYearOffset = 0
			extraPushPoint = 0
			for pushdiv in soup.findAll("div", {"class":"push"}):
				#print 'contentGet parse push'
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

				if m is None:
					continue

				if not m.groups()[1] is None: 
					parsedTime = parser.parse(m.groups()[1])
					#if pushTmpYearOffset > 0:
					#	parsedTime = parsedTime.replace(year=parsedTime.year+pushTmpYearOffset)
					parsedTimeStr = parsedTime.strftime("%Y-%m-%d %H:%M:%S")
					parsedTimeStamp = time.mktime(time.strptime(parsedTimeStr, '%Y-%m-%d %H:%M:%S'))
					if parsedTimeStamp > self.sixHourBeforeTime:
						extraPushPoint = extraPushPoint + 1;
					#print type(parsedTime)
					#print type(parsedTimeStr)
					#print parsedTimeStr
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
			# contextData[contentLink] = { 'push': pushData}
						
			links = []		
			only_link = SoupStrainer('a', href=True)
			soup = BeautifulSoup(copy.copy(response), features=self.features, parse_only=only_link)
			print 'contentGet start parse link'	
			for link in soup.findAll('a', href=True):
				print 'contentGet parse link'
				m = re.search('http://.+', link['href'])
				if not m is None:
	
					if link['href'] == content_link:
						continue
					if link['href'].find('http://www.ptt.cc/') != -1:
						continue	
	
					print '--' +  link['href'].encode('utf8')
	
					contenturl = link['href']
	
					links.append(contenturl)
	
					# if contenturl in linkData:
					# 	linkData[contenturl] = linkData[contenturl] + pushGoodCount + pushBadCount + pushNormalCount;
					# else:
					# 	linkData[contenturl] = pushGoodCount + pushBadCount + pushNormalCount;
			print 'contentGet end parse link'
			# contextData[contentLink]['link'] = links			
			
			#時間
			#<span class="article-meta-value">Tue Apr 15 00:07:21 2014</span>
			only_div_acticlemeta = SoupStrainer('div',  {"class":"article-metaline"})
			soup = BeautifulSoup(copy.copy(response), features=self.features, parse_only=only_div_acticlemeta)
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
	
					# print contextTime
					# print endTime
					# if contextTime < endTime:
					# 	print '===end'
					# 	flagStop = True
	
				if metaDivTag.string.encode('utf8').find('標題') != -1:
					#object['title'] = metaDivValue.string
					content_obj['title'] = metaDivValue.string
			print 'contentGet stop parse time'	

			keyword = self._keyword_parse(response)
			if keyword:
				content_obj['keyword'] = keyword

			links = self._link_parse(response, content_link)
			if len(links) > 0:
				content_obj['links'] = links

			fb_data = self._fb_parse(content_link)	
			content_obj['fb'] = fb_data

			score = pushData['g'] * 2 + pushData['b'] + pushData['n'] #fb_data['like_count'] + fb_data['share_count'] + fb_data['comment_count'] + pushData['g'] * 2 + pushData['b'] + pushData['n']
			if fb_data:
				score = score + fb_data['like_count'] + fb_data['share_count'] + fb_data['comment_count']
			content_obj['score'] = score
			
		return content_obj	

	def _fb_parse(self, origin_link):
		# #[{"like_count":1421162,"share_count":5664540,"comment_count":1748801}]
		# url = 'https://api.facebook.com/method/fql.query?format=json&query=select%20%20like_count,%20share_count,comment_count%20from%20link_stat%20where%20url=%22' + origin_link.string + '%22'
		# response = self.br.open(url, timeout=30.0)
		# response_str = response.read()
		# fb_json = json.loads(response_str)
		# time.sleep(3)
		# print fb_json
		# return fb_json[0]

		# [{u'fql_result_set': [{u'normalized_url': u'http://www.yahoo.com/', u'commentsbox_count': 4690, u'click_count': 0, u'url': u'http://www.yahoo.com', u'total_count': 259986, u'comment_count': 34555, u'like_count': 73902, u'comments_fbid': 386757221287, u'share_count': 151529}], u'name': u'example'}]
		fb_data = {}
		if  self.graph : #graph.fql({'example':"SELECT url,normalized_url,share_count,like_count,comment_count,total_count,commentsbox_count,comments_fbid,click_count FROM link_stat WHERE url=\'" + link+ "\'"})
			fql_str = "SELECT url,normalized_url,share_count,like_count,comment_count,total_count,commentsbox_count,comments_fbid,click_count FROM link_stat WHERE url=\'" + origin_link+ "\'"
			# fql_results = self.graph.fql({'example':"SELECT url,normalized_url,share_count,like_count,comment_count,total_count,commentsbox_count,comments_fbid,click_count FROM link_stat WHERE url='http://www.ptt.cc/bbs/sex/M.1401765380.A.52C.html'"})
			fql_results = self.graph.fql({'example': str(fql_str)})
			print fql_str
			print "<<<<<<<<"
			print fql_results
			for result in fql_results:
				if result['name'] == 'example':
					fb_data['share_count'] = result['fql_result_set'][0]['share_count']
					fb_data['like_count'] = result['fql_result_set'][0]['like_count']
					fb_data['comment_count'] = result['fql_result_set'][0]['comment_count']
		print fb_data		
		return fb_data

	def _link_parse(self, response, origin_link):
		#取連結
		only_link = SoupStrainer('a', href=True)
		soup = BeautifulSoup(copy.copy(response), features=self.features, parse_only=only_link)
		print 'contentGet start parse link'	
		link_ary = []
		for link in soup.findAll('a', href=True):
			m = re.search('http://.+', link['href'])
			if not m is None:

				print '-origin-:' +  link['href'].encode('utf8')

				contenturl = link['href'].encode('utf8')

				response_link = None
				try:
					response_link = self.br.open(contenturl, timeout=30.0)
				except:	
					response_link = None		

				if not response_link is None:
					link_data = {}
					print response_link.geturl()
					link_data['origin'] = contenturl
					link_data['real'] = response_link.geturl()

					if link_data['real'] == origin_link:
						continue
					if link_data['real'].find('http://www.ptt.cc/') != -1:
						continue

					title = None
					pre_word = ''
					try:
						'''
						print sys.getdefaultencoding()
						print 'a '
						pre_word = pre_word + 'a '
						if isinstance(self.br.title(), unicode):
							print 'a-1 '
							pre_word = pre_word + 'a-1 '
							title =  pre_word + self.br.title().encode('utf8')
						else: 
							print 'a-2 '
							pre_word = pre_word + 'a-2 '
							title =  pre_word + self.br.title().encode('utf8')
							'''
						title =  self.br.title().encode('utf8')	
					except:	
						'''
						print sys.exc_info()[0]
						try:
							pre_word = pre_word +  'b '
							print 'b '
							soup2 = BeautifulSoup(response_link.read().decode('utf-8', 'ignore'), features=self.features)
							#pre_word = pre_word +  type(soup2.title.string) + '  '
							#title = soup2.title.string.decode(sys.getdefaultencoding()).encode('utf8')
							if isinstance(soup2.title.string, unicode):
								print 'b-1 '
								pre_word = pre_word + 'b-1 '
								title = pre_word + soup2.title.string
							else: 
								print 'b-2 '
								pre_word = pre_word +  'b-2 '
								title = pre_word + soup2.title.string.decode(sys.getdefaultencoding()).encode('utf8')
						except:		
							print 'c'
							print sys.exc_info()[0]
							pre_word = pre_word +  'c '
							title = pre_word + link_data['real']	
						'''	
						title = link_data['real']	

					link_data['title'] = title	
					link_ary.append(link_data)
		return link_ary			

	def _keyword_parse(self, response):
		#取keyword
		only_div_acticlemeta = SoupStrainer('div',  {"class":"article-metaline"})
		soup = BeautifulSoup(copy.copy(response), features=self.features, parse_only=only_div_acticlemeta)
		div = soup.find('div',  {"class":"bbs-screen bbs-content"})

		titles = soup.findAll('div',  {"class":"article-metaline"})
		[title.extract() for title in titles]
		titles2 = soup.findAll('div',  {"class":"article-metaline-right"})
		[title.extract() for title in titles2]
		pushs = soup.findAll('div',  {"class":"push"})
		[push.extract() for push in pushs]
		spans = soup.findAll('span',  {"class":"f2"})
		[span.extract() for span in spans]

		tags = None
		if not div is None:
			contenttext = ''
			for str in div.strings:
				contenttext += str
		
			tags = jieba.analyse.extract_tags( contenttext, topK=10)		
			print tags
		return tags

	# #=======
	# def parseKeyword(board_data):
	# global br
	# global db_address

	# conn=pymongo.Connection(db_address,27017)
	# db = conn[board_data['name']]

	# rank_data = list(db.single.find({}, { '_id': 0}) \
	# 					    .sort([('push.all', pymongo.DESCENDING)]) \
	# 						.limit(50))	
	# keywords = {}
	# links_data = []

	# for data in rank_data:
		
	# 	response = None
	# 	try:
	# 		#response = br.open('http://www.ptt.cc/bbs/Gossiping/M.1398786724.A.D29.html')
	# 		response = br.open(data['link'])
	# 		print data['link']
		
	# 		if response.geturl().find('over18') != -1:
	# 			print 'over 18 page process'
	# 			br.select_form(nr=0)
	# 			response = br.submit(name='yes', label='yes')
	# 	except:	
	# 		response = None	
			
	# 	if response is None:	
	# 		continue 

	# 	#取連結
	# 	only_link = SoupStrainer('a', href=True)
	# 	soup = BeautifulSoup(copy.copy(response), features=features, parse_only=only_link)
	# 	print 'contentGet start parse link'	
	# 	for link in soup.findAll('a', href=True):
	# 		m = re.search('http://.+', link['href'])
	# 		if not m is None:

	# 			print '-origin-:' +  link['href'].encode('utf8')

	# 			contenturl = link['href'].encode('utf8')

	# 			response_link = None
	# 			try:
	# 				response_link = br.open(contenturl, timeout=30.0)
	# 			except:	
	# 				response_link = None		

	# 			if not response_link is None:
	# 				link_data = {}
	# 				print response_link.geturl()
	# 				link_data['origin'] = contenturl
	# 				link_data['real'] = response_link.geturl()

	# 				if link_data['real'] == data['link']:
	# 					continue
	# 				if link_data['real'].find('http://www.ptt.cc/') != -1:
	# 					continue

	# 				title = None
	# 				try:
	# 					print sys.getdefaultencoding()
	# 					print 'a'
	# 					if isinstance(br.title(), unicode):
	# 						print 'a-1'
	# 						title =  br.title().encode('utf8')
	# 					else: 
	# 						print 'a-2'
	# 						title =  br.title().decode(sys.getdefaultencoding()).encode('utf8')
	# 				except:	
	# 					try:
	# 						print 'b'
	# 						soup2 = BeautifulSoup(copy.copy(response_link), features=features)
	# 						print type(soup2.title.string)
	# 						#title = soup2.title.string.decode(sys.getdefaultencoding()).encode('utf8')
	# 						if isinstance(soup2.title.string, unicode):
	# 							print 'b-1'
	# 							title = soup2.title.string.encode('utf8')
	# 						else: 
	# 							print 'b-2'
	# 							title = soup2.title.string.decode(sys.getdefaultencoding()).encode('utf8')
	# 					except:		
	# 						print 'c'
	# 						title = link_data['real']	
					
	# 				link_data['title'] = title	
	# 				link_data['idx'] = data['push']['all']	
	# 				link_data['from'] = data['link']
	# 				print '>>>>>>>>>>>>>>>>>>>'
	# 				print link_data['title'] 
	# 				print link_data['real'] 
	# 				print link_data['idx']
	# 				print '<<<<<<<<<<<<<<<<<<<'
	# 				links_data.append(link_data)

	# 	#取keyword
	# 	only_div_acticlemeta = SoupStrainer('div',  {"class":"article-metaline"})
	# 	soup = BeautifulSoup(copy.copy(response), features=features, parse_only=only_div_acticlemeta)
	# 	div = soup.find('div',  {"class":"bbs-screen bbs-content"})

	# 	titles = soup.findAll('div',  {"class":"article-metaline"})
	# 	[title.extract() for title in titles]
	# 	titles2 = soup.findAll('div',  {"class":"article-metaline-right"})
	# 	[title.extract() for title in titles2]
	# 	pushs = soup.findAll('div',  {"class":"push"})
	# 	[push.extract() for push in pushs]
	# 	spans = soup.findAll('span',  {"class":"f2"})
	# 	[span.extract() for span in spans]

	# 	if not div is None:
	# 		contenttext = ''
	# 		for str in div.strings:
	# 			contenttext += str
		
	# 		tags = jieba.analyse.extract_tags( contenttext, topK=10)
	# 		for tag in tags:
	# 			if tag in keywords.keys():
	# 				keywords[tag] = keywords[tag] + 1
	# 			else:
	# 				keywords[tag] = 1	

	# sort_dict= sorted(keywords.iteritems(), key=lambda d:d[1], reverse = True)
	
	# #for key in sort_dict:
	# #	print key[0]

	# for keyword_data in sort_dict:
	# 	keyword = keyword_data[0].encode('utf8')
	# 	count = keyword_data[1]
	# 	findData = db.keyword.find_one({'keyword': keyword})
	# 	if findData is None:
	# 		db.keyword.insert({'keyword': keyword, 'count': count})
	# 	else:
	# 		findData['count'] = count
	# 		db.keyword.save(findData)

	# db.links.drop()
	# for link_data in links_data:
	# 	db.links.insert(link_data)
		

	# jsonStr = json.dumps(sort_dict, indent=4)
	# with open("keyword.json", "w") as f:
	# 	f.write(jsonStr) 
	# #=======		

	#當內文解析出了問題缺少資料，用清單的資料與其他資料來補
	def _complete_context(self, context_obj, list_data):
		print context_obj
		print list_data
		context_obj['id'] = list_data['cid']
					
		#內文title抓不到 用列表的
		if not 'title' in context_obj:
			context_obj['title'] = list_data['title']
		#內文時間抓不到 用現在時間頂替	
		if not 'time' in context_obj:	
			context_obj['time'] = time.time()
		#內文推文抓不到  用預設為0
		if not 'push' in context_obj:	
			context_obj['push'] = { 'g': 0, 'b': 0, 'all': 0 }
		context_obj['link'] = list_data['link']
	
		if not 'extra_push_point' in context_obj:	
			context_obj['extra_push_point'] = 0	

	#將單一文章資料存到資料庫中
	def _context_to_single_db(self, db, context_obj):
		#單一文章
		findDoc = db.single.find_one({'id': context_obj['id']})
		if findDoc is None:
			db.single.insert(context_obj)
			print 'add to db'
		else:
			findDoc['push'] = context_obj['push']
			db.single.save(findDoc)				
			print 'change db'		
	def _context_to_group_db(self, db, context_obj):
		context_id = context_obj['id']
		group_key_str = '';
		if context_obj['title'].find('Re: ') != -1:  #回覆
			group_key_str = context_obj['title'][4:];
		else:
			group_key_str = context_obj['title']		

		#群組文章
		find_group = db.group.find_one({'key': group_key_str})
		if find_group is None:
			group_data = {}
			group_data['key'] 		= group_key_str
			group_data['groupList'] = [context_id]
			group_data['time'] 		= time.time()
			db.group.insert(group_data)
		else:
			if not context_id in find_group['groupList']:
				find_group['groupList'].append(context_id)
				find_group['time'] = time.time()
					
			pushData = { 'g': 0, 'b': 0, 'n': 0, 'all': 0 }	
			for rec in db.single.find({"id":{"$in":find_group['groupList']}}):
				pushData['g'] += rec['push']['g']
				pushData['n'] += rec['push']['n']
				pushData['b'] += rec['push']['b']
			pushData['all'] = pushData['g'] + pushData['n'] + pushData['b']
			find_group['push'] = pushData
			db.group.save(find_group)	

	def board_parse(self, board_name, time_range):
		# global linkData
		# global contextData
		# global groupData
		# global contextData2
		
		# global curTime
		# global endTime
		# global flagStop
		# global listLink
		# global db_address
		# global sixHourBeforeTime
	
		linkData = {}
		contextData = {}
		groupData = {}
		contextData2 = {}
		flagStop = False
		curTime = time.time()
		print '=== start time ==='
		print curTime
		print datetime.datetime.fromtimestamp(curTime).strftime('%Y-%m-%d %H:%M:%S')
		endTime = curTime - 60 * 60 * time_range 
		#rangeDay = curTime - 60 * 60 * boardData['rankHour']
		sixHourBeforeTime = curTime - 60 * 60 * 6
		print datetime.datetime.fromtimestamp(endTime).strftime('%Y-%m-%d %H:%M:%S')
		print '=================='
	
    	#dataCollect();
		#board = 'beauty'#'Gossiping'
		list_link = "http://www.ptt.cc/bbs/" + board_name + "/index.html"
		# while flagStop is False:
		# 	formProcess2(listLink)#HatePolitics

		flag_stop = False
		while not list_link is None:
			context_list_obj = self.context_list_parse(list_link)
			for context_list in context_list_obj['context_list']:
				context_obj = self.context_parse(context_list['link'])
				if context_obj:
				 	self._complete_context(context_obj, context_list)
				 	
					#save to db
					#conn=pymongo.Connection('54.251.147.205',27017)
					conn=pymongo.Connection(self.db_address, 27017)
					db = conn[board_name]#conn['Gossiping']
					self._context_to_single_db(db, context_obj)
					self._context_to_group_db(db, context_obj)
					#如果超過指定時間結束
					if context_obj['time'] < endTime:
						flag_stop = True
			if flag_stop:
				list_link = None
			else:
				list_link = 	context_list_obj['next_list']
			print 	list_link
			
	
		# #print
		# for key in linkData.keys():
		# 	print key.encode('utf8') + ':' + str(linkData[key])
		# for key in contextData.keys():
		# 	print key.encode('utf8') + ':' + str(contextData[key]['push']) + ' - ' + str(contextData[key]['push']['g'] + contextData[key]['push']['b'] + contextData[key]['push']['n'])
		# 	for link in contextData[key]['link']:
		# 		print '-- link:' + link.encode('utf8')
		
		# jsonStr = json.dumps(contextData, indent=4)
		# with open("contextData.json", "w") as f:
		# 	f.write(jsonStr)	
		# jsonStr = json.dumps(linkData, indent=4)
		# with open("linkData.json", "w") as f:
		# 	f.write(jsonStr)  
		# jsonStr = json.dumps(contextData2, indent=4)
		# with open("contextData2.json", "w") as f:
		# 	f.write(jsonStr)	      	
		
	
		# for key in groupData.keys():
		# 	print key 
		# 	push = {"all": 0, "b": 0, "g": 0, "n": 0}
		# 	for data in groupData[key]['groupList']:
		# 		if not contextData2[data] is None:
		# 			print '--' + data
		# 			print contextData2[data]
		# 			if not contextData2[data]['push'] is None:
		# 				print contextData2[data]['push']
		# 				push['b'] = push['b'] + contextData2[data]['push']['b']
		# 				push['g'] = push['g'] + contextData2[data]['push']['g']
		# 				push['n'] = push['n'] + contextData2[data]['push']['n']
		# 				push['all'] = push['all'] + contextData2[data]['push']['all']
		# 	groupData[key]['push'] = push
	
		# #save to file
		# jsonStr = json.dumps(groupData, indent=4)
		# with open("groupData.json", "w") as f:
		# 	f.write(jsonStr) 
			
		
		# #save to db
		# #conn=pymongo.Connection('54.251.147.205',27017)
		# conn=pymongo.Connection(db_address,27017)
		# db = conn[boardData['name']]#conn['Gossiping']
	
		# #單一文章
		# for key in contextData2.keys():
		# 	findDoc = db.single.find_one({'id': key})
		# 	if findDoc is None:
		# 		db.single.insert(contextData2[key])
		# 	else:
		# 		findDoc['push'] = contextData2[key]['push']
		# 		db.single.save(findDoc)
	
		# #群組文章
		# for key in groupData.keys():
		# 	findDoc = db.group.find_one({'key': key})
		# 	if findDoc is None:
		# 		groupData[key]['time'] = curTime
		# 		db.group.insert(groupData[key])
		# 	else:
		# 		#data reset
		# 		for recId in groupData[key]['groupList']:
		# 			if not recId in findDoc['groupList']:
		# 				findDoc['groupList'].append(recId)
		# 				findDoc['time'] = curTime
	
		# 		print findDoc['groupList']
						
		# 		pushData = { 'g': 0, 'b': 0, 'n': 0, 'all': 0 }	
		# 		for rec in db.single.find({"id":{"$in":findDoc['groupList']}}):
		# 			pushData['g'] += rec['push']['g']
		# 			pushData['n'] += rec['push']['n']
		# 			pushData['b'] += rec['push']['b']
		# 		pushData['all'] = pushData['g'] + pushData['n'] + pushData['b']
		# 		findDoc['push'] = pushData
		# 		db.group.save(findDoc)	
				
		# #排行資料
		
		# #文章資料
		# '''		
		# rankdata = {}
		# rankdata['g'] = sorted(contextData2.items(), key=lambda t: t[1]['push']['g'], reverse=True)[:10]
		# rankdata['b'] = sorted(contextData2.items(), key=lambda t: t[1]['push']['b'], reverse=True)[:10]
		# rankdata['t'] = sorted(contextData2.items(), key=lambda t: t[1]['push']['all'], reverse=True)[:10]
		# rankdata['gg'] = sorted(groupData.items(), key=lambda t: t[1]['push']['g'], reverse=True)[:10]
		# rankdata['gb'] = sorted(groupData.items(), key=lambda t: t[1]['push']['b'], reverse=True)[:10]
		# rankdata['gt'] = sorted(groupData.items(), key=lambda t: t[1]['push']['all'], reverse=True)[:10]
		# jsonStr = json.dumps(rankdata, indent=4)
		# with open("rankdata.json", "w") as f:
		# 	f.write(jsonStr) 
		# 	'''
	
		# #資料庫資料
		# rankdata = {}
		# rankdata['t'] = list(db.single.find({'time':{"$gte":rangeDay}}, { '_id': 0}) \
		# 				  .sort([('push.all', pymongo.DESCENDING)]) \
		# 				  .limit(50))	
		# rankdata['g'] = list(db.single.find({'time':{"$gte":rangeDay}}, { '_id': 0}) \
		# 				  .sort([('push.g', pymongo.DESCENDING)]) \
		# 				  .limit(50))
		# rankdata['b'] = list(db.single.find({'time':{"$gte":rangeDay}}, { '_id': 0}) \
		# 				  .sort([('push.b', pymongo.DESCENDING)]) \
		# 				  .limit(50))
	
		# rankdata['gt'] = list(db.group.find({'time':{"$gte":rangeDay}}, { '_id': 0}) \
		# 				  .sort([('push.all', pymongo.DESCENDING)]) \
		# 				  .limit(50))
	
		# for gData in rankdata['gt']:
		# 	gData['groupListData'] = list(db.single.find({"id":{"$in":gData['groupList']}}, { '_id': 0}) \
		# 				  				.sort([('time', pymongo.ASCENDING)]) \
		# 				  				.limit(50))
	
		# rankdata['gg'] = list(db.group.find({'time':{"$gte":rangeDay}}, { '_id': 0}) \
		# 				  .sort([('push.g', pymongo.DESCENDING)]) \
		# 				  .limit(50))
		# for gData in rankdata['gg']:
		# 	gData['groupListData'] = list(db.single.find({"id":{"$in":gData['groupList']}}, { '_id': 0}) \
		# 				  				.sort([('time', pymongo.ASCENDING)]) \
		# 				  				.limit(50))
		# rankdata['gb'] = list(db.group.find({'time':{"$gte":rangeDay}}, { '_id': 0}) \
		# 				  .sort([('push.b', pymongo.DESCENDING)]) \
		# 				  .limit(50))
		# for gData in rankdata['gb']:
		# 	gData['groupListData'] = list(db.single.find({"id":{"$in":gData['groupList']}}, { '_id': 0}) \
		# 				  				.sort([('time', pymongo.ASCENDING)]) \
		# 				  				.limit(50))
		# rankdata['time'] = curTime
	
	
		
	
		# jsonStr = json.dumps(rankdata, indent=4)
		# with open("rankdata.json", "w") as f:
		# 	f.write(jsonStr) 	
		# db.rank.insert(rankdata)
	
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



def test1():
	#global features
	if platform.system() == 'Windows':
		features = 'html5lib'
	else:
		features = 'lxml'
	print 'use features: ' + features
	parser = PttWebParser()
	# print parser.context_parse('http://www.ptt.cc/bbs/Gossiping/M.1400819015.A.454.html')
	# print parser.context_parse('http://www.ptt.cc/bbs/Gossiping/M.1400819040.A.771.html')
	parser.board_parse('Gossiping', 24)



if __name__ == "__main__":
	test1()
	
	'''
	recorder = TwitterRecorder()
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

	# twitter_data = None
	# with open("twitter_setting.json", "r") as f:
	# 	twitter_data = f.read() 
	# twitter_obj = json.loads(twitter_data)	
	# auth = tweepy.OAuthHandler(twitter_obj['consumer_key'], twitter_obj['consumer_secret'])
	# auth.set_access_token(twitter_obj['access_token'], twitter_obj['access_token_secret'])
	# api = tweepy.API(auth)	

	processBoard = [{'name': 'Gossiping'   	, 'parseHour':24, 'rankHour':72 },  \
					{'name': 'beauty'      	, 'parseHour':72, 'rankHour':72},  \
					{'name': 'joke'      	, 'parseHour':72, 'rankHour':72},  \
					{'name': 'StupidClown'	, 'parseHour':72, 'rankHour':72},  \
					{'name': 'sex'      	, 'parseHour':72, 'rankHour':72}]

	pre_time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
	tag = '#pttWatcher'
	recorder.twitter_update('ptt bbs data parse start.\n' + pre_time + '\n' + tag)			
	for boardData in processBoard:
		print '********* process' + boardData['name'] + '*********'
		#boardProcess(boardData)
		#recorder.twitter_update( boardData['name'] + 'board rank data parse over.\n' + pre_time + '\n' + tag)				
		#parseKeyword(boardData)
		#recorder.twitter_update( boardData['name'] + 'board other data parse over.\n' + pre_time + '\n' + tag)				
		
	
	conn=pymongo.Connection(db_address,27017)

	db = conn['setting']
	db.board_list.drop()
	for boardData in processBoard:
		boardName = boardData['name']
		db.board_list.insert({'board':boardName})
		
	recorder.twitter_update('ptt bbs data parse all over.\n' + pre_time + '\n' + tag)	
	'''
	

			 
	 

					  	
		
				