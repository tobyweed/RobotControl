#!/usr/bin/env python3

import socket

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)



def foo1(client):
    print('I am a')
    client.sendall(b'foo1')

def foo2(client):
    print('I am b')
    client.sendall(b'foo2')

if __name__ == '__main__':
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    command = data.decode("utf-8")
                    if command == 'a':
                        foo1(conn)
                    else:
                        foo2(conn)
