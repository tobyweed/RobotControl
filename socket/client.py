#!/usr/bin/env python3

import socket
import sys

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 50001 # The port used by the server

if __name__ == '__main__':


    if len(sys.argv) != 1 and len(sys.argv) != 2:
        print("""usage: python3 RobotImitation_client.py [pathname]
        - without pathname: create a new path
        - with pathname: load the path with specified pathname""")    
        exit()


    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        if(len(sys.argv)==1):
            s.send(b'new')
        else:
            name = sys.argv[1]
            file_name = '%s.obj'%name
            s.send(file_name.encode("utf-8"))
        data = s.recv(1024)
    print(data.decode("utf-8"))
    
    while True:
        command = input("Enter Command:")
        if not command:
            command = 'foo'
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.send(command.encode("utf-8"))
            data = s.recv(1024)
        print(data.decode("utf-8"))
        if(command == "q"):
            break
