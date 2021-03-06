# -*- coding:utf-8 -*-

from gi.repository import Gtk, Gdk
#try: 
#    from gi.repository import AppIndicator3 as AppIndicator  
#except:  
#    from gi.repository import AppIndicator
from gi.repository import Notify
from gi.repository import GObject
import eapauth, usermgr
from eappacket import *
import threading, socket, time
import status, dbus, dbus.service

class MainWindow(GObject.Object):
        
    #__gsignals__ = {
    #    'login-succeed': (GObject.SignalFlags.RUN_LAST, None, ()), 
    #    'logoff-succeed': (GObject.SignalFlags.RUN_LAST, None, ()),
    #    'eapfailure': (GObject.SignalFlags.RUN_LAST, None, ()),
    #}
    def __init__(self, mainloop):
        GObject.Object.__init__(self)
        self.hasLogin = False
        self.thread = None    
        self.mainloop = mainloop
        self.retryNum = 0
        
        dbusname = 'com.yah3c.EAPDaemon'
        dbuspath = '/' + dbusname.replace('.', '/')
        dbusinterface = dbusname
        
        # DBus Receiver
        self.bus = dbus.SystemBus()
        self.bus.add_signal_receiver(self.dbus_message_handler, dbus_interface=dbusinterface, signal_name='Message')
        self.bus.add_signal_receiver(self.dbus_status_handler, dbus_interface=dbusinterface, signal_name="Status")
        
        #bus_name = dbus.service.BusName(dbusname, bus=self.bus)
        #dbus.service.Object.__init__(self, bus_name, dbuspath)
        
        # DBus Method
        eap_service = 'com.yah3c.EAPDaemon'
        eap_object = '/' + eap_service.replace('.', '/')
        eap_interface = eap_service
        self.eapDaemon = dbus.Interface(self.bus.get_object(eap_service, eap_object), eap_interface)
        
        # Init the Notify
        Notify.init('gYaH3C')
        self.loginSuccedNotify = Notify.Notification.new('gYaH3C', "登录成功", "/usr/share/gYaH3C/icon/icon.png")
        self.eapfailureNotify = Notify.Notification.new('gYaH3C', "已下线", "/usr/share/gYaH3C/icon/icon.png")
        self.runningFaultNotify = Notify.Notification.new('gYaH3C', "已有一个进程在运行，请尝试重启", "/usr/share/gYaH3C/icon/icon.png")
        
        builder = Gtk.Builder()
        builder.add_from_file('/usr/share/gYaH3C/mainwindow.glade')
        builder.connect_signals(self)
        
        # Init the Window
        self.win = builder.get_object('mainWindow')
        self.win.show()
        
        # Connect Signals
        #self.connect('login-succeed', self.on_loginSucceed)
        #self.connect('logoff-succeed', self.on_logoffSucceed)
        #self.connect('eapfailure', self.on_EAPFailure)
        
        # Window Menu
                

        # Label
        self.label = builder.get_object('label')
        self.label.set_text("Ready.")

        # The Button
        self.logButton = builder.get_object('logButton')
        self.logButton.set_label('登录')
        
        self.um = usermgr.UserMgr()
        
        # Init the UserList
        self.userListComboBox = builder.get_object('userListComboBox')
        userlist = self.um.get_all_users_info()
        for i in range(len(userlist)):
            self.userListComboBox.append_text(userlist[i]['username'])
        if len(userlist) != 0:
            self.userListComboBox.set_active(0)
        
        #init the Indicator
        #self.indicator = AppIndicator.Indicator.new(
        #        "indicator-yah3c", 
        #        "/usr/share/gYaH3C/icon/systray.png",
        #        AppIndicator.IndicatorCategory.COMMUNICATIONS)
        # Show the indicator
        #self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)

        self.statusIcon = Gtk.StatusIcon()
        self.statusIcon.set_from_file("/usr/share/gYaH3C/icon/icon.png")
        self.statusIcon.connect("activate", self.on_status_icon_clicked)

        #self.menu = Gtk.Menu()

        # Show/Hide the UI
        #self.togUiMenuItem = Gtk.CheckMenuItem()
        #self.togUiMenuItem.set_label("显示界面")
        #self.togUiMenuItem.set_active(True)
        #self.togUiMenuItem.connect("activate", self.handler_menu_togui)
        #self.togUiMenuItem.show()
        #self.menu.append(self.togUiMenuItem)
        
        # Exit the App
        #self.exitMenuItem = Gtk.MenuItem()
        #self.exitMenuItem.set_label("退出")
        #self.exitMenuItem.connect("activate", self.handler_menu_exit)
        #self.exitMenuItem.show()
        #self.menu.append(self.exitMenuItem)

        # Show the Menu
        #self.menu.show()
        #self.indicator.set_menu(self.menu)

        if self.eapDaemon.IsLogin():
           self.runningFaultNotify.show()
           self.eapDaemon.Logoff()
           exit(1)

    def on_status_icon_clicked(self, widget):
        self.win.show()

    def handler_menu_usermanage(self, widget):
        pass

    def dbus_message_handler(self, message):
        print message
        self.label.set_text(message)
        
    def dbus_status_handler(self, status_code):
        if status_code == status.LOGIN_SUCCEED:
            self.on_loginSucceed()
        elif status_code == status.LOGOFF_SUCCEED:
            self.on_logoffSucceed()
        else:
            self.eapfailureNotify.show()
            self.retryNum += 1
            if self.hasLogin and self.retryNum <= 5:
                self.on_relogin()
                time.sleep(1)
                self.eapDaemon.Login(self.um.get_all_users_info()[self.userListComboBox.get_active()]['username'])
            else:
                self.on_EAPFailure()

    def on_relogin(self):
        self.logButton.set_label('正在重连 #%d' % (self.retryNum + 1))
        self.logButton.set_sensitive(False)
        
    def on_logButton_clicked(self, widget):
        if self.hasLogin:
            self.logButton.set_label('正在下线')
            hasLogin = False
            self.eapDaemon.Logoff()
        else:
            self.logButton.set_label('正在登录')
            self.userListComboBox.set_sensitive(False)
            self.eapDaemon.Login(self.um.get_all_users_info()[self.userListComboBox.get_active()]['username'])
        
        self.logButton.set_sensitive(False)

    def on_mainWindow_delete_event(self, widget, evt):
        if self.hasLogin:
            self.win.hide()
            #self.togUiMenuItem.set_active(False)
            return True
        else:
            self.mainloop.quit()

    #def handler_menu_togui(self, widget):
    #    if widget.get_active():
    #        self.win.show()
    #    else:
    #        self.win.hide()

    def handler_menu_exit(self, evt):
        self.eapDaemon.Logoff()
        self.mainloop.quit()

    def on_userListComboBox_changed(self, widget):
        #print widget.get_active()
        pass
        
    def on_loginSucceed(self):
        self.retryNum = 0
        self.loginSuccedNotify.show()
        self.hasLogin = True
        self.logButton.set_label('下线')
        self.logButton.set_sensitive(True)
        self.win.hide()
        #self.togUiMenuItem.set_active(False)

    def on_logoffSucceed(self):
        self.hasLogin = False
        self.logButton.set_label('登录')
        self.logButton.set_sensitive(True)
        self.userListComboBox.set_sensitive(True)

    def on_EAPFailure(self):
        self.hasLogin = False
        self.logButton.set_label('登录')
        self.logButton.set_sensitive(True)
        self.userListComboBox.set_sensitive(True)
        
    
