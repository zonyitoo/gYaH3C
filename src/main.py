#!/usr/bin/env python
# -*- coding:utf-8 -*-

from gi.repository import Gtk, GLib, Gdk, GObject
from indicator import IndicatorYaH3C
from mainwindow import MainWindow

GObject.threads_init()

def main():
    #IndicatorYaH3C()
    MainWindow()
    Gdk.threads_enter()
    Gtk.main()
    Gdk.threads_leave()

if __name__ == "__main__":
    main()
