# LoadPath_server.py
# 2019 Middlebury College Summer Research with Professor Scharstein
# Guanghan Pan

#!/usr/bin/env python3

import asyncio
import pickle
import sys
import time
from pyquaternion import Quaternion
from xamla_motion.data_types import CartesianPath, JointPath, Pose, JointValues
from xamla_motion.v2.motion_client import EndEffector, MoveGroup
from xamla_motion.utility import register_asyncio_shutdown_handler
import socket
import numpy as np
import math

HOST = '' 
PORT = 50001        # Port to listen on (non-privileged ports are > 1023)

async def move_path(move_group):
    velocity = 0.05
    running = True
    path = ''
    file_path = open("test.obj", 'rb')
    path = pickle.load(file_path)
    print(path)
    while running:
        time.sleep(0.5)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        s.settimeout(None)
        # print(s.gettimeout())
        # print('waiting for connection')
        conn, addr = s.accept()
        with conn:
            while 1:
                data = conn.recv(1024)
                if not data:
                    break
                instruction = data.decode("utf-8")
                splitins = instruction.split()
                print(splitins)
                if len(splitins) == 2 and splitins[0] == 'load':
                    # print('loading a path')
                    pathName = splitins[1]
                    try:
                        file_path = open(pathName, 'rb') 
                    except:
                        message = 'An error occurs while loading %s'%pathName
                        conn.sendall(message.encode("utf-8"))
                    else:
                        message = 'Sucessfully loaded %s'%pathName
                        conn.sendall(message.encode("utf-8"))
                        path = pickle.load(file_path)
                elif instruction == "q":
                    running = False
                    conn.sendall(b'bye')
                elif path:
                    if instruction.isdigit():
                        view_points = path.points
                        num = int(instruction)
                        if num < len(view_points):
                            print('--- Going to Viewpoint %d---' %num)
                            move_joints_cf = move_group.move_joints_collision_free(view_points[num], velocity_scaling = velocity)
                            await move_joints_cf.plan().execute_async()
                            conn.sendall(b'success')
                        else:
                            conn.sendall(b'There are %d viewpoints, please enter a valid number' %len(view_points))
                    elif instruction == "e":
                        print("--- moving to the first viewpoint ---")
                        move_joints_cf = move_group.move_joints_collision_free(path.points[0], velocity_scaling = velocity)
                        await move_joints_cf.plan().execute_async()
                        print("--- executing the path ---")
                        move_joints = move_group.move_joints(path, velocity_scaling = velocity)
                        await move_joints.plan().execute_async()
                        print("--- Finished ---")
                        conn.sendall(b'success')
                    elif len(splitins)==2 and splitins[0]=='v':
                        new_velocity = float(splitins[1])
                        if new_velocity>0 and new_velocity<=1:
                            velocity = str(new_velocity)
                            message = 'Successfully set velocity to '+velocity
                            conn.sendall(message.encode("utf-8"))
                        else:
                            conn.sendall(b'please enter a valid number, 0-1')
                    elif len(splitins)==2 and splitins[0]=='r':
                        degree = float(splitins[1])
                        radian = degree/180 * math.pi
                        path = JointPath(path.joint_set,[x.set_values(path.joint_set,x.values+np.array([-radian,0,0,0,0,0])) for x in path.points])
                        message = 'Successfully rotate path to the right by '+ str(degree) + ' degrees'
                        conn.sendall(message.encode("utf-8"))
                    elif len(splitins)==2 and splitins[0]=='l':
                        degree = float(splitins[1])
                        radian = degree/180 * math.pi
                        path = JointPath(path.joint_set,[x.set_values(path.joint_set,x.values+np.array([radian,0,0,0,0,0])) for x in path.points])
                        message = 'Successfully rotate path to the left by '+ str(degree) + ' degrees'
                        conn.sendall(message.encode("utf-8"))
                    else:
                        conn.sendall(b'''usage: - e: execute the path from the beginning
       - number: go to specified viewpoint
       - v [value]: change the velocity to specified value
       - load [pathname]: load path with specified path name
       - q: quit the program''')
                else:
                    conn.sendall(b'NO path is loaded, please load a path first')
            conn.close()
        s.close()

    return
    
if __name__ == '__main__':

    # create move group instance
    move_group = MoveGroup()
    # get default endeffector of the movegroup
    end_effector = move_group.get_end_effector()
                        
    loop = asyncio.get_event_loop()
    register_asyncio_shutdown_handler(loop)
    

    try:
        loop.run_until_complete(move_path(move_group))
    finally:
        loop.close()