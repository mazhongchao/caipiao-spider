#!/usr/bin/python
#-*- coding: utf-8 -*-

import os
import time
import datetime
import urllib2
import logging
import bs4
from bs4 import BeautifulSoup

# 抓取双色球, 处理最新几期的数据, 并写入到文件最前面
class SSQ_New:
    def __init__(self):
        self.userAgent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        self.headers = {'User-Agent' : self.userAgent}
        self.data = []
        self.this_max_no = ''
        self.logger = logging.getLogger('ssq')
        self.log_formatter = logging.Formatter('%(asctime)s %(levelname)-8s:  %(message)s')
        self.log_file = logging.FileHandler('ssq.log')
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
        local_no = '3000000'
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
                lines.append(line.strip('\n'))
            fp.close()
            
            lines = self.data + lines
            data = '\n'.join(lines)
            
            fp = open('ssq_' + y + '.txt','w')
            fp.write(data)
            fp.close()

            print '写入完成....\n'
            self.logger.info('写入完成....')
        else:
            print '无数据，不写入文件...\n'
            self.logger.info('无数据，不写入文件...')
    
    def fetch_data(self, page_html):
        local_no = self.find_local_no()
        max_no = local_no
        page_data = []
        
        row = 0
        trs = page_html.find_all('tr')

        for one_tr in trs:
            info = []
            row = row + 1
            if row == 1 or row == 2 or row == 23: #忽略表头表尾
                continue
            
            tdc = 1
            tds = one_tr.find_all('td')

            for td in tds:
                if tdc > 4: # 只取日期、期数、开奖号、销售额4项数据
                    break
                if td.string != None:
                    # print td.string
                    stxt = td.string
                    info.append(stxt.strip())
                    
                    if tdc == 2:
                        if int(local_no) < int(stxt):
                            print '处理第', stxt, '期数据...'
                            self.logger.info('处理第'+str(stxt)+'期数据')
                            if int(stxt) > int(max_no):
                                max_no = stxt
                        else:
                            print '没有新数据了'
                            self.logger.info('没有新数据了')
                            self.this_max_no = max_no
                            return
                else:
                    if tdc == 3: # 处理中奖号码
                        ems = td.find_all('em')
                        em_order = 1
                        ball = []
                        balls = ''
                        for em in ems:
                            btxt = em.string   # 开奖号码
                            if em_order == 7:
                                ball.append('|' + btxt.strip())
                            elif em_order == 6:
                                ball.append(btxt.strip())
                            else:
                                ball.append(btxt.strip() + ',')
                            em_order = em_order + 1
                        balls = ''.join(ball) # 红球,...|蓝球
                        info.append(balls)
                tdc = tdc + 1
            
            # 循环完所有td, 完成一期数据获取
            # info是单个一期的数据:[u'2017-07-06', u'2017078', u'05,07,18,19,22,24|16', u'308,678,006']
            # 将以上列表中的元素转换成字符串,每期的各项数据之间用制表符(\t)分隔, 并添加到self.data中, self.data是字符串列表
            if len(info) > 0:
                self.data.append('\t'.join(info))

    def run(self):
        url = 'http://kaijiang.zhcw.com/zhcw/html/ssq/list_1.html'
        print '正在获取双色球彩票数据....'
        print url
        
        self.logger.info('正在获取双色球最新数据...')
        self.logger.info(url)
        
        page_html = self.get_content(url)
        soup = BeautifulSoup(page_html, 'html5lib')
        
        self.fetch_data(soup)
        print '采集完成!'
        self.logger.info('采集完成')

        self.dump()
        self.mark_down_no(self.this_max_no)

if __name__ == "__main__":
    e = SSQ_New()
    e.run()
