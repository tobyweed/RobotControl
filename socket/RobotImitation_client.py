#!/usr/bin/env python3
# python test code for server
# Guanghan Pan

import socket
import sys

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 50001 # The port used by the server

if __name__ == '__main__':
    
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
