import requests
from lxml import etree
from multiprocessing import Queue
from threading import Thread
import csv
import random
import time
#创建user-agent列表
USERAGENT = ['Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60 ',
    'Opera/8.0 (Windows NT 5.1; U; en)',
    'Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50 ',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 9.50',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0 ',
    'Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2 ',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36 ',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11 ',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36 ',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0 ',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.3.4000 Chrome/30.0.1599.101 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 UBrowser/4.0.3214.0 Safari/537.36']
#随机生成headers信息的user-agent
headers = {"User-Agent":random.choice(USERAGENT)}

#创建class类
class lianjiaSpider(object):
    #初始化
    def __init__(self):
        #基础url
        self.baseurl = "https://hz.lianjia.com/ershoufang/"
        #价格区间列表，p1-p6代表二手房不同的价格区间，用作拼接url
        self.priceList = ['p1','p2','p2','p4','p5','p6']
        #创建url队列，html源码队列、二手房信息队列
        self.urlQueue = Queue()
        self.htmlQueue = Queue()
        self.msgQueue = Queue()
        #获取数据的数量
        self.n = 0

    #储存函数，将二手房信息存入csv表
    def saveMsg(self):
        time.sleep(2)
        with open('链家二手房价格信息表.csv', 'a', newline='', encoding='gb18030') as f:
            writer = csv.writer(f)
            while True:
                #当msgQueue队列不为空时，开始存入信息
                if not self.msgQueue.empty():
                    #阻塞2S，若未从队列中获取信息，则线程退出
                    try:
                        getmsg = self.msgQueue.get(timeout=2)
                        writer.writerow(getmsg)
                        self.n += 1
                    except:
                        break
                #当msgQueue队列持续5秒仍旧为空，则线程退出
                else:
                    time.sleep(5)
                    if self.msgQueue.empty():
                        break
    #解析函数，解析得到的html页面
    def parseHtml(self):
        while True:
            # 当htmlQueue队列不为空时，开始存入信息
            if not self.htmlQueue.empty():
                # 阻塞2S，若未从队列中获取信息，则线程退出
                try:
                    gethtml = self.htmlQueue.get(timeout=1)
                    p = etree.HTML(gethtml)
                    p = p.xpath("//li[@class='clear LOGCLICKDATA']")
                    #当页面匹配的信息不为空时，进行页面进一步解析
                    if p:
                        for i in p:
                            #二手房地址信息
                            msg = i.xpath(".//div/div[@class='address']/div//text()")
                            #二手房价格信息
                            price = i.xpath(".//div/div[@class='priceInfo']/div//text()")
                            #二手房其他信息
                            other = i.xpath(".//div/div[@class='followInfo']//text()")
                            L = [''.join(price[0:2]), price[2], msg[1], msg[0], other[0]]
                            #将二手房信息以列表形式存入msgQueue队列
                            self.msgQueue.put(L)
                except:
                    print('**************有一个parsehtml线程退出*******************')
                    break
            # 当htmlQueue队列持续5秒仍旧为空，判断为没有新的html加入，线程退出
            else:
                time.sleep(5)
                if self.htmlQueue.empty():
                    break
    #获取页面函数，用于获取页面的源码
    def getHtml(self):
        while True:
            #urlQueue队列不为空时进行页面获取，为空时退出线程
            if not self.urlQueue.empty():
                #开始获取页面
                try:
                    geturl = self.urlQueue.get(timeout=0.5)
                    p = requests.get(geturl,headers=headers)
                    p.encoding = 'utf-8'
                    html = p.text
                    #将页面html信息存入htmlQueue队列
                    self.htmlQueue.put(html)
                except:
                    break
            else:
                break

    #主函数，开始执行程序
    def main(self):

        for price in self.priceList:
            for i in range(101):
                url = self.baseurl + 'pg' + str(i) + price
                self.urlQueue.put(url)
        print('*****url存储完毕******')
        tList = []
        for i in range(15):
            t1 = Thread(target=self.getHtml)
            t2 = Thread(target=self.parseHtml)
            tList.append(t1)
            tList.append(t2)
            t1.start()
            t2.start()
        t3 = Thread(target=self.saveMsg)
        t3.start()
        tList.append(t3)
        print('******线程创建完毕*******')
        print('抓取中..........')
        for i in tList:
            i.join()
        print('******线程回收完毕*******')



if __name__ == "__main__":
    a = time.time()
    mySpider = lianjiaSpider()
    mySpider.main()
    print('抓取完毕，用时:',time.time()-a,'秒，',' 爬取信息',mySpider.n,'条')

