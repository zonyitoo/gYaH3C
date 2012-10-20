# gYaH3C
一个带GUI界面的YaH3C，带有DBus支持和AppIndicator

只在Ubuntu12.10下测试

## 安装
因为使用了DBus的SystemBus，所以要先向系统注册一下下
```bash
sudo cp com.yah3c.EAPDaemon.conf /etc/dbus-1/system.d/
sudo cp com.yah3c.EAPDaemon.service /usr/share/dbus-1/system-services/
```

先运行`daemon.py`，用root权限，然后用普通用户权限运行`main.py`
## TODO
* 用户管理模块
