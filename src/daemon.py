#!/usr/bin/env python

import dbus, dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GObject
import status, threading, socket, time
import usermgr, eapauth
from eappacket import *
import os, sys

GObject.threads_init()
dbus.mainloop.glib.threads_init()

class EAPDaemon(dbus.service.Object):
    name = 'com.yah3c.EAPDaemon'
    path = '/' + name.replace('.', '/')
    interface = name

    def __init__(self, event_loop):
        self.bus = dbus.SystemBus()
        self.event_loop = event_loop

        busName = dbus.service.BusName(EAPDaemon.name, bus=self.bus)
        
        dbus.service.Object.__init__(self, busName, EAPDaemon.path)
        
        self.hasLogin = False
        self.yah3c = None
        
        self.um = usermgr.UserMgr()
        
    @dbus.service.method('com.yah3c.EAPDaemon', in_signature='s')
    def Login(self, login_info):
        print 'Do Authorize ', login_info
        login_info = str(login_info)
        self.yah3c = eapauth.EAPAuth(self.um.get_user_info(login_info))
        self.thread = threading.Thread(target=self.serve_forever, args=(self.yah3c, ))
        self.thread.start()
        #self.serve_forever(self.yah3c)

    @dbus.service.method('com.yah3c.EAPDaemon')
    def Logoff(self):
        print 'Do Logoff'
        self.yah3c.send_logoff()
        if self.thread and not self.thread.isAlive():
            self.Status(status.EAP_FAILURE)

    @dbus.service.signal('com.yah3c.EAPDaemon', signature='s')
    def Message(self, message):
        print message
        pass

    @dbus.service.signal('com.yah3c.EAPDaemon', signature='u')
    def Status(self, status):
        print status
        pass

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
            self.Status(status.EAP_FAILURE)
            self.display_prompt('Connection Closed')
            exit(-1)
            
    def display_prompt(self, string):
        #print string
        self.Message(string)
    
    def display_login_message(self, msg):
        """
            display the messages received form the radius server,
            including the error meaasge after logging failed or 
            other meaasge from networking centre
        """
        try:
            decoded = msg.decode('gbk')
            #print decoded
            self.Message(decoded)
        except UnicodeDecodeError:
            #print msg
            self.Message(msg)
        except TypeError:
            pass
        
        
    def EAP_handler(self, eap_packet, yah3c):
        vers, type, eapol_len  = unpack("!BBH",eap_packet[:4])
        if type != EAPOL_EAPPACKET:
            self.display_prompt('Got unknown EAPOL type %i' % type)

        # EAPOL_EAPPACKET type
        code, id, eap_len = unpack("!BBH", eap_packet[4:8])
        if code == EAP_SUCCESS:
            self.display_prompt('Got EAP Success')
            #self.loginSucceedSignal.emit()
            self.Status(status.LOGIN_SUCCEED)
            
        elif code == EAP_FAILURE:
            if (yah3c.has_sent_logoff):
                self.display_prompt('Logoff Successfully!')
                self.display_login_message(eap_packet[10:])
                #self.logoffSucceedSignal.emit()
                self.Status(status.LOGOFF_SUCCEED)
                
                exit(1)
            else:
                self.display_prompt('Got EAP Failure')

                self.display_login_message(eap_packet[10:])
                if self.hasLogin:
                    raise socket.error()
                else:
                    #self.eapfailureSignal.emit()
                    self.Status(status.EAP_FAILURE)
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


if __name__ == "__main__":
    DBusGMainLoop(set_as_default=True)
    loop = GObject.MainLoop()
    service = EAPDaemon(loop)

    print 'Deamon working'

    # Do first fork
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError, e:
        sys.stderr.write("fork #1 failed: (%d) %s\n" % (e.errno, e.strerr))
        sys.exit(1)

    # Decouple from parent environment.
    os.chdir("/")
    os.umask(0)
    os.setsid()

    # Do second fork.
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError, e:
        sys.stderr.write("fork #2 failed: (%d) %s\n" % (e.errno, e.strerr))
        sys.exit(1)

    # Now I am a daemon!

    # Redirect standard file descriptors.
    si = open("/dev/null", 'r')
    so = open("/tmp/gyah3c-daemon.log", 'a+')
    se = open("/tmp/gyah3c-daemon.log", 'a+', 0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(si.fileno(), sys.stdout.fileno())
    os.dup2(si.fileno(), sys.stderr.fileno())

    #Gdk.threads_enter()
    loop.run()
    #Gdk.threads_leave()
