#!/bin/env python
""" This is a parser for openvpn status files, version 3.

How to use:

- add "status-version 3" to openvpn server configuration. Reload/restart openvpn server.
- locate openvpn status file. Usually it's under /var/run in Unix based systems.
- Run "python openvpn-status-parser.py <filename>" for demo. Sample file with random data
  is included in the repository, try it with "python openvpn-status-parser.py".

MIT License:

Copyright (C) 2012, Olli Jarva <olli.jarva@futurice.com>

Permission is hereby granted, free of charge, to any person obtaining a 
copy of this software and associated documentation files (the 
"Software"), to deal in the Software without restriction, including 
without limitation the rights to use, copy, modify, merge, publish, 
distribute, sublicense, and/or sell copies of the Software, and to 
permit persons to whom the Software is furnished to do so, subject to 
the following conditions:

The above copyright notice and this permission notice shall be included 
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS 
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF 
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY 
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE 
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE. 

"""

import pprint
import csv
import datetime
import logging
import sys
import subprocess

class OpenVPNStatusParser:
    def __init__(self, filename):
        self.filename = filename
        self.connected_clients = None
	self.parse_file()
        self.info_time
	self.what

    def parse_file(self):
        self.connected_clients = {}
        csvreader = csv.reader(open(self.filename), delimiter='\t')
        for row in csvreader:
            row_title = row[0] 
            if row_title == "TIME":
                try:
                    self.info_time= datetime.datetime.fromtimestamp(int(row[2]))
                except (IndexError, ValueError):
                    logging.error("TIME row is invalid: %s" % row)

            elif row_title == "CLIENT_LIST":
                try:
                    self.connected_clients[row[2]] = { "VirtAddr":row[3],"recd":row[4],"sent":row[5],"startts":row[7] }
                except IndexError:
                    logging.error("CLIENT_LIST row is invalid: %s" % row)

            elif row_title == "ROUTING_TABLE":
                try:
                    self.connected_clients[row[3]].update({ "stopts":row[5]})
                except IndexError:
                    logging.error("ROUTING_TABLE row is invalid: %s" % row)

            elif row_title == "GLOBAL_STATS":
                try:
                    self.what= row[2]
                except IndexError:
                    logging.error("GLOBAL_STATS row is invalid: %s" % row)


def main():
    if len(sys.argv) == 1:
        files = ["/etc/openvpn/status.log"]
    else:
        files = sys.argv[1:]

    for file in files:
        parser = OpenVPNStatusParser(file)
	print "\n"
        print "="*79
        print "Connected VPN Clients on the XSCENET\nLast updated:         %s"%(parser.info_time)
	print "Current machine time: %s"%datetime.datetime.today()
        print "-"*79
	print "   vpn ip          actual ip         connect time         handle"
        print "-"*79
        for x in parser.connected_clients:
		try:
		    secs = long(parser.connected_clients[x]["stopts"]) - long(parser.connected_clients[x]["startts"])
		except:
		    secs = 0
		m, s = divmod(secs, 60)
		h, m = divmod(m , 60)
		d, h = divmod(h , 24)
		readabletime = "%sd %sh %sm"%(d,h,m)

		# get the handle for this client
		ip = parser.connected_clients[x]["VirtAddr"]
		cmd = "/bin/ncat -i1 %s 1705"%ip
		FNULL = open('/dev/null','w')
		result = subprocess.Popen(cmd, stdout=subprocess.PIPE,shell=True,	
				stderr=FNULL).communicate()[0]

		print(parser.connected_clients[x]["VirtAddr"],x,readabletime, result.rstrip())
	print "\n"

if __name__ == '__main__':
    main()
