# NewPath.py
# A program that creates a new path and saves to local directory
# 2019 Middlebury College Summer Research with Professor Scharstein
# Guanghan Pan

#!/usr/bin/env python3

import asyncio
import pickle
import sys
from pyquaternion import Quaternion
from xamla_motion.data_types import CartesianPath, JointPath, Pose, JointValues
from xamla_motion.v2.motion_client import EndEffector, MoveGroup
from xamla_motion.utility import register_asyncio_shutdown_handler

async def test_run(move_group,path):
    while 1:
        input("press enter to start the test run")
        print("--- moving to the first viewpoint ---")
        move_joints_cf = move_group.move_joints_collision_free(path.points[0], velocity_scaling = 0.1)
        await move_joints_cf.plan().execute_async()
        print('start test run')
        move_joints_cf = move_group.move_joints_collision_free(path)
        move_joints_cf = move_joints_cf.with_velocity_scaling(0.05)
        await move_joints_cf.plan().execute_async()
        print('test run finished')


        command = input("Enter 's' to save to local directory,'d' to discard the path, otherwise rerun the test run:")
        if command == 's':
            name = input("Enter the name of the path: ")
            file_path = open('paths/%s.obj'%name, 'wb') 
            pickle.dump(path, file_path)
            print('saved as %s.obj'%name)
            break
        elif command == 'd':
            break
        else:
            pass

def new_path_joint_values(move_group):
    i = 0;
    input("Move Robot Arm to viewpoint %d, and press Enter to continue..." %i)
    startingPoint = move_group.get_current_joint_positions();
    newPath = JointPath.from_one_point(startingPoint)
    while True:
        i += 1
        inst = input("Move Robot to viewpoint %d, and press Enter to continue...\nOtherwise, enter 'end' to finish\n" %i)
        if inst == 'end':
            break
        newPath = newPath.append(move_group.get_current_joint_positions())

    return newPath

if __name__ == '__main__':

    # create move group instance
    move_group = MoveGroup()
    # get default endeffector of the movegroup
    end_effector = move_group.get_end_effector()
    path = new_path_joint_values(move_group)


    loop = asyncio.get_event_loop()
    register_asyncio_shutdown_handler(loop)
    try:
        loop.run_until_complete(test_run(move_group,path))
        # loop.run_until_complete(cartesian_moves(move_group,path))
    finally:
        loop.close()

