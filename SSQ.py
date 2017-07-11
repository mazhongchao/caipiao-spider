#!/usr/bin/python
#-*- coding: utf-8 -*-

import os
import time
import urllib2
import bs4
from bs4 import BeautifulSoup

# 抓取双色球
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
                    print td.string
                    stxt = td.string
                    info.append(stxt.strip())
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
