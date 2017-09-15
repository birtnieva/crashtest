# simple illustration of thrd module

# multiple clients connect to server; each client repeatedly sends a
# letter k, which the server adds to a global string v and echos back
# to the client; k = '' means the client is dropping out; when all
# clients are gone, server prints final value of v

# this is the server

import socket
import sys
from pth import *

class glbs: # globals
    v = '' # the string we are building up from the clients

class serveclient(thrd):
    def __init__(self,id,c):
        thrd.__init__(self,id)  # like Threading class, we subclass thrd
        self.c = c[0]           # socket for this client
        try:
            self.c.send('c')        # confirm connection
        except TypeError:
            print('Send bytes-like object')
    def run(self):
        while 1:
            # receive letter or EOF signal from c
            try:
                k = self.c.recv(1)
                if k == '':
                    break
                # concatenate v with k, but do NOT need a lock
                glbs.v += k
                self.c.send(glbs.v)
            except:
                pass
            # here comes the main difference; we use yield to relinquish
            # our turn; yield allows one argument, in this case the tuple
            # ('clnt loop','pause'); the first element, 'clnt loop' is for
            # documentation and debugging purposes, but the second,
            # 'pause', tells the threads manager what state we want this
            # thread to be in, in this case Run
            yield 'clnt loop', 'pause'
        self.c.close()

def main():
    lstn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = int(sys.argv[1]) # server port number
    lstn.bind(('', port))
    lstn.listen(5)
    # initialize concatenated string, v
    glbs.v = ''
    # number of clients
    nclnt = 2
    # accept calls from the clients
    for i in range(nclnt):
        (clnt,ap) = lstn.accept()
        clnt.setblocking(0) # set client socket to be nonblocking
        # start thread for this client, with the first argument being a
        # string ID I choose for this thread, and the second argument begin
        # (a tuple consisting of) the socket
        t = serveclient('client '+str(i),(clnt,))
    # shut down the server socket, since it's not needed anymore
    lstn.close()
    # start the threads; the call will block until all threads are done
    thrd.tmgr()
    print('the final value of v is', glbs.v)

if __name__ == '__main__':
    main()