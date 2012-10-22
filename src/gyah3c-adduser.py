#!/usr/bin/env python
# -*- coding:utf8 -*-

import eapauth
import usermgr
import os
import ConfigParser
import getpass

def prompt_user_info():
    username = raw_input('Input username: ')
    while True:
        password = getpass.getpass('Input password: ')
        password_again = getpass.getpass('Input again: ')
        if password == password_again:
            break
        else:
            print 'Password do not match!'

    dev = raw_input('Decice(eth0 by default): ')
    if not dev:
        dev = 'eth0'

    choice = raw_input('Forked to background after authentication(Yes by default)\n<Y/N>: ')
    if choice == 'n' or choice == 'N':
        daemon = False
    else:
        daemon = True

    dhcp_cmd = raw_input('Dhcp command(Press Enter to pass): ')
    if not dhcp_cmd:
        dhcp_cmd = ''
    return {
        'username': username,
        'password': password,
        'ethernet_interface': dev,
        'daemon': daemon,
        'dhcp_command': dhcp_cmd
    }
    
if __name__ == "__main__":
    if not (os.getuid() == 0):
        print (u'亲，要加sudo!')
        exit(-1)
    
    um = usermgr.UserMgr()
    
    try:
        user_info = prompt_user_info()
        um.add_user(user_info)
    except ConfigParser.DuplicateSectionError:
        print 'User already exist!'
        exit(-1)
        
    print "\nDone!"
    print "Try to reopen gYaH3C to refresh the userlist"
