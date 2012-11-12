#!/bin/sh

SOFTWARE=usr/share/gYaH3C
ICON=$SOFTWARE/icon
DBUS_SYSTEMD=etc/dbus-1/system.d
DBUS_SERVICE=usr/share/dbus-1/system-services
SYSTEM_PIXMAP=usr/share/pixmaps
APP_PATH=usr/share/applications
INIT_PATH=etc/init.d

rm -rf pkg
mkdir pkg
mkdir -p pkg/$ICON
mkdir -p pkg/$DBUS_SYSTEMD
mkdir -p pkg/$DBUS_SERVICE
mkdir -p pkg/$SYSTEM_PIXMAP
mkdir -p pkg/$APP_PATH
mkdir -p pkg/$INIT_PATH

cp icon/* pkg/$ICON
sudo rm src/*.pyc
cp src/*.py pkg/$SOFTWARE
cp src/*.glade pkg/$SOFTWARE
cp src/*.conf pkg/$DBUS_SYSTEMD
cp src/*.service pkg/$DBUS_SERVICE
cp icon/icon.png pkg/$SYSTEM_PIXMAP/gYaH3C.png
cp src/gYaH3C.desktop pkg/$APP_PATH
cp src/gyah3c-daemon pkg/$INIT_PATH
cp -r DEBIAN pkg/

dpkg -b ./pkg gyah3c_0.3_all.deb
