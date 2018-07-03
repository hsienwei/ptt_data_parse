# coding=utf8

#import mechanize
import dynamodb_conn
import time
#from bs4 import BeautifulSoup, SoupStrainer
import urllib
import re
import json
# pip install  python-dateutil
from dateutil import parser
import time
import datetime
#import pymongo
import copy
import platform
import sys, os
import shutil

# install facebook module : https://facebook-sdk.readthedocs.io/en/latest/install.html#installing-from-git
import facebook
import urllib
#import urlparse
import subprocess
import warnings
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By

#pip install boto3


from multiprocessing import Pool, Process, Value, Array, Manager, Lock

def run_context_parse(obj, param):
    print('empty')
    #context = obj.context_parse(param)
    #with open((os.path.dirname(os.path.abspath(__file__)) + "/temp.json"), "w") as f:  
    #   f.write(json.dumps(context, indent=4))


class PttWebParser  :
    def __init__(self):

        self.web = webdriver.Chrome(executable_path=r'.\chromedriver.exe')

        fb_data = None
        with open("fb_setting.json", "r") as f:
            fb_data = f.read() 
        fb_obj = json.loads(fb_data)    
    
        self.graph = facebook.GraphAPI()
        self.graph.access_token = self.graph.get_app_access_token(fb_obj['app_id'], fb_obj['app_secret'])

    
    '''
    def _pre_dict_combine(self, combine_file_path):
        origin_file = 'dict.txt.big'
        customize_file = 'dict.txt'
        origin_data = {}
        customize_data = {}
        add_data = {}
        with open(origin_file, 'r') as fo:
            for line in fo.readlines(): 
                list = line.split(' ')
                data = {}
                if list[0]:
                    data['key'] = list[0]
                if list[1]:
                    data['feq'] = list[1]
                if list[2]:
                    data['type'] = list[2]      
                origin_data[list[0]] = data

        with open(customize_file, 'r') as fc:
            for line in fc.readlines(): 
                list = line.split(' ')
                data = {}
                if list[0]:
                    data['key'] = list[0]
                if list[1]:
                    data['feq'] = list[1]
                if list[2]:
                    data['type'] = list[2]      
                customize_data[list[0]] = data
        #print customize_data
        for key in customize_data:
            if not key in origin_data:
                add_data[key] = customize_data[key]

        shutil.copyfile(origin_file, combine_file_path)
        with open(combine_file_path, 'a') as f:
            for key in add_data:
                data = add_data[key]
                f.write(data['key'] + ' ' + data['feq'] + ' ' + data['type'])
        #print add_data     
    '''
    def context_over18(self):
        if self.web.current_url.find('over18') != -1:
            print ('over 18 page process')
            yes = self.web.find_element_by_xpath("//button[@name='yes']")
            yes.click()


    def context_list_parse(self, link):

        list_detail = {}
        
        print ('process list:' + link)
    
        try_time = 0
        time.sleep(1)
        while (True): 
            try:
                if try_time > 50:
                    flagStop = True
                    break
                self.web.get(link)
            
            except Exception as e:
                #logger.error('Failed to upload to ftp: '+ str(e))
                print(str(e))
                print ('re Try')
            try_time = try_time + 1 

            try:
                a = self.web.find_element_by_css_selector('.bbs-content')
                print(a)
                break
            except selenium.common.exceptions.NoSuchElementException as ne:
                print ('re Try')
            

        self.context_over18()
            
    
        nextIdx = 0
    
        #下一頁面連結取得
        pageLinkDiv = self.web.find_element_by_css_selector('.btn-group.btn-group-paging')   

        pre_link_a = pageLinkDiv.find_element_by_xpath(".//a[2]")
        print(pre_link_a.text)
        next_link = pre_link_a.get_property("href")
        print(next_link)
        list_detail['next_list'] = next_link
    
        #文章列表
        page_content = self.web.find_element_by_css_selector('.r-list-container.action-bar-margin.bbs-screen')

        content_list = page_content.find_elements_by_tag_name('div')

        for content in content_list:
            
            if content.get_attribute('class') == 'r-list-sep':
                break
            if content.get_attribute('class') == 'r-ent':
                try:
                    title_elm = content.find_element_by_class_name('title')
                    link_elm = title_elm.find_element_by_tag_name('a') 
                    meta_elm = content.find_element_by_class_name('meta')
                    date_elm = meta_elm.find_element_by_class_name('date')
                    nrec_elm = content.find_element_by_class_name('nrec')
                    push_elm = nrec_elm.find_element_by_tag_name('span')
                except:
                    continue
                title = link_elm.text
                link = link_elm.get_property("href")
                print(title)
                print(link)

                m = re.search('\/bbs\/([A-Za-z0-9_\-]+)\/([A-Za-z0-9\.]+)\.html', link)
                id = m.groups()[1]
                print(id)

                m = re.search('([0-9]+)\/([0-9]+)', date_elm.text)
                print(date_elm.text)
                date = int(m.groups()[0]) * 100 + int(m.groups()[1])
                print(date)

                push_cnt = 0
                if '爆' in push_elm.text:
                    push_cnt = 100
                elif 'X' not in push_elm.text:
                    push_cnt = int(push_elm.text)
            
                if 'context_list' not in list_detail:
                    list_detail['context_list'] = []

                fb = self._fb_parse(link, push_cnt)
                score = fb['reaction_count'] + fb['comment_count'] + fb['share_count'] + fb['comment_plugin_count'] + push_cnt
                print(score)
                list_detail['context_list'].append(
                    {
                        'title': title, 
                        'link': link, 
                        'cid': id, 
                        'push' : push_cnt, 
                        'date' : date_elm.text, 
                        'fb' : fb, 
                        'score' : score
                    })
                
        return list_detail      

    def context_parse(self, content_link):
        is_success = True
        print (content_link)
        content_obj = {}
        try:
            self.web.get(content_link)
            self.context_over18()
        except: 
            is_success = False

        if is_success:
            page_content = self.web.find_element_by_css_selector('.bbs-screen.bbs-content')

            article_elm = page_content.find_elements_by_class_name('article-metaline')
            print(article_elm)
            if len(article_elm) is 0:
                return content_obj
            
            time_str = article_elm[2].find_element_by_class_name('article-meta-value').text
            print(time_str)
            parsedTimeStr = parser.parse(time_str).strftime("%Y-%m-%d %H:%M:%S")
            print(parsedTimeStr)
            contextTime = time.mktime(time.strptime(parsedTimeStr, '%Y-%m-%d %H:%M:%S'))
            print(contextTime)
            

            content_obj['time'] = contextTime
            '''
            only_div_push = SoupStrainer("div", {"class":"push"})
            soup = BeautifulSoup(copy.copy(response), features=self.features, parse_only=only_div_push)
            pushGoodCount = 0
            pushBadCount = 0
            pushNormalCount = 0
            print ('contentGet start parse push')
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
                    #   parsedTime = parsedTime.replace(year=parsedTime.year+pushTmpYearOffset)
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
            print ('pushAllCount ' + str(pushGoodCount + pushBadCount + pushNormalCount))
            print ('extraPushPoint ' + str(extraPushPoint))
    
            print ('contentGet end parse push')
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
            print ('contentGet start parse link')
            for link in soup.findAll('a', href=True):
                print ('contentGet parse link')
                m = re.search('http://.+', link['href'])
                if not m is None:
    
                    if link['href'] == content_link:
                        continue
                    if link['href'].find('http://www.ptt.cc/') != -1:
                        continue    
    
                    print ('--' +  link['href'].encode('utf8'))
    
                    contenturl = link['href']
    
                    links.append(contenturl)
    
                    # if contenturl in linkData:
                    #   linkData[contenturl] = linkData[contenturl] + pushGoodCount + pushBadCount + pushNormalCount;
                    # else:
                    #   linkData[contenturl] = pushGoodCount + pushBadCount + pushNormalCount;
            print ('contentGet end parse link')
            # contextData[contentLink]['link'] = links          
            
            #時間
            #<span class="article-meta-value">Tue Apr 15 00:07:21 2014</span>
            only_div_acticlemeta = SoupStrainer('div',  {"class":"article-metaline"})
            soup = BeautifulSoup(copy.copy(response), features=self.features, parse_only=only_div_acticlemeta)
            print ('contentGet start parse time')
            for metaDiv in soup.findAll('div',  {"class":"article-metaline"}):
                print ('contentGet parse time')
                metaDivTag = metaDiv.find('span',  {"class":"article-meta-tag"})
                metaDivValue = metaDiv.find('span',  {"class":"article-meta-value"})
                try:
                    if metaDivTag.string.encode('utf8').find('時間') != -1:
                        print (metaDivValue.string)
                        print (parser.parse(metaDivValue.string))
                        #object['time'] = parser.parse(metaDivValue.string).strftime("%Y-%m-%d %H:%M:%S")
                        #contextTime = time.mktime(time.strptime(object['time'], '%Y-%m-%d %H:%M:%S'))
                        parsedTimeStr = parser.parse(metaDivValue.string).strftime("%Y-%m-%d %H:%M:%S")
                        contextTime = time.mktime(time.strptime(parsedTimeStr, '%Y-%m-%d %H:%M:%S'))
                        #object['time'] = contextTime
                        content_obj['time'] = contextTime
                except:
                    print ('time format error') 
    
                    # print contextTime
                    # print endTime
                    # if contextTime < endTime:
                    #   print '===end'
                    #   flagStop = True
    
                if metaDivTag.string.encode('utf8').find('標題') != -1:
                    #object['title'] = metaDivValue.string
                    content_obj['title'] = metaDivValue.string
            print ('contentGet stop parse time')    

            keyword = self._keyword_parse(response)
            if keyword:
                content_obj['keyword'] = keyword

            links = self._link_parse(response, content_link)
            if len(links) > 0:
                content_obj['links'] = links

            fb_data = self._fb_parse(content_link, pushData['g'])   
            content_obj['fb'] = fb_data

            score = pushData['g'] * 2 + pushData['b'] + pushData['n'] #fb_data['like_count'] + fb_data['share_count'] + fb_data['comment_count'] + pushData['g'] * 2 + pushData['b'] + pushData['n']
            if fb_data:
                score = score + fb_data['like_count'] + fb_data['share_count'] + fb_data['comment_count']
            content_obj['score'] = score
            '''
        return content_obj  

    def _fb_parse(self, origin_link, push_count):
        
        if  self.graph : 
            # ref: https://developers.facebook.com/docs/graph-api/reference/v2.11/url/
            fb_get = self.graph.get_object(id=origin_link, fields="engagement")
            
            #
            # 以下取like數, 感覺數字不太有用, 註解起來
            #
            '''
            fb_get2 = self.graph.get_object(id=origin_link, fields="og_object")
            print(fb_get2)
            if 'og_object' in fb_get2:
                # ref: https://developers.facebook.com/docs/graph-api/reference/v2.11/object/likes
                like_cnt = self.graph.get_object(id=fb_get2['og_object']['id'] + '/likes', summary=True)
                print(like_cnt)
                fb_get['engagement']['likes'] = like_cnt['summary']['total_count']
            '''
                
            
        return fb_get['engagement']

    def _link_parse(self, response, origin_link):
        #取連結
        only_link = SoupStrainer('a', href=True)
        soup = BeautifulSoup(copy.copy(response), features=self.features, parse_only=only_link)
        print ('contentGet start parse link')
        link_ary = []
        for link in soup.findAll('a', href=True):
            m = re.search('http[s]?://.+', link['href'])
            if not m is None:

                print ('-origin-:' +  link['href'].encode('utf8'))

                contenturl = link['href'].encode('utf8')

                response_link = None
                try:
                    response_link = self.br.open(contenturl, timeout=30.0)
                except: 
                    response_link = None        

                if not response_link is None:
                    link_data = {}
                    print (response_link.geturl())
                    link_data['origin'] = contenturl
                    link_data['real'] = response_link.geturl()

                    if link_data['real'] == origin_link:
                        continue
                    m = re.search('http[s]?://www.ptt.cc/.+', link_data['real'])
                    if not m is None:
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
                        try:
                            soup2 = BeautifulSoup(response_link.read().decode('utf-8', 'ignore'), features=self.features)
                            if isinstance(soup2.title.string, unicode):
                                title = soup2.title.string
                            else:   
                                title = pre_word + soup2.title.string.decode(sys.getdefaultencoding()).encode('utf8')
                        except:             
                            title = link_data['real']   

                    link_data['title'] = title  
                    link_ary.append(link_data)
        return link_ary         
    '''
    def _keyword_parse(self, response):
        #取keyword
        #only_div_acticlemeta = SoupStrainer('div',  {"class":"article-metaline"})
        soup = BeautifulSoup(copy.copy(response), features=self.features)
        div = soup.find('div',  {"class":"bbs-screen bbs-content"})

        titles = soup.findAll('div',  {"class":"article-metaline"})
        [title.extract() for title in titles]
        titles2 = soup.findAll('div',  {"class":"article-metaline-right"})
        [title.extract() for title in titles2]
        pushs = soup.findAll('div',  {"class":"push"})
        [push.extract() for push in pushs]
        spans = soup.findAll('span',  {"class":"f2"})
        [span.extract() for span in spans]
        richcontents = soup.findAll('div',  {"class":"richcontent"})
        [richcontent.extract() for richcontent in richcontents]
        tags = None
        
        if not div is None:
            contenttext = ''
            for str in div.strings:
                contenttext += str
            m = re.match('((.*\n)*)(\-{2}\n(.*\n)*?\-{2}\n*$)', contenttext)
            if  m != None:
                contenttext = m.groups()[0]
            
            tags = jieba.analyse.extract_tags( contenttext, topK=30)        
            # print contenttext
            # print '================'  
            print (tags)
        return tags
    ''' 

    # #=======
    # def parseKeyword(board_data):
    # global br
    # global db_address

    # conn=pymongo.Connection(db_address,27017)
    # db = conn[board_data['name']]

    # rank_data = list(db.single.find({}, { '_id': 0}) \
    #                       .sort([('push.all', pymongo.DESCENDING)]) \
    #                       .limit(50)) 
    # keywords = {}
    # links_data = []

    # for data in rank_data:
        
    #   response = None
    #   try:
    #       #response = br.open('http://www.ptt.cc/bbs/Gossiping/M.1398786724.A.D29.html')
    #       response = br.open(data['link'])
    #       print data['link']
        
    #       if response.geturl().find('over18') != -1:
    #           print 'over 18 page process'
    #           br.select_form(nr=0)
    #           response = br.submit(name='yes', label='yes')
    #   except: 
    #       response = None 
            
    #   if response is None:    
    #       continue 

    #   #取連結
    #   only_link = SoupStrainer('a', href=True)
    #   soup = BeautifulSoup(copy.copy(response), features=features, parse_only=only_link)
    #   print 'contentGet start parse link' 
    #   for link in soup.findAll('a', href=True):
    #       m = re.search('http://.+', link['href'])
    #       if not m is None:

    #           print '-origin-:' +  link['href'].encode('utf8')

    #           contenturl = link['href'].encode('utf8')

    #           response_link = None
    #           try:
    #               response_link = br.open(contenturl, timeout=30.0)
    #           except: 
    #               response_link = None        

    #           if not response_link is None:
    #               link_data = {}
    #               print response_link.geturl()
    #               link_data['origin'] = contenturl
    #               link_data['real'] = response_link.geturl()

    #               if link_data['real'] == data['link']:
    #                   continue
    #               if link_data['real'].find('http://www.ptt.cc/') != -1:
    #                   continue

    #               title = None
    #               try:
    #                   print sys.getdefaultencoding()
    #                   print 'a'
    #                   if isinstance(br.title(), unicode):
    #                       print 'a-1'
    #                       title =  br.title().encode('utf8')
    #                   else: 
    #                       print 'a-2'
    #                       title =  br.title().decode(sys.getdefaultencoding()).encode('utf8')
    #               except: 
    #                   try:
    #                       print 'b'
    #                       soup2 = BeautifulSoup(copy.copy(response_link), features=features)
    #                       print type(soup2.title.string)
    #                       #title = soup2.title.string.decode(sys.getdefaultencoding()).encode('utf8')
    #                       if isinstance(soup2.title.string, unicode):
    #                           print 'b-1'
    #                           title = soup2.title.string.encode('utf8')
    #                       else: 
    #                           print 'b-2'
    #                           title = soup2.title.string.decode(sys.getdefaultencoding()).encode('utf8')
    #                   except:     
    #                       print 'c'
    #                       title = link_data['real']   
                    
    #               link_data['title'] = title  
    #               link_data['idx'] = data['push']['all']  
    #               link_data['from'] = data['link']
    #               print '>>>>>>>>>>>>>>>>>>>'
    #               print link_data['title'] 
    #               print link_data['real'] 
    #               print link_data['idx']
    #               print '<<<<<<<<<<<<<<<<<<<'
    #               links_data.append(link_data)

    #   #取keyword
    #   only_div_acticlemeta = SoupStrainer('div',  {"class":"article-metaline"})
    #   soup = BeautifulSoup(copy.copy(response), features=features, parse_only=only_div_acticlemeta)
    #   div = soup.find('div',  {"class":"bbs-screen bbs-content"})

    #   titles = soup.findAll('div',  {"class":"article-metaline"})
    #   [title.extract() for title in titles]
    #   titles2 = soup.findAll('div',  {"class":"article-metaline-right"})
    #   [title.extract() for title in titles2]
    #   pushs = soup.findAll('div',  {"class":"push"})
    #   [push.extract() for push in pushs]
    #   spans = soup.findAll('span',  {"class":"f2"})
    #   [span.extract() for span in spans]

    #   if not div is None:
    #       contenttext = ''
    #       for str in div.strings:
    #           contenttext += str
        
    #       tags = jieba.analyse.extract_tags( contenttext, topK=10)
    #       for tag in tags:
    #           if tag in keywords.keys():
    #               keywords[tag] = keywords[tag] + 1
    #           else:
    #               keywords[tag] = 1   

    # sort_dict= sorted(keywords.iteritems(), key=lambda d:d[1], reverse = True)
    
    # #for key in sort_dict:
    # # print key[0]

    # for keyword_data in sort_dict:
    #   keyword = keyword_data[0].encode('utf8')
    #   count = keyword_data[1]
    #   findData = db.keyword.find_one({'keyword': keyword})
    #   if findData is None:
    #       db.keyword.insert({'keyword': keyword, 'count': count})
    #   else:
    #       findData['count'] = count
    #       db.keyword.save(findData)

    # db.links.drop()
    # for link_data in links_data:
    #   db.links.insert(link_data)
        

    # jsonStr = json.dumps(sort_dict, indent=4)
    # with open("keyword.json", "w") as f:
    #   f.write(jsonStr) 
    # #=======      

    #當內文解析出了問題缺少資料，用清單的資料與其他資料來補
    def _complete_context(self, context_obj, list_data):
        print (context_obj)
        print (list_data)
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
            print ('add to db')
        else:
            findDoc['push'] = context_obj['push']
            findDoc['fb'] = context_obj['fb']
            findDoc['score'] = context_obj['score']
            db.single.save(findDoc)             
            print ('change db')     
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
            group_data['key']       = group_key_str
            group_data['groupList'] = [context_id]
            group_data['time']      = time.time()
            score = 0
            for rec in db.single.find({"id":{"$in":group_data['groupList']}}):
                if 'score' in rec:
                    score += rec['score']
            group_data['score'] = score 
            db.group.insert(group_data)
        else:
            if not context_id in find_group['groupList']:
                find_group['groupList'].append(context_id)
                find_group['time'] = time.time()
                    
            # pushData = { 'g': 0, 'b': 0, 'n': 0, 'all': 0 }   
            score = 0
            for rec in db.single.find({"id":{"$in":find_group['groupList']}}):
                if 'score' in rec:
                    score += rec['score']
                # pushData['g'] += rec['push']['g']
                # pushData['n'] += rec['push']['n']
                # pushData['b'] += rec['push']['b']
            # pushData['all'] = pushData['g'] + pushData['n'] + pushData['b']
            find_group['score'] = score
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
    
        list_data = []
        linkData = {}
        contextData = {}
        groupData = {}
        contextData2 = {}
        flagStop = False
        cur_time = time.time()
        print ('=== start time ===')
        print (datetime.datetime.fromtimestamp(cur_time).strftime('%Y-%m-%d %H:%M:%S'))
        target_time = cur_time - 60 * 60 * time_range
        print (datetime.datetime.fromtimestamp(target_time).strftime('%Y-%m-%d %H:%M:%S'))
        print ('==================')
    
        #dataCollect();
        list_link = "http://www.ptt.cc/bbs/" + board_name + "/index.html"
        # while flagStop is False:
        #   formProcess2(listLink)#HatePolitics

        flag_stop = False
        #count = 0
        while not list_link is None:
            context_list_obj = self.context_list_parse(list_link)

            for data in context_list_obj['context_list']:
                list_data.append(data)

            # 檢查最後一則的時間.
            list_last_link = context_list_obj['context_list'][0]['link']
            print('-----------' + list_last_link)
            context = self.context_parse(list_last_link)

            if context['time'] < target_time:
                flag_stop = True
                    
            if flag_stop:
                list_link = None
            else:
                list_link = context_list_obj['next_list']
            print   (list_link)
            

        return list_data

        
        # #print
        # for key in linkData.keys():
        #   print key.encode('utf8') + ':' + str(linkData[key])
        # for key in contextData.keys():
        #   print key.encode('utf8') + ':' + str(contextData[key]['push']) + ' - ' + str(contextData[key]['push']['g'] + contextData[key]['push']['b'] + contextData[key]['push']['n'])
        #   for link in contextData[key]['link']:
        #       print '-- link:' + link.encode('utf8')
        
        # jsonStr = json.dumps(contextData, indent=4)
        # with open("contextData.json", "w") as f:
        #   f.write(jsonStr)    
        # jsonStr = json.dumps(linkData, indent=4)
        # with open("linkData.json", "w") as f:
        #   f.write(jsonStr)  
        # jsonStr = json.dumps(contextData2, indent=4)
        # with open("contextData2.json", "w") as f:
        #   f.write(jsonStr)            
        
    
        # for key in groupData.keys():
        #   print key 
        #   push = {"all": 0, "b": 0, "g": 0, "n": 0}
        #   for data in groupData[key]['groupList']:
        #       if not contextData2[data] is None:
        #           print '--' + data
        #           print contextData2[data]
        #           if not contextData2[data]['push'] is None:
        #               print contextData2[data]['push']
        #               push['b'] = push['b'] + contextData2[data]['push']['b']
        #               push['g'] = push['g'] + contextData2[data]['push']['g']
        #               push['n'] = push['n'] + contextData2[data]['push']['n']
        #               push['all'] = push['all'] + contextData2[data]['push']['all']
        #   groupData[key]['push'] = push
    
        # #save to file
        # jsonStr = json.dumps(groupData, indent=4)
        # with open("groupData.json", "w") as f:
        #   f.write(jsonStr) 
            
        
        # #save to db
        # #conn=pymongo.Connection('54.251.147.205',27017)
        # conn=pymongo.Connection(db_address,27017)
        # db = conn[boardData['name']]#conn['Gossiping']
    
        # #單一文章
        # for key in contextData2.keys():
        #   findDoc = db.single.find_one({'id': key})
        #   if findDoc is None:
        #       db.single.insert(contextData2[key])
        #   else:
        #       findDoc['push'] = contextData2[key]['push']
        #       db.single.save(findDoc)
    
        # #群組文章
        # for key in groupData.keys():
        #   findDoc = db.group.find_one({'key': key})
        #   if findDoc is None:
        #       groupData[key]['time'] = curTime
        #       db.group.insert(groupData[key])
        #   else:
        #       #data reset
        #       for recId in groupData[key]['groupList']:
        #           if not recId in findDoc['groupList']:
        #               findDoc['groupList'].append(recId)
        #               findDoc['time'] = curTime
    
        #       print findDoc['groupList']
                        
        #       pushData = { 'g': 0, 'b': 0, 'n': 0, 'all': 0 } 
        #       for rec in db.single.find({"id":{"$in":findDoc['groupList']}}):
        #           pushData['g'] += rec['push']['g']
        #           pushData['n'] += rec['push']['n']
        #           pushData['b'] += rec['push']['b']
        #       pushData['all'] = pushData['g'] + pushData['n'] + pushData['b']
        #       findDoc['push'] = pushData
        #       db.group.save(findDoc)  
                
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
        #   f.write(jsonStr) 
        #   '''
    
        # #資料庫資料
        # rankdata = {}
        # rankdata['t'] = list(db.single.find({'time':{"$gte":rangeDay}}, { '_id': 0}) \
        #                 .sort([('push.all', pymongo.DESCENDING)]) \
        #                 .limit(50))   
        # rankdata['g'] = list(db.single.find({'time':{"$gte":rangeDay}}, { '_id': 0}) \
        #                 .sort([('push.g', pymongo.DESCENDING)]) \
        #                 .limit(50))
        # rankdata['b'] = list(db.single.find({'time':{"$gte":rangeDay}}, { '_id': 0}) \
        #                 .sort([('push.b', pymongo.DESCENDING)]) \
        #                 .limit(50))
    
        # rankdata['gt'] = list(db.group.find({'time':{"$gte":rangeDay}}, { '_id': 0}) \
        #                 .sort([('push.all', pymongo.DESCENDING)]) \
        #                 .limit(50))
    
        # for gData in rankdata['gt']:
        #   gData['groupListData'] = list(db.single.find({"id":{"$in":gData['groupList']}}, { '_id': 0}) \
        #                               .sort([('time', pymongo.ASCENDING)]) \
        #                               .limit(50))
    
        # rankdata['gg'] = list(db.group.find({'time':{"$gte":rangeDay}}, { '_id': 0}) \
        #                 .sort([('push.g', pymongo.DESCENDING)]) \
        #                 .limit(50))
        # for gData in rankdata['gg']:
        #   gData['groupListData'] = list(db.single.find({"id":{"$in":gData['groupList']}}, { '_id': 0}) \
        #                               .sort([('time', pymongo.ASCENDING)]) \
        #                               .limit(50))
        # rankdata['gb'] = list(db.group.find({'time':{"$gte":rangeDay}}, { '_id': 0}) \
        #                 .sort([('push.b', pymongo.DESCENDING)]) \
        #                 .limit(50))
        # for gData in rankdata['gb']:
        #   gData['groupListData'] = list(db.single.find({"id":{"$in":gData['groupList']}}, { '_id': 0}) \
        #                               .sort([('time', pymongo.ASCENDING)]) \
        #                               .limit(50))
        # rankdata['time'] = curTime
    
    
        
    
        # jsonStr = json.dumps(rankdata, indent=4)
        # with open("rankdata.json", "w") as f:
        #   f.write(jsonStr)    
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
                    except:     '''
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

def save_board_data_to_db(parser, db, board_name, hour):
    data = parser.board_parse(board_name, hour)
    #data = parser.board_parse('beauty', 12)
    
    #jsonStr = json.dumps(data, indent=4)
    #with open(board_name + "_data.json", "w") as f:
    #   f.write(jsonStr)    

    sort_data = sorted(data, key=lambda data: data['score'], reverse=True)
    db.store_to_db(board_name, sort_data)
        

def test1():
    parser = PttWebParser()
    
    #print(parser.context_parse('https://www.ptt.cc/bbs/C_Chat/M.1520518343.A.07A.html'))

    db = dynamodb_conn.AwsDB('accessKeys_dbm.csv')
    save_board_data_to_db(parser, db, 'Gossiping', 4)
    #save_board_data_to_db(parser, db, 'C_Chat', 4)

    parser.web.close()

def test_parse_board(board_name, hour):
    parser = PttWebParser()
    data = parser.board_parse(board_name, hour)
    parser.web.close()    
    return data

def test_data_to_file(board_name, data):

    jsonStr = json.dumps(data, indent=4)
    with open(board_name + "_data.json", "w") as f:
       f.write(jsonStr) 

def test_file_to_data(board_name):
    with open(board_name + "_data.json", "r") as f:
        file_data = f.read() 
    file_obj = json.loads(file_data)  
    return file_obj
       

def test_db_save(board_name, data):
    db = dynamodb_conn.AwsDB('accessKeys_dbm.csv')
    sort_data = sorted(data, key=lambda data: data['score'], reverse=True)
    db.store_to_db(board_name, sort_data)

def test_db_load(board_name):
    db = dynamodb_conn.AwsDB('accessKeys_dbm.csv')
    db.get_data(board_name)

def test_parse_to_db(board_name, hr):
    data = test_parse_board(board_name, hr)    
    test_db_save(board_name, data)
    test_db_load(board_name)
    
if __name__ == "__main__":
    #data = test_parse_board('Gossiping', 1)
    #test_data_to_file('Gossiping', data)
    #data = test_file_to_data('Gossiping')
    #test_db_save('Gossiping', data)
    #test_db_load('Gossiping')
    
    test_parse_to_db('Gossiping', 4)
    test_parse_to_db('C_Chat', 4)

             
     

                        
        
                
