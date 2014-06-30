import ptt_parser
import pymongo

import facebook
import urllib
import urlparse
import subprocess
import warnings

def update_board_list(list):
	conn=pymongo.Connection('127.0.0.1',27017)
	# conn=pymongo.Connection('54.251.147.205',27017)

	db = conn['setting']
	db.board_list.drop()
	for board_name in list:
		db.board_list.insert({'board':board_name})

def update_board_data():
	board_list = ['Gossiping', 'Beauty', 'joke', 'StupidClown', 'sex', 'PublicIssue', 'HatePolitics', 'NBA', 'LoL']

	parser = ptt_parser.PttWebParser()
	parser.board_parse('Gossiping', 24)
	parser.board_parse('Beauty', 72)
	parser.board_parse('joke', 72)
	parser.board_parse('StupidClown', 72)
	parser.board_parse('sex', 72)
	parser.board_parse('PublicIssue', 72)
	parser.board_parse('HatePolitics', 72)
	parser.board_parse('NBA', 24)
	parser.board_parse('LoL', 24)
	update_board_list(board_list)		
	# parser.context_parse("https://www.ptt.cc/bbs/Gossiping/M.1403079856.A.F28.html")
	# parser.context_parse("https://www.ptt.cc/bbs/HatePolitics/M.1404095069.A.092.html")

def fb_test():
	#Trying to get an access token. Very awkward.
	oauth_args = dict(client_id     = '482698495096073',
	                  client_secret = '8c58b055fcb762a9780638dc401c85e2',
	                  grant_type    = 'client_credentials')
	oauth_curl_cmd = ['curl',
	                  'https://graph.facebook.com/oauth/access_token?' + urllib.urlencode(oauth_args)]
	oauth_response = subprocess.Popen(oauth_curl_cmd,
	                                  stdout = subprocess.PIPE,
	                                  stderr = subprocess.PIPE).communicate()[0]
	print oauth_response
	try:
	    oauth_access_token = urlparse.parse_qs(str(oauth_response))['access_token'][0]
	except KeyError:
	    print('Unable to grab an access token!')
	    exit()
	
	graph = facebook.GraphAPI(oauth_access_token)	
	print graph.get_object('http://www.yahoo.com')
	print graph.get_object('6127898346')

	# print graph.get_object('fql?q=SELECT%20url,%20normalized_url,%20share_count,%20like_count,%20comment_count,%20total_count,commentsbox_count,%20comments_fbid,%20click_count%20FROM%20link_stat%20WHERE%20url=%27http://www.yahoo.com%27')
	link = 'http://www.ptt.cc/bbs/sex/M.1401768579.A.49F.html'
	# print graph.fql({'example':"SELECT url,normalized_url,share_count,like_count,comment_count,total_count,commentsbox_count,comments_fbid,click_count FROM link_stat WHERE url=\'" + link+ "\'"})
	print graph.fql({'example':"SELECT url,normalized_url,share_count,like_count,comment_count,total_count,commentsbox_count,comments_fbid,click_count FROM link_stat WHERE url='http://www.ptt.cc/bbs/sex/M.1401781334.A.72D.html'"})
if __name__ == "__main__":
	
	update_board_data()
	#fb_test()
