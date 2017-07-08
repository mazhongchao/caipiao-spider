#!/usr/bin/python
#-*- coding: utf-8 -*-

import os
import time
import urllib2
import bs4
from bs4 import BeautifulSoup

#抓取双色球
class SSQ:
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
            f = open('ssq.txt','a')
            data = '\n'.join(self.data)
            f.write(data)
            f.close()
            print '写入完成....\n'
        else:
            print '无数据，不写入文件...\n'
    
    def fetch_data(self, page_html):
        i = 0
        page_data = []
        for tr in page_html.tbody.children:
            #print type(tr), tr
            info = []
            if isinstance(tr, bs4.element.Tag) == True:
                n = 1
                for td in tr.children:
                    if isinstance(td, bs4.element.Tag) == True:                            
                        if n > 4: #只取日期、期数、开奖号、销售额4项数据
                            break
                        else:
                            if isinstance(td, bs4.element.Tag) == True and td.string != None:
                                stxt = td.string   #处理日期、期数、销售额
                                info.append(stxt.strip())
                            else:
                                ball = []
                                balls = ''
                                c = 1
                                for em in td.children: # 处理开奖号码
                                    if isinstance(em, bs4.element.Tag) == True and  em.string != None:
                                        #print type(em), em.name, '--',em.string,'--',  em.string.strip(),'--'
                                        btxt = em.string   # 开奖号码
                                        if c == 7:
                                            ball.append('|'+btxt.strip())
                                        elif c == 6:
                                            ball.append(btxt.strip())
                                        else:
                                            ball.append(btxt.strip()+',')
                                        c = c + 1
                                balls = ''.join(ball) #红球,...|蓝球
                                info.append(balls)
                        n = n + 1
                # print info
                # 循环完所有td, 完成一期数据获取
                # info是单个一期的数据:[u'2017-07-06', u'2017078', u'05,07,18,19,22,24|16', u'308,678,006']
                # 转换成字符串，各项数据之间用制表符(\t)分隔
                # page_data是一页的多期数据：[u'2017-05-21\t2017058\t01,09,13,22,28,32|11\t338,794,650', u'2017-05-18\t2017057\ ..]
                page_data.append('\t'.join(info))
        
        page_data = page_data[2:len(page_data)-1]# 去掉表头、表尾 
        #print page_data
        
        for e in page_data:
            self.data.append(e)
        #print self.data
        
    def run(self):
        print '正在获取双色球彩票数据....'
        for page in range(1, 108):
            url = 'http://kaijiang.zhcw.com/zhcw/html/ssq/list_'+str(page)+'.html'
            print url
            
            page_html = self.get_content(url)
            soup = BeautifulSoup(page_html, 'html5lib')
            
            self.fetch_data(soup)
            print '采集完成!\n'
            #print self.data
            #break
            time.sleep(1)

        self.dump()

if __name__ == "__main__":
    e = SSQ()
    e.run()
