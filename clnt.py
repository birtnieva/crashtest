# simple illustration of thrd module

# two clients connect to server; each client repeatedly sends a letter,
# stored in the variable k, which the server appends to a global string
# v, and reports v to the client; k = '' means the client is dropping
# out; when all clients are gone, server prints the final string v

# this is the client; usage is

# python clnt.py server_address port_number

import socket
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = sys.argv[1] # server address
port = int(sys.argv[2]) # server port
s.connect((host, port))

confirm = s.recv(1)
print(confirm)

while(1):
    # get letter
    k = input('enter a letter:')
    s.send(k) # send k to server
    # if stop signal, then leave loop
    if k == '': break
    v = s.recv(1024) # receive v from server (up to 1024 bytes)
    print(v)

s.close() # close socket