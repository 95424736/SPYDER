from selenium import webdriver
from lxml import etree
from multiprocessing import Queue
from threading import Thread
import csv
import time

#创建类对象
class FeiXiaohaospider(object):
    def __init__(self):
        #初始url
        self.baseurl ="https://www.feixiaohao.com/list_"
        #数据队列
        self.msgQueue = Queue()
        #url队列
        self.urlQueue = Queue()
        #html队列
        self.htmlQueue = Queue()
        #记录请求线程的数量，设定最大量为10
        self.alive = 10
        #记录爬取的数据数量
        self.n = 0

    #储存函数，存入csv文件
    def savemsg(self):
        #创建csv文件，编码gb18030，
        with open('非小号虚拟货币数据.csv','a',newline='',encoding='gb18030') as f:
            writer = csv.writer(f)
            #设置列表表头
            writer.writerow(['币种','流通市值','全球指数','24H成交额','流通数量','24H涨幅'])
            #循环存入数据
            while True:
                #当数据msg队列不为空时，开始存入
                if not self.msgQueue.empty():
                    getmsg = self.msgQueue.get()
                    writer.writerow(getmsg)
                    self.n += 1
                    #记录存入的数据数量
                    print('存入%d条数据' % self.n)
                #当三个队列都为空时候，且get线程不在运行时，数据抓取完毕，退出解析线程
                else:
                    time.sleep(5)
                    if (not self.alive) and self.urlQueue.empty() and self.htmlQueue.empty() and self.msgQueue.empty() :
                        print('存储线程退出')
                        break
    #解析线程，从html队列取出html源码进行解析
    def parseHtml(self):
        while True:
            #当html队列不为空时，开始进行网页解析
            if not self.htmlQueue.empty():
                getHtml = self.htmlQueue.get()
                p = etree.HTML(getHtml)
                baseList = p.xpath('//tr[@class="ivu-table-row"]')
                for base in baseList:
                    L = []
                    L.append(base.xpath('./td/div/a/span/text()')[0]) #币种
                    msg = base.xpath("./td[@class='ivu-table-column-right'][1]//text()")[5]
                    L.append(msg) if msg else L.append(' ')
                    msg = base.xpath("./td[@class='ivu-table-column-right'][2]//text()")[5]
                    L.append(msg) if msg else L.append(' ')
                    msg = base.xpath("./td[@class='ivu-table-column-right'][3]//text()")[5]
                    L.append(msg) if msg else L.append(' ')
                    msg = base.xpath('./td/div/span/span/text()')[0]
                    L.append(msg) if msg else L.append(' ')
                    msg = base.xpath("./td/div/span[contains(@class,'text')]/text()")
                    L.append(msg[0]) if msg else L.append(' ')
                    #将解析后得到的数据存入msg队列
                    self.msgQueue.put(L)
            else:
                time.sleep(5)
                print(self.alive)
                #当url队列和html队列都为空时候，数据解析完毕，退出解析线程
                if self.urlQueue.empty() and (not self.alive) and self.htmlQueue.empty():
                    break

    #请求线程，用于模仿浏览器行为，获得html页面
    def gethtml(self):
        while True:
            if not self.urlQueue.empty():
                # 设置chrome为无头浏览器
                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_argument('--headless')
                driver = webdriver.Chrome(chrome_options=chrome_options)
                geturl = self.urlQueue.get()
                driver.get(geturl)
                html = driver.page_source
                self.htmlQueue.put(html)
            else:
                #当url队列为空时候，无要继续创建的页面，退出线程
                print('请求线程退出')
                break

    #主函数
    def main(self):
        #创建24个url
        for i in range(1,25):
            url = self.baseurl+str(i)+'.html'
            self.urlQueue.put(url)
        #创建储存线程的列表，用于统一回收
        L1 = []
        #分别创建10个请求线程和10个解析线程
        for i in range(10):
            t1 = Thread(target=self.gethtml)
            t1.start()
            L1.append(t1)
        L2 = []
        for i in range(10):
            t2 = Thread(target=self.parseHtml)
            t2.start()
            L2.append(t2)
        #创建一个储存线程
        t3 = Thread(target=self.savemsg)
        t3.start()
        L2.append(t3)
        print('线程创建完毕,开始爬取.......')
        #回收线程
        for i in L1:
            i.join()
            # 请求线程数量减1
            self.alive -= 1
        for i in L2:
            i.join()
        print('爬取完毕，线程关闭')

if __name__ == "__main__":
    bt = time.time()
    myspider = FeiXiaohaospider()
    myspider.main()
    print('爬取完毕，共用时',time.time()-bt,'秒，共爬取数据',myspider.n,'条')





