__author__ = 'josh'

import sys
import os
import urllib3
import socket
import subprocess
import datetime
from time import sleep
import markup
import re

GLO_SERVER_ADD = 'joshjh.dyndns-home.com'
GLO_SERVER_PORT = 21954 
PAGEFILE = '/var/www/dt/index.html'

class d_tracker_client(object):

    def __init__(self, send_handler):
        # these send calls are a little ugly, might be work unpacking a tupple for parameters
        print('attemping to send first update')
        send_handler.send("{} at: ('{}')('{}')".format(self.__checkin__(), self.__gettime__(), socket.gethostname()),
                                  GLO_SERVER_ADD, GLO_SERVER_PORT)
        print('sent first update')
        while True:
            if self.lastalivedate + datetime.timedelta(seconds=3500) < datetime.datetime.today():
                send_handler.send("{} at: ('{}')('{}')".format(self.__checkin__(), self.__gettime__(),
                socket.gethostname()), GLO_SERVER_ADD, GLO_SERVER_PORT)
            else:
                sleep(3600)

    def __gettime__(self):
        """ Returns the current time, whist setting that as the last update time, as that's the only time it's called.
        Returns self.lastalivedate as string
        """
        self.lastalivedate = datetime.datetime.today()
        return str(self.lastalivedate)

    def __checkin__(self):
        """ gets the external ip from a website and local ip, returns it as string in a tupple"""
        print('getting IP info')
        http = urllib3.PoolManager()
        r = http.request('GET', 'http://ipecho.net/plain')
        intf = 'wlan0'
        intf_ip = subprocess.check_output("/bin/ip address show dev " + intf, shell=True).decode().split()
        intf_ip = intf_ip[intf_ip.index('inet') + 1].split('/')[0]
        print('got IP info')
        return (r.data.decode(), intf_ip)

class d_tracker_server(object):

    def __init__(self):

        self.rpis = []

    def message_handle(self, msg):
        x = re.findall("('\d+.*?\d')", msg)
        y = re.findall("('\w+')", msg)
        if str(x[0]) in str(self.rpis):
            print(x, 'known in rpis')

        else:
            self.rpis.append(x + y)
            print('appended:', x)
            print (self.rpis)
            self.__genpage__()

    def __genpage__(self):
        title = "Josh's RPI devices"
        header = 'Known running entities'
        footer = 'created at {}'.format(datetime.datetime.today())
        styles = ('layout.css', 'alt.css', 'images.css')
        self.page = markup.page()
        self.page.init(css=styles, title=title, header = header, footer=footer)
        self.page.br()
        self.page.ul(class_='mylist')
        self.page.li(self.rpis, class_='myitem')
        self.page.ul.close()
        with open(PAGEFILE, 'w') as f:
            f.write(str(self.page))
            f.close()

class hcs_socket_listen(object):

    def __init__(self, dt):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', GLO_SERVER_PORT))
        s.listen(5)

        while True:
            #  s.accept returns client (cli) object, and connected address (addr)
            cli, addr = s.accept()
            print ('hcs-socket got connect from ', addr)
            cli.send(b'READY:')
            msg = bytes.decode(cli.recv(1024))  # recieve 1024
            dt.message_handle(msg)
        s.close()

class hcs_socket_send(object):

    def __init__(self):
        pass

    def send(self, msg, t_host, t_port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('', 0))
        self.s.connect((t_host, t_port))
        s_handshake = bytes.decode(self.s.recv(1024))

        if s_handshake == 'READY:': # master awaits data
            self.s.send(bytes(msg, 'ascii'))
            self.s.close()
        else:
            print ('unable to send, bad response from master')
            self.s.close()


def main(client=False, server=False):

    if client == True:
            send_handler = hcs_socket_send()
            dt = d_tracker_client(send_handler)
    elif server == True:
        dt = d_tracker_server()
        listener = hcs_socket_listen(dt)
    else:
        print('you must specify client or server')


# boilerplate

if __name__ == '__main__':
    if sys.argv[1] == 'client': main(client=True)

    main(sys.argv[1])
