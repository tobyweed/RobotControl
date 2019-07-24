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

HOST = ''  # Standard loopback interface address (localhost)
PORT = 65431        # Port to listen on (non-privileged ports are > 1023)


async def imitate_move(end_effector,move_group):
    input("Press enter to start")
    start = end_effector.get_current_pose()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn = None
            try:
                conn, addr = s.accept()
                with conn:  
                    print('Connected by', addr)
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        
                        pose_list = eval(data.decode("utf-8"))
                        # print(pose_list)
                        path = []
                        for pose in pose_list:
                            coordinate = pose[:3]
                            coordinate[0], coordinate[1],coordinate[2] = coordinate[2], coordinate[0], coordinate[1]
                            coordinate = np.array(coordinate) + start.translation
                            quat_element = pose[3:7]
                            quat = Quaternion(quat_element[0], quat_element[3], quat_element[1], quat_element[2])
                            quat = quat * start.quaternion
                            pose = Pose(coordinate,quat)
                            path.append(pose)

                        cartesian_path = CartesianPath(path)
                        joint_path = end_effector.inverse_kinematics_many(cartesian_path,False).path
                        move_joints = move_group.move_joints(joint_path)
                        move_joints = move_joints.with_velocity_scaling(0.1)
                        move_joints_plan = move_joints.plan()
                        await move_joints_plan.execute_async()
            
            except KeyboardInterrupt:
                if conn:
                    conn.close()
                break

if __name__ == '__main__':

    # create move group instance
    move_group = MoveGroup()
    # get default endeffector of the movegroup
    end_effector = move_group.get_end_effector()
                        
    loop = asyncio.get_event_loop()
    register_asyncio_shutdown_handler(loop)
    
    try:
        loop.run_until_complete(imitate_move(end_effector, move_group))
    finally:
        loop.close()