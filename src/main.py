#!/usr/bin/env python
# -*- coding:utf-8 -*-

from gi.repository import Gtk, GLib, Gdk, GObject
import dbus
from mainwindow import MainWindow
from dbus.mainloop.glib import DBusGMainLoop

GObject.threads_init()

def main():
    DBusGMainLoop(set_as_default=True)
    mainloop = GObject.MainLoop()
    MainWindow(mainloop)
    
    Gdk.threads_enter()
    #Gtk.main()
    mainloop.run()
    Gdk.threads_leave()

if __name__ == "__main__":
    main()
