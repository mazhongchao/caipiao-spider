#!/usr/bin/python
#-*- coding: utf-8 -*-

import os
import time
import datetime
import logging
import urllib2
import bs4
from bs4 import BeautifulSoup

# 抓取大乐透, 处理最新几期的数据, 并写入到文件最前面
class DLT_New:
    def __init__(self):
        self.userAgent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        self.headers = {'User-Agent' : self.userAgent}
        self.data = []
        self.this_max_no = ''
        self.logger = logging.getLogger('dlt')
        self.log_formatter = logging.Formatter('%(asctime)s %(levelname)-8s:  %(message)s')
        self.log_file = logging.FileHandler('dlt.log')
        self.log_file.setFormatter(self.log_formatter)
        self.logger.addHandler(self.log_file)
        self.logger.setLevel(logging.INFO)
    
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
            self.logger.info('REQUEST Fail: '+e.code+','+e.reason)

    def find_local_no(self):
        local_no = '30000'
        if os.path.isfile('dlt_max.txt'):
            fp = open('dlt_max.txt', 'r')
            local_no = fp.read()

        return local_no

    def mark_down_no(self, num):
        if os.path.isfile('dlt_max.txt'):
            fp = open('dlt_max.txt', 'w')
            fp.write(num)
            fp.close()

    '''
    dump数据到文件ssq_YYYY.txt
    '''
    def dump(self):
        if len(self.data) > 0:
             # print '正在将数据写入文件....'

            y = datetime.date.today().strftime('%Y')
            if os.path.isfile('dlt_' + y + '.txt') != True:
                open('dlt_' + y + '.txt', 'w+').close()

            fp = open('dlt_' + y + '.txt','r')
            lines = []
            for line in fp:
                lines.append(line)
            fp.close()
            
            lines = self.data + lines
            data = '\n'.join(lines)
            
            fp = open('dlt_' + y + '.txt','w')
            fp.write(data)
            fp.close()
            print '写入完成...\n'
            self.logger.info('写入完成....')
        else:
            print '无数据，不写入文件...\n'
            self.logger.info('无数据，不写入文件...')
    
    def fetch_data(self, page_html):
        local_no = self.find_local_no()
        max_no = local_no
        
        
        for tr in page_html.tbody.children:
            info = [] # 存放单个一期的数据
            if isinstance(tr, bs4.element.Tag) == True:
                ball = []
                balls = ''
                td_order = 1
                for td in tr.children:                          
                    if isinstance(td, bs4.element.Tag) == True and td.string != None:
                        stxt = td.string

                        if td_order == 1:
                            if int(local_no) < int(stxt):
                                print '处理第', stxt, '期数据...'
                                self.logger.info('处理第'+str(stxt)+'期数据')
                                if int(stxt) > int(max_no):
                                    max_no = stxt # 记下这批处理数据中最大的，即所处理行(tr)中第一个的期数，因为每页期数最大的一期数据排在最前
                            else:
                                print '没有新数据了'
                                self.logger.info('没有新数据了')
                                self.this_max_no = max_no
                                return
                            info.append(stxt.strip())
                        elif td_order == 2 or td_order == 3 or td_order == 4 or td_order == 5 or td_order == 7:
                            ball.append(stxt.strip()+',')
                        elif td_order == 6:
                            ball.append(stxt.strip()+'|')
                        elif td_order == 8:
                            ball.append(stxt.strip())
                            balls = ''.join(ball) # 前区号码1, ...|后区号码1,后区号码2
                            info.append(balls)
                        else:
                            info.append(stxt.strip())
                        td_order = td_order + 1
                        
                # info是单个一期的数据，转换成字符串，各项数据之间用制表符(\t)分隔
                # self.data ['aa bb  cc', 'dd, ee, ff', ...]
                if len(info) > 0:
                    self.data.append('\t'.join(info))

    def run(self):
        url = 'http://www.lottery.gov.cn/historykj/history.jspx?_ltype=dlt'
        print '正在获取大乐透彩票数据....'
        print url
        
        self.logger.info('正在获取大乐透最新数据...')
        self.logger.info(url)

        page_html = self.get_content(url)
        soup = BeautifulSoup(page_html, 'html5lib')
        
        self.fetch_data(soup)
        print '采集完成!'
        self.logger.info('采集完成')

        self.dump()
        self.mark_down_no(self.this_max_no)
        
if __name__ == "__main__":
    e = DLT_New()
    e.run()
