# -*- coding: utf-8 -*- 
# @Time : 2022/3/22 18:53 
# @Author : junjie
# @File : config.py

class Config(object):
    dubbo_connect_timeout = 3
    zookeeper_url_list = ['192.168.240.15:2181', '192.168.240.15:2182', '192.168.240.15:2183']
    zookeeper_connect_timeout = 3
    zookeeper_wait_timeout = 3
    prompt = 'dubbo>'