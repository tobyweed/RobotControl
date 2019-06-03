#!/usr/bin/env python3

import asyncio
import pickle
import sys
from pyquaternion import Quaternion
from xamla_motion.data_types import CartesianPath, JointPath, Pose, JointValues
from xamla_motion.motion_client import EndEffector, MoveGroup
from xamla_motion.utility import register_asyncio_shutdown_handler
import socket

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)


def newPath():
    i = 0;
    while True:
        client = client_socket()
        data = client.recv(1024)
        mode = data.decode("utf-8")
        if command == 'new':
            newPath()
        else:
            loadPath(pathName)


def client_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()
    conn,addr = s.accept()
    return conn
    
if __name__ == '__main__':

    client = client_socket()
    data = client.recv(1024)
    mode = data.decode("utf-8")
    if command == 'new':
        print('foo1')
        #path = newPath()
    else:
        print('foo2')
#        path = loadPath(pathName)
                        
