# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 18:23:23 2019

@author: Python
"""

import urllib.request
import urllib.parse

class BaiduSpider(object):
    def __init__(self):
        self.baseurl='http://tieba.baidu.com/f?'
        self.headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0'}
        
    #获取页面
    def getPage(self,url):
        req = urllib.request.Request(url, headers=self.headers)
        res = urllib.request.urlopen(req)
        html = res.read().decode('utf-8')
        return html
        
    def writePage(self,filename,html):
        with open(filename,'w',encoding='utf-8') as f:
            f.write(html)
    
    def workOn(self):
        name = input('请输入贴吧名称：')
        begin = int(input('请输入起始页：'))
        end = int(input('请输入终止页:'))
        #拼接贴吧主页的url地址
        kw = urllib.parse.urlencode({'kw':name})
        for page in range(begin, end+1):
            pn = (page - 1)*50
            url = self.baseurl + kw+ '&pn=' + str(pn)
            html = self.getPage(url)   
            filename = '第'+str(page)+'页.html'
            self.writePage(filename,html)
            print('第%d页爬取成功'%page)

    
    

if __name__ == '__main__':
    spider = BaiduSpider()
    spider.workOn()