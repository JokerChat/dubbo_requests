# -*- coding: utf-8 -*- 
# @Time : 2022/3/22 19:05 
# @Author : junjie
# @File : util.py

import telnetlib
import json
import re
from kazoo.client import KazooClient
from urllib import parse
from .config import Config

def param_type_mapping(param_type, value):
    """
    Java类型转换python类型
    :param param_type: Java类型
    :param value: 实际入参值
    :return:
    """
    enum_type = ['int', 'double', 'short', 'float', 'long', 'byte', 'boolean', 'java.util.Date',
                 'char', 'java.lang.String', 'String', 'string', 'java.lang.Integer',
                 'Integer', 'integer', 'java.lang.Double', 'Double', 'java.lang.Short',
                 'Short','java.lang.Long', 'Long', 'java.lang.Float', 'Float', 'java.lang.Byte',
                 'Byte', 'java.lang.Boolean', 'Boolean' ]
    list_type = ['int[]', 'double[]', 'short[]', 'float[]', 'long[]', 'byte[]', 'boolean[]',
                 'char[]', 'java.lang.String[]', 'String[]', 'string[]', 'java.lang.Integer[]', 'Integer[]', 'integer[]',
                 'java.lang.Double[]','Double[]', 'java.lang.Short[]', 'Short[]', 'java.lang.Long[]', 'Long[]',
                 'java.lang.Float[]', 'Float[]', 'java.lang.Byte[]', 'Byte[]', 'java.lang.Boolean[]', 'Boolean[]',
                 'java.util.Collection', 'java.util.List', 'java.util.ArrayList']
    map_type = ['java.util.Map', 'java.util.HashMap']
    if param_type in enum_type:
        if isinstance(value, int):
            return str(value)
        else:
            # 这里兼容入参类型是java.lang.String, 但是这个String是由json转换而成，json必须转义
            return f"'{value}'"
    elif param_type in list_type and isinstance(value, list):
        return json.dumps(value, ensure_ascii=False)
    elif param_type in map_type and isinstance(value, dict):
        value.update({'class': param_type})
        return json.dumps(value, ensure_ascii=False)
    elif param_type not in [*enum_type, *list_type, *map_type] and isinstance(value, dict):
        value.update({'class': param_type})
        return json.dumps(value, ensure_ascii=False)
    elif param_type not in [*enum_type, *list_type, *map_type] and isinstance(value, list):
        return json.dumps(value, ensure_ascii=False)
    elif param_type == '':
        return value
    else:
        return None


class DubboUtil(object):

    def __init__(self, host, port):
        self.conn = self.conn(host, port)

    def conn(self, host, port):
        """
        Telnet连接
        :param host: ip
        :param port: 端口
        :return: 连接对象
        """
        try:
            # 初始化
            conn = telnetlib.Telnet()
            # 设置3秒超时
            conn.open(host, port, timeout=Config.dubbo_connect_timeout)
            return conn
        except Exception as e:
            raise Exception(f'{host}:{port}, Telnet连接出错: {str(e)}')


    def command(self, str_=""):
        # 模拟cmd控制台 dubbo>invoke ...
        self.conn.write(str_.encode() + b'\n')
        data = self.conn.read_until(Config.prompt.encode())
        return data

    def invoke_command(self, service, method, param):
        """
        拼接invoke命令
        :param service: 服务名
        :param method: 方法名
        :param param: 参数
        :return:
        """
        command_str = "invoke {0}.{1}({2})".format(service, method, param)
        data = self.command(command_str)
        try:
            # 字节数据解码 utf8
            data = data.decode("utf-8").split('\n')[0].strip()
        except BaseException:
            # 字节数据解码 gbk
            data = data.decode("gbk").split('\n')[0].strip()
        self.conn.close()
        return data

    def ls_command(self, service, method=None):
        """
        获取服务名下所有的方法
        :param service: 服务名
        :param method: 指定方法名
        :return:
        """
        command_str = "ls -l {0}".format(service)
        data = self.command(command_str)
        if data.decode("utf-8").startswith('No such service'):
            raise Exception(f"{service}没有在Zookeeper中心注册")
        data = data.decode("utf-8").split('\n')[:-1]
        method_data = {}
        for dto in data:
            dubbo_name = dto.strip().split(' ')[1]
            method_name = re.findall(r"(.*?)[(]", dubbo_name)[0]
            param_type_data = re.findall(r"[(](.*?)[)]", dubbo_name)[0]
            param_type_data = param_type_data.split(',')
            method_data[method_name] = param_type_data
        if method:
            if method in method_data.keys():
                data_ = dict()
                data_[method] = method_data.get(method)
                return data_
            else:
                raise Exception(f"{service}服务下不存在{method}方法")
        self.conn.close()
        return method_data

    def invoke(self, service, method, param_dict, param_type_list = None):
        """
        invoke测试dubbo接口
        :param service: 服务名
        :param method: 方法名
        :param param_dict: 参数对象
        :param param_type_list: 实际入参数组
        :return:
        """
        invoke_param_List = []
        if param_type_list:
            error_type_list = []
            for index, key in enumerate(param_dict):
                value = param_type_mapping(param_type_list[index], param_dict[key])
                if not value:
                    error_type_list.append(f"{key}应为{param_type_list[index]}类型")
                else:
                    invoke_param_List.append(value)
            if len(error_type_list) > 0:
                error_msg = '、'.join(error_type_list)
                error_msg += '！请检查！'
                raise Exception(error_msg)
        else:
            for k,v in param_dict.items():
                if isinstance(v, int):
                    invoke_param_List.append(str(v))
                elif isinstance(v, str):
                    invoke_param_List.append(f"'{v}'")
                elif isinstance(v, dict):
                    invoke_param_List.append(json.dumps(v, ensure_ascii=False))
                elif isinstance(v, list):
                    invoke_param_List.append(json.dumps(v, ensure_ascii=False))
                else:
                    invoke_param_List.append(str(v))
        boby = ','.join(invoke_param_List)
        response_data = self.invoke_command(service, method, boby)
        try:
            response_data = json.loads(response_data)
        except Exception as e:
            raise Exception(f"解析json失败: {response_data}！请检查data请求参数！")
        return response_data


class ZookeeperUtil(object):

    def __init__(self):
        self.zk = self.zk_conn()

    def zk_conn(self):
        """
        zookeeper中心连接
        :return: 连接对象
        """
        try:
            zk = KazooClient(hosts=Config.zookeeper_url_list, timeout=Config.zookeeper_connect_timeout)
            zk.start(Config.zookeeper_wait_timeout)  # 与zookeeper连接
            return zk
        except Exception as e:
            raise Exception(f"Zookeeper中心连接失败, 请重试！{str(e)}")


    def get_service_info(self, service):
        """
        获取服务名详情
        :param service: 服务名
        :return:
        """
        dubbo_service_data = []
        #先查出注册中心所有的dubbo服务
        all_node = self.zk.get_children('/dubbo')
        node = [i for i in all_node if service.lower() == i.lower()]
        if not node:
            raise Exception(f"{service}没有在Zookeeper中心注册")
        if len(node) > 1:
            raise Exception(f"{service}在Zookeeper中心注册了两次以上！请联系开发处理！")
        # 查询dubbo服务的详细信息
        node_data = self.zk.get_children(f'/dubbo/{node[0]}/providers')
        if not node_data: raise Exception(f'{node[0]}服务没有提供者！')
        for index, dto in enumerate(node_data):
            service_data = {}
            # parse.unquote 解码
            # parse.urlparse 解析URL
            # parse.query 获取查询参数
            # parse.parse_qsl 返回列表
            url_data = parse.urlparse(parse.unquote(dto))
            query_data = dict(parse.parse_qsl(url_data.query))
            service_data['url'] = url_data.netloc
            service_data['methods'] = query_data['methods'].split(",")
            service_data.update(query_data)
            dubbo_service_data.append(service_data)
        self.zk.stop()
        return dubbo_service_data