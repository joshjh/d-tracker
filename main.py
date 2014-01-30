__author__ = 'josh'

import sys
import os
import urllib3

class d_tracker_client(object):

    def __init__(self):


    def check_in():

        http = urllib3.PoolManager()
        r = http.request('GET', 'http://ipecho.net/plain)
        self.our_ip = r.data.decode()

def main(arg):

    if arg == '--client':
        client = True
    elif arg == '--server':
        self.server = True
    else:
        print('d_tracker must by run with the switch --client or --server')
        sys.exit()

    if client:
        dt = d_tracker_client()
    else:
        dt = d_tracker_server()



# boilerplate

if __name__ == __main__:
    main(sys.argv[1])
