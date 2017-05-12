import re
import os
import sys
import threading
from urllib import request
path = os.path.join(os.path.dirname(__file__),'requests')
sys.path.append(path)

'''
Name: This is film torrnet spider
Python: 3.5.2
'''

__author__ = 'demon'

class UpdateBtTorrent(object):

    def __init__(self,url = 'http://www.btbtt.co/forum-index-fid-951-page-1.htm'):      #构造函数，用于初始化正则以及headers等
        self.domain = 'http://www.btbtt.co/'
        self.page_regex = re.compile(r'<a href="(\bthread-index-fid.*htm{1}).*">')
        self.bt_regex = re.compile(r'<a href="(\battach-dialog-fid.*htm{1}).*">')
        self.film_name_regex = re.compile(r'"(\[BT下载\].*?)"')
        self.torrent_name_regex = re.compile(r'<a .*>(.*\.torrent{1})</a>')
        self.url,self.page_ursl,self.bt_urls,self.bt_download_urls = url,[],[],[]
        self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3026.3 Safari/537.36'}

    def __request_content(self,url):                        #请求网页返回html的源码
        req = request.Request(url=url,headers=self.headers)
        content = request.urlopen(req).read().decode()
        return content

    def get_page_urls(self):                                #得到电影下载页面入口中的所有电影介绍的链接
        content = self.__request_content(self.url)
        self.page_ursl = [self.domain+url for url in re.findall(self.page_regex,content)]
        return list(set(self.page_ursl))

    def get_bt_urls(self,url):                             #存放bt种子的方法，用于更新显示bt种子
        content = self.__request_content(url)
        bt_url = re.findall(self.bt_regex,content)         #查找bt种子的url
        if bt_url:
            try:
                film_name = re.findall(self.film_name_regex, content)[0].strip()            #获取页面中的电影名称
            except Exception as e:
                pass
            else:
                torrent = re.sub('dialog','download',self.domain+''.join(bt_url))         #得到bt种子的下载地址
                torrent_name = re.findall(self.torrent_name_regex,content)[0].strip()       #得到bt种子的名称
                print('电影名称:'.rjust(8),film_name)
                print('BT种子下载:'.rjust(8),torrent)
                print('BT种子名称:'.rjust(8),torrent_name)
                print('BT详细链接:'.rjust(8),url)
                print()

                with open('Torrent.txt', 'a+', encoding='utf-8') as f:                  #保存bt种子到文本文件中
                    f.write('%s<--->%s<--->%s' % (film_name,torrent,torrent_name) + '\n')
                    f.flush()

class BtTorrent(object):                                          #用于查找下载bt种子的方法

    def __init__(self):
        self.search_film_result = []                              #用于存放所有film的列表
        self.header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3026.3 Safari/537.36'}

    def search(self,search_film):                                 #用于搜索种子的方法
        with open('Torrent.txt','r',encoding='utf-8') as f:
            content = list(set(f.readlines()))
            for line in content:
                if re.findall(r'.*%s+.*?'%search_film,line):     #正则过滤要查找的电影名称
                    self.search_film_result.append(line)
                    print('电影名称:'.rjust(8),line.split('<--->')[0])
                    print('种子地址:'.rjust(8),line.split('<--->')[1])
                    print('种子名称:'.rjust(8),line.split('<--->')[2])

        return self.search_film_result

    def download(self,search):                                      #用于下载电影BT种子的方法
        with open('Torrent.txt','r',encoding='utf-8') as f:      #取出bt文件中的信息
            content = f.readlines()

        for line in content:                                        #获取要查找的内容
            if search in line:
                torrent_url  = line.split('<--->')[1].strip()
                torrent_name = line.split('<--->')[2].strip()

        data = requests.get(torrent_url,stream=True,headers=self.header)
        if data.ok:                                                 #下载bt种子
            print('正在准备下载电影BT种子，稍等一会我的哥~~~')
            with open(torrent_name,'wb+') as f:
                f.write(data.content)
            print('\033[32m%s电影种子下载完毕..~~~~\033[0m'%torrent_name)
        else:
            print('\033[31mWTF，请求头挂了...~~~\033[0m')


class ChoiceCommand(object):                                        #通过sys.argv传递进来的command调用不同的类方法，update,search,download...

    def __init__(self,command):
        self.film_page_urls = []
        self.command = command                                      #获取位置参数，update or search or download...

    def update(self,start_page=1,end_page=5):
        #url = 'http://www.btbtt.co/forum-index-fid-1183-page-%s.htm'
        url = 'http://www.btbtt.co/forum-index-fid-951-page-%s.htm'
        print('\033[32m正在初始化BT爬虫...,更新等待ing.\033[0m')
        for page_num in range(start_page,end_page):                 #支持多页更新
            self.update_tonnert = UpdateBtTorrent(url%page_num)
            film_urls = self.update_tonnert.get_page_urls()
            self.film_page_urls.extend(film_urls)                   #把每一页的电影的url都放到总的urls列表中

        while self.film_page_urls:                                  #因为bt之家有限制，不能同时开启超过10个并发，所以每次限制启动10个线程进行更新
            thread = []
            for film in self.film_page_urls[:10]:
                t = threading.Thread(target=self.update_tonnert.get_bt_urls,args=(film,))   #更新bt种子的信息
                t.start()
                thread.append(t)
            for th in thread:
                th.join()
            self.film_page_urls = self.film_page_urls[10:]          #每次启动是个线程，利用列表的切片
        else:
            print('\033[32m请求更新的BT种子信息完毕~\033[0m')
            sys.exit(0)

    def search(self,film_name):                                    #实例化搜索种子的方法
        bt_torrnet = BtTorrent()
        bt_torrnet.search(film_name)

    def download(self,film_name):                                  #实例化下载种子的方法
        bt_torrnet = BtTorrent()
        bt_torrnet.download(film_name)

if __name__ == '__main__':

    if len(sys.argv) >= 3:                                         #判断传递的参数个数
        command = sys.argv[1]
        choice = ChoiceCommand(command)
        if hasattr(choice, command):                               #利用反射调取不同的类方法
            if command == 'update':
                update = getattr(choice, command)
                start_page = int(sys.argv[2])
                end_page = int(sys.argv[3])
                update(start_page, end_page)
            else:
                if os.path.exists(os.path.join(os.path.dirname(__file__),'Torrent.txt')):       #判断Torrent.txt，如果有说明有本地的bt种子库
                    bt = getattr(choice, command)                   #通过反射找到search或者download的方法
                    film_name = sys.argv[2]
                    bt(film_name)                                   #调用对应的方法
                else:
                    print('木有找到本地的BT种子库.\033[32m准备更新本地的种子库\033[0m ,特么的给老子消停的等一会.')
                    choice.update()

    elif len(sys.argv) == 2 and sys.argv[1] == 'update':           #不加起始页和终止页，默认更新五页
        choice = ChoiceCommand('update')
        choice.update()

    else:
        print(
    '''
    Low B小哥哥：
        \033[31mLow B哥呀\033[0m,不是这样玩的呀.
    名称:
        这特么的是一个爬取小电影的bt种子
    简介:
        <\033[32mupdate\033[0m [更新电影的初始页,更新电影的终止页]> <\033[32msearch\033[0m电影名称> <\033[32mdownload\033[0m电影名称或者BT下载的地址>
    描述:
        search: 　查找的电影名称
        update: 　更新本地BT电影库，可以加上起始、终止的页数，默认为前五页
        download: 下载的电影名称或者BT种子的URL地址，默认下载查找到的第一条电影匹配
    示例：
        update  　起始更新页　终止更新页
        search　　电影名称
        download　电影名称
    作者:
        Film Torrent Spider by Demon.
    ''')
