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
GLO_SERVER_PORT = 42753
PAGEFILE = '/home/josh/test.html'

class d_tracker_client(object):

    def __init__(self, send_handler):

        send_handler.send("{} at: ('{}')('{}')".format(self.__checkin__(), self.__gettime__(), socket.gethostname()),
                                  GLO_SERVER_ADD, GLO_SERVER_PORT)

        while True:
            if self.lastalivedate + datetime.timedelta(seconds=3500) < datetime.datetime.today():
                send_handler.send("{} at: ('{}')('{}')".format(self.__checkin__(), self.__gettime__(), socket.gethostname()),
                                  GLO_SERVER_ADD, GLO_SERVER_PORT)
            else:
                sleep(3600)

    def __gettime__(self):
        self.lastalivedate = datetime.datetime.today()
        return str(self.lastalivedate)

    def __checkin__(self):
        """ gets the external ip from a website and local ip, returns it as string in a tupple"""
        http = urllib3.PoolManager()
        r = http.request('GET', 'http://ipecho.net/plain')
        intf = 'wlan0'
        intf_ip = subprocess.check_output("/bin/ip address show dev " + intf, shell=True).decode().split()
        intf_ip = intf_ip[intf_ip.index('inet') + 1].split('/')[0]
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
        s.bind(('sopra', GLO_SERVER_PORT))
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


def main(arg):
    client = False  # not very clean but avoids try arguement catching whilst testing if client
    server = False
    if arg == '--client':
        client = True
    elif arg == '--server':
        server = True
    else:
        print('d_tracker must by run with the switch --client or --server')
        sys.exit()

    if client:
            send_handler = hcs_socket_send()
            dt = d_tracker_client(send_handler)

    else:
        dt = d_tracker_server()
        listener = hcs_socket_listen(dt)


# boilerplate

if __name__ == '__main__':
    main(sys.argv[1])
