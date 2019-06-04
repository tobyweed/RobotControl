#!/usr/bin/env python3

import asyncio
import pickle
import sys
import time
from pyquaternion import Quaternion
from xamla_motion.data_types import CartesianPath, JointPath, Pose, JointValues
from xamla_motion.motion_client import EndEffector, MoveGroup
from xamla_motion.utility import register_asyncio_shutdown_handler
import socket

HOST = ''  # Standard loopback interface address (localhost)
PORT = 50001        # Port to listen on (non-privileged ports are > 1023)


def newPath(move_group):
    i = 0;
    new_path = []
    while True:
        time.sleep(0.5)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                command = data.decode("utf-8")
                if command == 'end':
                    new_path = JointPath(new_path[0].joint_set,new_path)
                    conn.sendall(b"path successfully created, now enter your command")
                else:
                    new_path.append(move_group.get_current_joint_positions())
                    i+=1
                    conn.sendall(b"Move Robot Arm to viewpoint %d, and press Enter to continue..." %i)
            conn.close()
        s.close()
        if command == 'end':
            return new_path

async def joint_moves(move_group,path):
    velocity = 0.05
    quit = False
    while True:
        time.sleep(0.5)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            conn, addr = s.accept()
            with conn:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    instruction = data.decode("utf-8")
                    if instruction.isdigit():
                        view_points = path.points
                        num = int(instruction)
                        if num < len(view_points):
                            print('--- Going to Viewpoint %d---' %num)
                            await move_group.move_joints_collision_free(view_points[num], velocity_scaling = velocity)
                            conn.sendall(b'success')
                        else:
                            conn.sendall(b'There are %d viewpoints, please enter a valid number' %len(view_points))
                    elif instruction == "e":
                        print("--- moving to the first viewpoint ---")
                        await move_group.move_joints_collision_free(path.points[0], velocity_scaling = velocity)
                        print("--- executing the path ---")
                        await move_group.move_joints(path, velocity_scaling = velocity)
                        print("--- Finished ---")
                        conn.sendall(b'success')
                    elif instruction == "q":
                        quit = True
                        conn.sendall(b'bye')
                    else:
                        split = instruction.split(' ')
                        if len(split)==2 and split[0]=='v':
                            new_velocity = float(split[1])
                            if new_velocity>0 and new_velocity<=1:
                                velocity = str(new_velocity)
                                message = 'Successfully set velocity to '+velocity
                                conn.sendall(message.encode("utf-8"))
                            else:
                                conn.sendall(b'please enter a valid number, 0-1')
                        elif len(split)==2 and split[0]=='s':
                            name = split[1]
                            file_path = open('%s.obj'%name, 'wb') 
                            pickle.dump(path, file_path)
                            message = 'Successfully saved path as %s'%name
                            conn.sendall(message.encode("utf-8"))
                        else:
                            conn.sendall(b"""usage: - e: execute the path from the beginning
       - number: go to specified viewpoint
       - v: change the velocity
       - s: save the path to local directory
       - q: quit the program""")
        if quit:
            return
    
if __name__ == '__main__':

    # create move group instance
    move_group = MoveGroup()
    # get default endeffector of the movegroup
    end_effector = move_group.get_end_effector()

    pathName = ''
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print(s.gettimeout())
    print('waiting for connection')
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while 1:
            data = conn.recv(1024)
            if not data:
                break
            pathName = data.decode("utf-8")
            if pathName == 'new':
                conn.sendall(b'Move Robot Arm to viewpoint 0, and press Enter to continue...')
            else:
                try:
                    file_path = open(pathName, 'rb') 
                except:
                    message = 'An error occurs while loading %s'%pathName
                    conn.sendall(message.encode("utf-8"))
                    exit()
                else:
                    message = 'Sucessfully loaded %s'%pathName
                    conn.sendall(message.encode("utf-8"))
                    path = pickle.load(file_path)
        conn.close()
    s.close()

    if pathName == 'new':
        path = newPath(move_group)
                        
    loop = asyncio.get_event_loop()
    register_asyncio_shutdown_handler(loop)
    

    try:
        loop.run_until_complete(joint_moves(move_group,path))
        # loop.run_until_complete(cartesian_moves(move_group,path))
    finally:
        loop.close()