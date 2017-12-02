#!/usr/bin/env python
# coding=utf-8
import os
import urllib,urllib.request
import hashlib
import socks,socket
import http.client


# 建立文件夹
def mkdirs(path: str):
    path = path.strip()  # 去除首位空格
    path = path.rstrip('\\')  # 去除尾部\符号

    if not os.path.exists(path):  # 判断路径是否存在
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


def set_socks5_proxy():
    socks.set_default_proxy(socks.SOCKS5, '127.0.0.1', 1080)
    socket.socket = socks.socksocket


def download(url, path, use_proxy=False):
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

    if use_proxy:
        set_socks5_proxy()
    urllib.request.urlretrieve(url, path)

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
                listone, listtwo, listthree, listfour, listfive = line.split('\t') # 以制表符分割每一行
                person.append(listone.replace(' ', '_')) # 将人名中间的空格替换成下划线
                imagenumber.append(listtwo)
                url.append(listthree)
                rect.append(listfour)
                md5sum.append(listfive)

    return person, imagenumber, url, rect, md5sum


if __name__ == '__main__':

    # 设置下载照片成功的张数
    pic_numbers = 0
    # 设置下载照片失败的张数
    pic_error = 0
    # 保存无法下载的name:imagenumber:url
    error_image = list()
    # 出错信息
    error_info = list()

    # 获取文件中的信息
    person, imagenumber, url, rect, md5sum = getValue('../urls/dev_urls.txt')

    # 建立人名文件夹，首先对人名去重
    for name in set(person):
        mkdirs('data/' + name)

    for i in range(0, len(url)):
        path = 'data/' + person[i] + '/' + imagenumber[i] + '.jpg'

        # 下载图片
        print(path + ' downloading from ' + url[i])
        try:
            if not os.path.exists(path):
                download(url[i], path, True)
                print(path + '下载成功!\n')
            else:
                print('文件已经被下载！\n')
            # 下载照片张数加一
            pic_numbers = pic_numbers + 1

        #except (urllib.error.HTTPError, urllib.error.URLError, urllib.error.ContentTooShortError, http.client.RemoteDisconnected) as error:
        except BaseException as error:
            # 存储报错信息
            error_info.append(str(error))
            print(str(error))
            # 出错照片加一
            pic_error = pic_error + 1
            # 存储出错照片的信息
            error_image.append(person[i] + ':' + imagenumber[i] + '.jpg:' + url[i])

    # 下载失败结果保存进文件中
    with open('log.txt', 'wt') as log:
        for line in error_image:
            log.write(line)

    # 输出下载结果
    print(str(pic_numbers) + ' pictures download successfully!\n' + \
          str(pic_error)   + ' pictures download failed!\n')