# gYaH3C
一个带GUI界面的YaH3C，带有DBus支持和AppIndicator

## 测试环境
* Ubuntu12.10 x64
* 中山大学东校区
* Python 2.7.3

## 依赖
* python2.7
* python-netifaces
* python-appindicator
* python-dbus

## 安装
首先应先装好依赖关系包

* 可直接从[这里](https://github.com/zonyitoo/gYaH3C/downloads)下载deb包直接安装

```bash
sudo dpkg -i gyah3c_[VERSION]_all.deb
```

安装完成后需先启动daemon进程
```bash
sudo service gyah3c-daemon start
```

* 从源码安装

因为使用了DBus的SystemBus，所以要先向系统注册一下下
```bash
sudo cp com.yah3c.EAPDaemon.conf /etc/dbus-1/system.d/
sudo cp com.yah3c.EAPDaemon.service /usr/share/dbus-1/system-services/
```
然后执行`install.sh`
## TODO
* 用户管理模块
