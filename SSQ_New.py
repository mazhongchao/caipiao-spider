#!/usr/bin/python
#-*- coding: utf-8 -*-

import os
import time
import urllib2
import bs4
from bs4 import BeautifulSoup

#抓取双色球, 处理最新几期的数据, 并写入到文件最前面
class SSQ_New:
    def __init__(self):
        self.userAgent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        self.headers = {'User-Agent' : self.userAgent}
        self.data = []
        self.this_max_no = ''
    
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

    def find_local_no(self):
        local_no = 3000000
        if os.path.isfile('ssq_max.txt'):
            fp = open('ssq_max.txt', 'r')
            local_no = fp.read()

        return local_no

    def mark_down_no(self, num):
        if os.path.isfile('ssq_max.txt'):
            fp = open('ssq_max.txt', 'w')
            fp.write(num)
            fp.close()

    '''
    dump数据到文件ssq_YYYY.txt
    '''
    def dump(self):
        if len(self.data) > 0:
            y = datetime.date.today().strftime('%Y')
            
            if os.path.isfile('ssq_' + y + '.txt') != True:
                open('ssq_' + y + '.txt', 'w+').close()
            
            fp = open('ssq_' + y + '.txt','r')
            lines = []
            for line in fp:
                lines.append(line)
            fp.close()
            
            lines = lines + self.data
            data = '\n'.join(lines)
            
            fp = open('ssq_' + y + '.txt','w')
            fp.write(data)
            fp.close()

            print '写入完成....\n'
        else:
            print '无数据，不写入文件...\n'
    
    def fetch_data(self, page_html):
        local_no = self.find_local_no()
        max_no = local_no
        page_data = []
        
        row = 1
        for tr in page_html.tbody.children:
            #print type(tr), tr
            info = [] # 存放单个一期的数据
            if isinstance(tr, bs4.element.Tag) == True:
                td_count = 1
                for td in tr.children:
                    if isinstance(td, bs4.element.Tag) == True:                            
                        if td_count > 4: # 只取日期、期数、开奖号、销售额4项数据
                            break
                        else:
                            if isinstance(td, bs4.element.Tag) == True and td.string != None:
                                stxt = td.string   # 处理日期、期数、销售额
                                if row == 1 or row == 2: # 忽略表头两行
                                    pass
                                else:
                                    if td_count == 2:
                                        #print local_no, stxt
                                        if int(local_no) < int(stxt):
                                            if int(stxt) > int(max_no):
                                                max_no = stxt
                                        else:
                                            print '没有新数据了\n'
                                            self.this_max_no = max_no
                                            #self.mark_down_no(max_no)
                                            return
                                info.append(stxt.strip())
                            else:
                                ball = []
                                balls = ''
                                em_order = 1
                                for em in td.children: # 处理中奖号码
                                    if isinstance(em, bs4.element.Tag) == True and  em.string != None:
                                        #print type(em), em.name, '--',em.string,'--',  em.string.strip(),'--'
                                        btxt = em.string   # 开奖号码
                                        if em_order == 7:
                                            ball.append('|'+btxt.strip())
                                        elif em_order == 6:
                                            ball.append(btxt.strip())
                                        else:
                                            ball.append(btxt.strip()+',')
                                        em_order = em_order + 1
                                balls = ''.join(ball) #红球,...|蓝球
                                info.append(balls)
                        td_count = td_count + 1
                row = row + 1
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
        url = 'http://kaijiang.zhcw.com/zhcw/html/ssq/list_1.html'
        print url
        
        page_html = self.get_content(url)
        soup = BeautifulSoup(page_html, 'html5lib')
        
        self.fetch_data(soup)
        print '采集完成!\n'

        self.dump()
        self.mark_down_no(self.this_max_no)

if __name__ == "__main__":
    e = SSQ_New()
    e.run()
