import requests
from lxml import etree
import threading
from queue import Queue

class QiubaiSpider:
    def __init__(self):
        self.temp_url = "https://www.qiushibaike.com/text/page/{}/"
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'}
        self.url_list = Queue()
        self.html_list = Queue()
        self.content_list = Queue()

    def get_url_list(self):
        while True:
            for i in range(1,10):
                url = self.temp_url.format(i)
                self.url_list.put(url)

    def parse_url(self):
        while True:
            url = self.url_list.get()
            response = requests.get(url=url,headers=self.headers)
            print(response)
            self.html_list.put(response.content.decode())
            self.url_list.task_done()

    def get_content_list(self):
        while True:
            html_str = self.html_list.get()
            html = etree.HTML(html_str)
            div_list = html.xpath('//*[@id="content-left"]/div')
            content_list = []
            for div in div_list:
                item = {}
                item['author_name'] = div.xpath('.//div/a[2]/h2/text()')
                item['author_name'] = [i.replace('\n','') for i in item['author_name']]
                item['author_name'] = item['author_name'] if len(item['author_name'])>0 else None
                item['artical'] = div.xpath('.//a/div/span[1]/text()')
                item['artical'] = [i.replace('\n', '') for i in item['artical']]
                item['artical'] = item['artical'] if len(item['artical'])>0 else None
                # print(content_list)
                content_list.append(item)
                self.content_list.put(content_list)
            self.html_list.task_done()



    def save_data(self):
        while True:
            content_list = self.content_list.get()
            for i in content_list:
                print(i)
                with open('./qiubai.txt','a',encoding='utf-8') as f:
                    f.write(str(i))
                    f.write('\n')
            self.content_list.task_done()
            # print('保存成功')

    def run(self):
        thread_list = []
        # 构建url
        thread1 = threading.Thread(target=self.get_url_list)
        thrrad = thread_list.append(thread1)
        # 发送请求
        thread2 = threading.Thread(target=self.parse_url)
        thrrad = thread_list.append(thread2)
        # 提取数据
        for i in range(10):
            thread3 = threading.Thread(target=self.get_content_list)
            thrrad = thread_list.append(thread3)
        # 保存内容
        thread4 = threading.Thread(target=self.save_data)
        thrrad = thread_list.append(thread4)

        for i in thread_list:
            i.setDaemon(True)
            i.start()

        for q in [self.url_list,self.html_list,self.content_list]:
            q.join()

if __name__ == '__main__':
    qiubaispider = QiubaiSpider()
    qiubaispider.run()