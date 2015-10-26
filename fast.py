#__author__ = 'croxy'
# -*- coding: UTF-8 -*-
#!/usr/bin/python

import requests
import optparse
import sys
import threading
import time
import Queue
import re
import urlparse

header = {
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
'Accept-Encoding': 'gzip, deflate, compress',
'Cache-Control': 'max-age=0',
'Connection': 'keep-alive',
"Accept-Language": "zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3",
"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:35.0) Gecko/20100101 Firefox/35.0"
}

class DirScan:
    def __init__(self, target, threads_num, ext):
        self.target = target.strip()
        self.threads_num = threads_num
        self.ext = ext
        self.lock = threading.Lock()
        #outfile
        self.__load_dir_dict()
        self.errorpage = r'信息提示|参数错误|no exists|User home page for|可疑输入拦截|D盾|安全狗|无法加载模块|[nN]ot [fF]ound|不存在|未找到|Error|Welcome to nginx!|404|'
        self.regex = re.compile(self.errorpage)

    def __load_dir_dict(self):
        self.queue = Queue.Queue()
        ext = self.ext
        target = self.target
        hostuser = target.split('.')
        hostuser = hostuser[len(hostuser)-2]
        bak =  ['/'+hostuser+'.rar','/'+hostuser+'.zip','/'+hostuser+hostuser+'.rar','/'+hostuser+'.rar','/'+hostuser+'.tar.gz','/'+hostuser+'.tar','/'+hostuser+'123.zip','/'+hostuser+'123.tar.gz','/'+hostuser+hostuser+'.zip','/'+hostuser+hostuser+'.tar.gz','/'+hostuser+hostuser+'.tar','/'+hostuser+'.bak']
        with open('dir.txt') as f:
            for line in f:
                mulu = line.replace('$ext$',ext).strip()
                if mulu:
                    self.queue.put(mulu)

    def _scan(self):
        #print errtext
        while True:
            if self.queue.empty():
                break
            try:
                sub = self.queue.get_nowait()
        #try:
                #print sub
                domain = self.target + sub
                #print domain
                r = requests.head(domain, headers = header, timeout=5, stream=True)
                code = r.status_code
                if code == 200:
                    print "[*] %s =======> 200 \n" %domain,
                elif code == 403:
                    print "[*] %s =======> 403 \n" %domain,

            except Exception,e:
                pass

    def run(self):
        self.start_time = time.time()
        for i in range(self.threads_num):
            t = threading.Thread(target=self._scan, name=str(i))
            t.start()

def patch_url(url):
    """ 修复不标准URL """
    res = urlparse.urlparse(url)
    if not res.scheme:
        url = 'http://' + url

    return url

if __name__ == '__main__':
    parser = optparse.OptionParser('usage: %prog [options] http://www.c-chicken.cc')
    parser.add_option('-t', '--threads', dest='threads_num',
              default=10, type='int',
              help='Number of threads. default = 10')
    parser.add_option('-e', '--ext', dest='ext', default='php',
               type='string', help='You want to Scan WebScript. default is php')
   # parser.add_option('-o', '--output', dest='output', default=None,
   #          type='string', help='Output file name. default is {target}.txt')

    (options, args) = parser.parse_args()
    if len(args) < 1:
        parser.print_help()
        sys.exit(0)
    url = patch_url(args[0])
    d = DirScan(target=url,threads_num=options.threads_num,ext=options.ext)
    d.run()