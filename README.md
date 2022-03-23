### 一、安装（python版本建议3.7以上）

```bash
pip install dubborequests
```
### 二、升级包
```bash
pip install --upgrade dubborequests
```
### 三、示例

#### 获取dubbo服务详情

```python
# 导入
import dubborequests
from dubborequests.config import Config
Config.zookeeper_url_list = ['192.168.240.15:2181', '192.168.240.15:2182', '192.168.240.15:2183']
# 获取dubbo服务详情
data = dubborequests.search('cn.com.xxx.sso.ehr.api.dubbo.SsoEmpInfoService')
```

#### 获取服务下的所有方法

```python
# 导入
import dubborequests
from dubborequests.config import Config
Config.zookeeper_url_list = ['192.168.240.15:2181', '192.168.240.15:2182', '192.168.240.15:2183']
# 获取dubbo服务下的所有方法
service_data = dubborequests.list('cn.com.xxx.sso.ehr.api.dubbo.SsoEmpInfoService')
# 获取dubbo服务指定的方法
method_data = dubborequests.list('cn.com.xxx.sso.ehr.api.dubbo.SsoEmpInfoService', 'login')
```

#### 通过zookeeper获取服务的ip和端口, Telnet命令测试dubbo接口

```python
import dubborequests
from dubborequests import Config
# 先配置zookeeper中心地址
Config.zookeeper_url_list = ['192.168.240.15:2181', '192.168.240.15:2182', '192.168.240.15:2183']
service_name = "cn.com.xxxxx.sso.ehr.api.dubbo.SsoEmpInfoService"
method_name = "login"
data = {
        "account": "xxxx",
        "password": "xxxx"
    }
# 通过zookeeper获取服务的ip和端口, Telnet命令测试dubbo接口
res_data = dubborequests.zk_invoke(service_name, method_name, data)
# 如果入参类型是java.lang.String
invoke_data1 = {
        "account": "xxxx"
    }
# 如果入参类型是java.util.List
invoke_data2 = {
        "list_": ['数组的内容']
    }
# 如果入参类型是java.util.Map、java.util.HashMap或者自定义对象名(com.your.package.BeanName)
invoke_data3 = {
        "map_": {
          "age":27,
          "name": "clearlove7"
        }
    }
# 如果无需入参类型, data为空dict即可
invoke_data4 = {}
# 组合入参类型1, java.lang.String、java.lang.String
invoke_data5 = {
        "account": "xxxx",
        "password": "xxxx"
    }
# 组合入参类型2, java.lang.String、java.util.List
invoke_data6 = {
        "account": "xxxx",
        "list_": ['数组的内容']
    }
# 组合入参类型3, cn.com.xxx.xxx.dto.xxx.ProductQuery、java.util.Map
invoke_data7 = {
    "map1": {
        "product": 10086,
        "num": 1
    },
    "map2": {
        "age": 27,
        "name": "clearlove7"
    }
}
# 注意：
#1、len(data)必须等于方法入参个数
#2、data里面的key可以随意命名，data必须为dict类型
#3、data里面的key-value排序必须按照方法定义的入参顺序
# 详细可参照：https://github.com/thubbo/jmeter-plugins-for-apache-dubbo/wiki/ParameterComparisonTable
```

#### Telnet命令测试dubbo接口

```python
import dubborequests
invoke_data = {
    "ip": 'xxxx',
    "port": 7777,
    "service_name": "cn.com.xxxxx.sso.ehr.api.dubbo.SsoEmpInfoService",
    "method_name": "login",
    "data": {
        "account": "xxxx",
        "password": "xxxx"
    }
}
 # Telnet命令测试dubbo接口
res_data = dubborequests.telnet_invoke(*invoke_data)
# 入参例子参考上面👆🏻
```