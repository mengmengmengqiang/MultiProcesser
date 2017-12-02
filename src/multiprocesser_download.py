#!/usr/bin/env python
# coding=utf-8

import concurrent
from concurrent.futures import ThreadPoolExecutor
import os
import urllib, urllib.request
import hashlib
import socks, socket


class ThisThreadPoolExecutor(object):
    def __init__(self, persons: list, imagenumbers: list, urls: list, use_proxy=False):
        self.persons = persons
        self.imagenumbers = imagenumbers
        self.urls = urls
        self._use_proxy = use_proxy

        self.download_error = list()
        self.download_success = list()

    def set_socks5_proxy(self):
        if self._use_proxy:
            socks.set_default_proxy(socks.SOCKS5, '127.0.0.1', 1080)
            socket.socket = socks.socksocket

    def download(self, url: str, path: str):
        """
        通过给定的链接下载文件
        :param url: 链接
        :param path: 带路径的将保存的文件名
        :param use_proxy: 是否使用代理
        :return:
        """

        # 伪装请求头，防止请求被服务器ban掉
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-Agent',
                              'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
        urllib.request.install_opener(opener)

        try:
            person, image = path.split('/')[1:3]
            if not os.path.exists(path):
                urllib.request.urlretrieve(url, path)
                return_string = person + '/' + image +' download from '+ str(url) + ' OK!'
            else:
                return_string = person + '/' + image + ' is already exist.'

            self.download_success.append(person + '\t' + image + '\t' + str(url) + '\n')
            return return_string

        except BaseException as error:
            person, image = path.split('/')[1:3]
            self.download_error.append(person + '\t' + image + '\t' + url + '\t' + str(error) + '\n')
            return person + '/' + image + ' ' + str(error)

    def runner(self):
        # 创建一个线程池
        thread_pool = ThreadPoolExecutor(max_workers=500, thread_name_prefix='DEMO')
        # 创建一个线程任务字典
        futures = dict()
        # 设置代理连接
        self.set_socks5_proxy()

        for i in range(0, len(self.persons)):
            person = self.persons[i]
            imagenumber = self.imagenumbers[i]
            url = self.urls[i]
            path = 'data/' + person + '/' + imagenumber + '.jpg'
            # 以get_url_content方法为句柄注册多个任务并返回任务对象future
            future = thread_pool.submit(self.download, url, path)
            # 将字典里链接的key对应为任务对象
            futures[future] = url

        for future in concurrent.futures.as_completed(futures):
            # 从字典里获取任务对应的下载链接
            _url = futures[future]
            try:
                # 获取任务对象的返回结果
                print(future.result())
            except Exception as error:
                print('Run thread url (' + _url + ') error. ' + str(error))
        print('Finished!')
        return self.download_success, self.download_error


# 建立文件夹
def mkdirs(path: str):
    path = path.strip()  # 去除首位空格
    path = path.rstrip('\\')  # 去除尾部\符号

    if not os.path.exists(path):  # 判断路径是否存在
        try:
            os.mkdir(path)
            print(path + '创建成功!\n')
        except:
            os.mkdir(str(path.split('/')[0]))
            os.mkdir(path)
            print(path + '创建成功!\n')
        return True
    else:
        print(path + '目录已存在!\n')
        return False


# md5校验函数
def compute_md5sum(file_name):
    """
    根据给定文件名计算文件MD5值
    :param file_name: 文件路径
    :return: 返回文件MD5值
    """
    fp = open(file_name, 'rb')
    content = fp.read()
    fp.close()
    m = hashlib.md5(content)
    file_md5 = m.hexdigest

    return file_md5


# 从文本文件中获取信息并保存到数组中
def getValue(file_name):
    count = 0
    person = list()
    imagenumber = list()
    url = list()
    rect = list()
    md5sum = list()
    with open(file_name, 'rt') as file:
        for line in file:
            if line[0] != '#':
                listone, listtwo, listthree, listfour, listfive = line.split('\t')  # 以制表符分割每一行
                person.append(listone.replace(' ', '_'))  # 将人名中间的空格替换成下划线
                imagenumber.append(listtwo)
                url.append(listthree)
                rect.append(listfour)
                md5sum.append(listfive)

    return person, imagenumber, url, rect, md5sum


if __name__ == '__main__':

    # 获取文件中的信息
    persons, imagenumbers, urls, rects, md5sums = getValue('../urls/dev_urls.txt')
    for name in set(persons):
        mkdirs('data/' + name)

    success, error = ThisThreadPoolExecutor(persons, imagenumbers, urls, True).runner()

    with open('error.txt', 'wt') as log:
        for line in error:
            log.write(line)
    with open('success.txt', 'wt') as log:
        for line in success:
            log.write(line)