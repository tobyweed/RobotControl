# MLRobotControl.py
# A socket server which communicates with MobileLingting to execute saved paths
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
import simplejson as json

HOST = ''
PORT = 65000       # Port to listen on (non-privileged ports are > 1023)

async def start_server(move_group):
    velocity = 0.2
    running = True
    path = ''
    file_path = open("./paths/default.obj", 'rb')
    path = pickle.load(file_path)
    views = path['path']
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    s.settimeout(None)
    print("--- MLRobotControl server started ---")
    while running:
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
                    pathName = splitins[1]
                    
                    try:
                        file_path = open('paths/'+pathName, 'rb') 
                    except:
                        message = 'An error occurs while loading %s'%pathName
                        conn.sendall(message.encode("utf-8"))
                    else:
                        path = pickle.load(file_path)
                        views = path['path']
                        print(path)
                        print(views)
                        # num_views = len(views.points)
                        # message = str(num_views)
                        message = json.dumps(views, iterable_as_array=True)
                        conn.sendall(message.encode("utf-8"))
                        # conn.sendall(message.encode("utf-8"))
                elif instruction == "q":
                    running = False
                    conn.sendall(b'bye')
                elif path:
                    if instruction.isdigit():
                        view_points = views.points
                        num = int(instruction)
                        if num < len(view_points):
                            print('--- Going to Viewpoint %d---' %num)
                            move_joints_cf = move_group.move_joints_collision_free(view_points[num], velocity_scaling = velocity)
                            await move_joints_cf.plan().execute_async()
                            conn.sendall(b'success')
                        else:
                            conn.sendall(b'There are %d viewpoints, please enter a valid number' %len(view_points))
                    elif instruction == "e":
                        print("--- moving to the starting point ---")
                        move_joints_cf = move_group.move_joints_collision_free(path['start'], velocity_scaling = 0.4)
                        await move_joints_cf.plan().execute_async()
                        print("--- executing the path ---")
                        temp_path = views.append(path['end']).prepend(path['start'])
                        move_joints = move_group.move_joints(temp_path, velocity_scaling = velocity)
                        await move_joints.plan().execute_async()
                        print("--- Finished ---")
                        conn.sendall(b'success')
                    elif instruction == "s":
                        print("--- moving to the starting point ---")
                        move_joints_cf = move_group.move_joints_collision_free(path['start'], velocity_scaling = velocity)
                        await move_joints_cf.plan().execute_async()
                        conn.sendall(b'success')
                    elif instruction == "t":
                        if 'traj' in path:
                            print("--- moving to the starting point ---")
                            move_joints_cf = move_group.move_joints_collision_free(path['start'], velocity_scaling = 0.4)
                            await move_joints_cf.plan().execute_async()
                            print("--- executing the recorded trajectory ---")
                            move_joints = move_group.move_joints(path['traj'], velocity_scaling = velocity)
                            await move_joints.plan().execute_async()
                            print("--- Finished ---")
                            conn.sendall(b'success')
                        else:
                            conn.sendall(b'The loaded path does not have a SteamVR trajectory')
                    elif len(splitins)==2 and splitins[0]=='v':
                        new_velocity = float(splitins[1])
                        if new_velocity>0 and new_velocity<=1:
                            velocity = str(new_velocity)
                            message = 'Successfully set velocity to '+velocity
                            conn.sendall(message.encode("utf-8"))
                        else:
                            conn.sendall(b'please enter a valid number, 0-1')
                            
                    # the rotation function only works for the old path structure
                    # also the repeatability of robot arm after rotation was not tested
                    # so I commented out this part of the code
                    # elif len(splitins)==2 and splitins[0]=='r':
                    #     degree = float(splitins[1])
                    #     radian = degree/180 * math.pi
                    #     path = JointPath(path.joint_set,[x.set_values(path.joint_set,x.values+np.array([-radian,0,0,0,0,0])) for x in path.points])
                    #     message = 'Successfully rotate path to the right by '+ str(degree) + ' degrees'
                    #     conn.sendall(message.encode("utf-8"))
                    # elif len(splitins)==2 and splitins[0]=='l':
                    #     degree = float(splitins[1])
                    #     radian = degree/180 * math.pi
                    #     path = JointPath(path.joint_set,[x.set_values(path.joint_set,x.values+np.array([radian,0,0,0,0,0])) for x in path.points])
                    #     message = 'Successfully rotate path to the left by '+ str(degree) + ' degrees'
                    #     conn.sendall(message.encode("utf-8"))
                    else:
                        conn.sendall(b'''usage: - e: execute the path from the start point
       - l: execute the recorded trajectory of SteamVR if there is one
       - number: go to specified viewpoint
       - v [value]: change the velocity to specified value
       - load [pathname]: load path with specified path name
       - s: go to the start point of video
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
        loop.run_until_complete(start_server(move_group))
    finally:
        loop.close()
