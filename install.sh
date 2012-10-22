#!/bin/sh

SOFTWARE=/usr/share/gYaH3C
ICON=$SOFTWARE/icon
DBUS_SYSTEMD=/etc/dbus-1/system.d
DBUS_SERVICE=/usr/share/dbus-1/system-services
SYSTEM_PIXMAP=/usr/share/pixmaps
APP_PATH=/usr/share/applications
INIT_PATH=/etc/init.d

rm -rf pkg
mkdir pkg
mkdir -p $ICON

cp icon/* $ICON
cp src/*.py $SOFTWARE
cp src/*.glade $SOFTWARE
cp src/*.conf $DBUS_SYSTEMD
cp src/*.service $DBUS_SERVICE
cp icon/icon.png $SYSTEM_PIXMAP/gYaH3C.png
cp src/gYaH3C.desktop $APP_PATH
cp src/gyah3c-daemon $INIT_PATH

ln -s /usr/share/gYaH3C/daemon.py /usr/bin/gyah3c-daemon
ln -s /usr/share/gYaH3C/main.py /usr/bin/gyah3c
ln -s /usr/share/gYaH3C/gyah3c-adduser.py /usr/bin/gyah3c-adduser
chmod +x $APP_PATH/daemon.py $APP_PATH/main.py $APP_PATH/gyah3c-adduser.py
