# -*- coding:utf-8 -*-

from gi.repository import Gtk, Gdk
try: 
    from gi.repository import AppIndicator3 as AppIndicator  
except:  
    from gi.repository import AppIndicator
from gi.repository import Notify
from gi.repository import GObject
import eapauth, usermgr
from eappacket import *
import threading, socket, time

class MainWindow(GObject.Object):
        
    __gsignals__ = {
        'login-succeed': (GObject.SignalFlags.RUN_LAST, None, ()), 
        'logoff-succeed': (GObject.SignalFlags.RUN_LAST, None, ()),
        'eapfailure': (GObject.SignalFlags.RUN_LAST, None, ()),
    }
    def __init__(self):
        GObject.Object.__init__(self)
        self.hasLogin = False
        self.thread = None    
        self.yah3c = None
        
        # Init the Notify
        Notify.init('gYaH3C')
        self.loginSuccedNotify = Notify.Notification.new('gYaH3C', "登录成功", "/usr/share/qYaH3C/image/icon.png")
        
        builder = Gtk.Builder()
        builder.add_from_file('mainwindow.glade')
        builder.connect_signals(self)
        
        # Init the Window
        self.win = builder.get_object('mainWindow')
        self.win.show()
        
        # Connect Signals
        self.connect('login-succeed', self.on_loginSucceed)
        self.connect('logoff-succeed', self.on_logoffSucceed)
        self.connect('eapfailure', self.on_EAPFailure)
        
        # The Button
        self.logButton = builder.get_object('logButton')
        self.logButton.set_label(u'登录')
        
        self.um = usermgr.UserMgr()
        
        # Init the UserList
        self.userListComboBox = builder.get_object('userListComboBox')
        userlist = self.um.get_all_users_info()
        for i in range(len(userlist)):
            self.userListComboBox.append_text(userlist[i]['username'])
        if len(userlist) != 0:
            self.userListComboBox.set_active(0)
        self.userListComboBox.append_text(u'添加新用户')
        
        #init the Indicator
        self.indicator = AppIndicator.Indicator.new(
                "indicator-yah3c", 
                "/usr/share/qYaH3C/image/systray.png",
                AppIndicator.IndicatorCategory.COMMUNICATIONS)
        # Show the indicator
        self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)

        self.menu = Gtk.Menu()

        # Show/Hide the UI
        self.togUiMenuItem = Gtk.CheckMenuItem()
        self.togUiMenuItem.set_label(u"显示界面")
        self.togUiMenuItem.set_active(True)
        self.togUiMenuItem.connect("activate", self.handler_menu_togui)
        self.togUiMenuItem.show()
        self.menu.append(self.togUiMenuItem)
        
        # Exit the App
        self.exitMenuItem = Gtk.MenuItem()
        self.exitMenuItem.set_label(u"退出")
        self.exitMenuItem.connect("activate", self.handler_menu_exit)
        self.exitMenuItem.show()
        self.menu.append(self.exitMenuItem)

        # Show the Menu
        self.menu.show()
        self.indicator.set_menu(self.menu)

    def on_logButton_clicked(self, widget):
        if self.hasLogin:
            self.logButton.set_label(u'正在下线')
            hasLogin = False
            self.yah3c.send_logoff()
            if self.thread and not self.thread.isAlive():
                self.on_EAPFailure()
        else:
            self.logButton.set_label(u'正在登录')
            self.userListComboBox.set_sensitive(False)
            
            self.yah3c = eapauth.EAPAuth(self.um.get_all_users_info()[self.userListComboBox.get_active()])
            self.thread = threading.Thread(target=self.serve_forever, args=(self.yah3c, ))
            self.thread.start()
        self.logButton.set_sensitive(False)

    def on_mainWindow_delete_event(self, widget, evt):
        if self.hasLogin:
            self.win.hide()
            self.togUiMenuItem.set_active(False)
            return True
        else:
            Gtk.main_quit()

    def handler_menu_togui(self, widget):
        if widget.get_active():
            self.win.show()
        else:
            self.win.hide()

    def handler_menu_exit(self, evt):
        Gtk.main_quit()

    def on_userListComboBox_changed(self, widget):
        print widget.get_active()
        
    def on_loginSucceed(self, args):
        self.loginSuccedNotify.show()
        self.hasLogin = True
        self.logButton.set_label(u'下线')
        self.logButton.set_sensitive(True)

    def on_logoffSucceed(self, args):
        self.hasLogin = False
        self.logButton.set_label(u'登录')
        self.logButton.set_sensitive(True)
        self.userListComboBox.set_sensitive(True)

    def on_EAPFailure(self):
        print 'FAIL'
        
    def serve_forever(self, yah3c):
        retry_num = 1
        
        while retry_num <= 5:
            try:
                yah3c.send_start()
                while True:
                    eap_packet = yah3c.client.recv(200)
                    # strip the ethernet_header and handle
                    self.EAP_handler(eap_packet[14:], yah3c)
                    retry_num = 1
            except socket.error, msg:
                self.display_prompt("Connection error! retry %d" % retry_num)
                time.sleep(retry_num * 2)
                retry_num += 1
            except KeyboardInterrupt:
                self.display_prompt('Interrupted by user')
                yah3c.send_logoff()
                exit(1)
        else:
            #self.eapfailureSignal.emit()
            self.display_prompt('Connection Closed')
            exit(-1)
            
    def display_prompt(self, string):
        #print string
        print string
    
    def display_login_message(self, msg):
        """
            display the messages received form the radius server,
            including the error meaasge after logging failed or 
            other meaasge from networking centre
        """
        try:
            decoded = msg.decode('gbk')
            #print decoded
            print decoded
        except UnicodeDecodeError:
            #print msg
            print decoded
        
        
    def EAP_handler(self, eap_packet, yah3c):
        vers, type, eapol_len  = unpack("!BBH",eap_packet[:4])
        if type != EAPOL_EAPPACKET:
            self.display_prompt('Got unknown EAPOL type %i' % type)

        # EAPOL_EAPPACKET type
        code, id, eap_len = unpack("!BBH", eap_packet[4:8])
        if code == EAP_SUCCESS:
            self.display_prompt('Got EAP Success')
            #self.loginSucceedSignal.emit()
            self.emit('login-succeed')
            
        elif code == EAP_FAILURE:
            if (yah3c.has_sent_logoff):
                self.display_prompt('Logoff Successfully!')
                self.display_login_message(eap_packet[10:])
                #self.logoffSucceedSignal.emit()
                self.emit('logoff-succeed')
                
                exit(1)
            else:
                self.display_prompt('Got EAP Failure')

                self.display_login_message(eap_packet[10:])
                if self.hasLogin:
                    raise socket.error()
                else:
                    #self.eapfailureSignal.emit()
                    self.emit('eapfailure')
                    exit(1)
        elif code == EAP_RESPONSE:
            self.display_prompt('Got Unknown EAP Response')
        elif code == EAP_REQUEST:
            reqtype = unpack("!B", eap_packet[8:9])[0]
            reqdata = eap_packet[9:4 + eap_len]
            if reqtype == EAP_TYPE_ID:
                self.display_prompt('Got EAP Request for identity')
                yah3c.send_response_id(id)
                self.display_prompt('Sending EAP response with identity')
            elif reqtype == EAP_TYPE_H3C:
                self.display_prompt('Got EAP Request for Allocation')
                yah3c.send_response_h3c(id)
                self.display_prompt('Sending EAP response with password')
            elif reqtype == EAP_TYPE_MD5:
                data_len = unpack("!B", reqdata[0:1])[0]
                md5data = reqdata[1:1 + data_len]
                self.display_prompt('Got EAP Request for MD5-Challenge')
                yah3c.send_response_md5(id, md5data)
                self.display_prompt('Sending EAP response with password')
            else:
                self.display_prompt('Got unknown Request type (%i)' % reqtype)
        elif code==10 and id==5:
            self.display_login_message(eap_packet[12:])
        else:
            self.display_prompt('Got unknown EAP code (%i)' % code)
