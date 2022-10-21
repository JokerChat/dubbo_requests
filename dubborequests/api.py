# -*- coding: utf-8 -*- 
# @Time : 2022/3/22 20:44 
# @Author : junjie
# @File : api.py

from .util import DubboUtil, ZookeeperUtil


def search(service_name, version = None):
    """
    获取dubbo服务详情
    :param service_name: 服务名
    :param version: 版本号
    :return:
    """
    zk_conn = ZookeeperUtil()
    service_info = zk_conn.get_service_info(service_name)
    if version:
        service_info = [i for i in service_info if i.get('version') == version]
    return service_info

def __get_conn_dto(service_name, version = None):
    """
    通过zookeeper获取连接对象和可连接的dubbo服务
    :param service_name: 服务名
    :param version: 版本号
    :return: 返回连接对象和dubbo
    """
    dubbo_data = None
    dubbo_conn = None
    service_info = search(service_name, version)
    if not service_info: raise Exception(f"{service_name}在Zookeeper中心不存在{version}版本")
    for service in service_info:
        ip, port = service['url'].split(':')
        try:
            # 取一个可以连通的ip地址
            dubbo_conn = DubboUtil(ip, port)
            status = dubbo_conn.command()
            if status:
                dubbo_data = service
                break
        except:
            pass
    if dubbo_conn is None: raise Exception(f'{service_name}服务连接出错')
    return dubbo_conn, dubbo_data


def list(service_name, method_name=None, version=None):
    """
    获取服务名下的所有方法
    :param service_name: 服务名
    :param method_name: 方法名, 传值就获取指定方法名
    :param version: 版本号
    :return:
    """
    dubbo_conn, dubbo_data = __get_conn_dto(service_name, version)
    ls_invoke_data = dubbo_conn.ls_command(dubbo_data['interface'], method_name)
    return [dict(method=k, param_type=v) for k,v in ls_invoke_data.items()]

def zk_invoke(service_name, method_name, data, version = None):
    """
    通过zookeeper获取服务的ip和端口, invoke命令测试dubbo接口
    :param service_name: 服务名zk_invoke
    :param method_name: 方法名
    :param data: 参数对象
    :param version: 版本号
    :return:
    """
    dubbo_conn, dubbo_data = __get_conn_dto(service_name, version)
    param_type_list = dubbo_conn.ls_command(dubbo_data['interface'], method_name)[method_name]
    invoke_data = dubbo_conn.invoke(service_name, method_name, data, param_type_list)
    return dict(invoke_data=invoke_data, param_type_list=param_type_list)

def telnet_invoke(ip, port, service_name, method_name, data):
    """
    手动telnet测试dubbo接口
    :param ip: ip
    :param port: 端口
    :param service_name: 服务名
    :param method_name: 方法名
    :param data: 参数对象
    :return:
    """
    dubbo_conn = DubboUtil(ip, port)
    invoke_data = dubbo_conn.invoke(service_name, method_name, data)
    return invoke_data

def telnet_list(ip, port, service_name, method_name=None):
    """
    手动telnet获取服务下的所有方法
    :param ip:ip
    :param port: 端口
    :param service_name: 服务名
    :param method_name: 方法名
    :return:
    """
    dubbo_conn = DubboUtil(ip, port)
    list_data = dubbo_conn.ls_command(service_name, method_name)
    return [dict(method=k, param_type=v) for k, v in list_data.items()]