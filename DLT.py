#!/usr/bin/python
#-*- coding: utf-8 -*-

import os
import time
import urllib2
import bs4
from bs4 import BeautifulSoup

#抓取大乐透
class DLT:
    def __init__(self):
        self.userAgent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        self.headers = {'User-Agent' : self.userAgent}
        self.data = []
    
    def get_content(self, url):
        try:
            request = urllib2.Request(url, headers = self.headers)
            response = urllib2.urlopen(request)
            pageContent = response.read()
            return pageContent
        except urllib2.URLError, e:
            if hasattr(e,"code"):
                print e.code
            if hasattr(e,"reason"):
                print e.reason

    '''
    dump数据到文件ssq.txt
    '''
    def dump(self):
        if len(self.data) > 0:
            print '正在将数据写入文件....'
            f = open('dlt.txt','a')
            data = '\n'.join(self.data)
            f.write(data)
            f.close()
            print '写入完成...\n'
        else:
            print '无数据，不写入文件...\n'
    
    def fetch_data(self, page_html):
        for tr in page_html.tbody.children:
            #print type(tr), tr
            info = [] # 存放单个一期的数据,即存放一行数据
            if isinstance(tr, bs4.element.Tag) == True:
                ball = []
                balls = ''
                td_count = 1
                for td in tr.children:
                    if isinstance(td, bs4.element.Tag) == True and td.string != None:
                        
                        stxt = td.string
                        #print stxt
                        
                        if td_count == 2 or td_count == 3 or td_count == 4 or td_count == 5 or td_count == 7:
                            ball.append(stxt.strip()+',')
                        elif td_count == 6:
                            ball.append(stxt.strip()+'|')
                        elif td_count == 8:
                            ball.append(stxt.strip())
                            balls = ''.join(ball) # 前区号码1, ...|后区号码1,后区号码2
                            info.append(balls)
                        else:
                            info.append(stxt.strip())
                        td_count = td_count + 1
                        
                # print info
                # break
                # info是单个一期的数据，转换成字符串，各项数据之间用制表符(\t)分隔
                # self.data存放一页的数据，多行：['aa bb cc', 'dd ff ee', ...] 
                self.data.append('\t'.join(info))

    def run(self):
        print '正在获取大乐透彩票数据....'
        for page in range(1, 79):
            if page == 1:
                url = 'http://www.lottery.gov.cn/historykj/history.jspx?_ltype=dlt'
            else:
                url = 'http://www.lottery.gov.cn/historykj/history_'+str(page)+'.jspx?_ltype=dlt'
                
            print url
            
            page_html = self.get_content(url)
            soup = BeautifulSoup(page_html, 'html5lib')
            
            self.fetch_data(soup)
            print '采集完成!\n'
            time.sleep(1)
            #break

        self.dump()
        
if __name__ == "__main__":
    e = DLT()
    e.run()
