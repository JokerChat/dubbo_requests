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
# 获取dubbo服务详情
data = dubborequests.search('cn.com.xxx.sso.ehr.api.dubbo.SsoEmpInfoService')
```

#### 获取服务下的所有方法

```python
# 导入
import dubborequests
# 获取dubbo服务下的所有方法
data = dubborequests.list('cn.com.xxx.sso.ehr.api.dubbo.SsoEmpInfoService')
# 获取dubbo服务指定的方法
data = dubborequests.list('cn.com.xxx.sso.ehr.api.dubbo.SsoEmpInfoService', 'login')
```

#### 通过zookeeper获取服务的ip和端口, Telnet命令测试dubbo接口

```python
import dubborequests
from dubborequests import Config
# 先配置zookeeper中心地址
Config.zookeeper_url_list = ['192.168.240.15:2181', '192.168.240.15:2182', '192.168.240.15:2183']
invoke_data = {
    "service_name": "cn.com.xxxxx.sso.ehr.api.dubbo.SsoEmpInfoService",
    "method_name": "login",
    "data": {
        "account": "xxxx",
        "password": "xxxx"
    }
}
# 通过zookeeper获取服务的ip和端口, Telnet命令测试dubbo接口
data = dubborequests.zk_invoke(*invoke_data)
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
data = dubborequests.telnet_invoke(*invoke_data)
```