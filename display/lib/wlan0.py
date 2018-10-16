#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
IPv4とhost名を表示する
'''
import socket
import os
def ip_check():
	gw = os.popen("ip -4 route show default").read().split()
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect((gw[2], 0))
	ipaddr = s.getsockname()[0]
	gateway = gw[2]
	host = socket.gethostname()
	return ipaddr, host