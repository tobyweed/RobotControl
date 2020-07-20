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

async def test_run(move_group,path,view_num):

    new_path = path

    while 1:
        command = input("Enter command:")
        if command == "e":
            print("--- moving to the start point ---")
            move_joints_cf = move_group.move_joints_collision_free(new_path['joint_values'][0], velocity_scaling = 0.2)
            await move_joints_cf.plan().execute_async()
            print('start test run')
            temp_path = new_path['joint_values']
            move_joints_cf = move_group.move_joints_collision_free(temp_path)
            move_joints_cf = move_joints_cf.with_velocity_scaling(0.2)
            await move_joints_cf.plan().execute_async()
            print('test run finished')
        elif command.isdigit():
            num = int(command)
            if num < int(view_num):
                view_points = new_path['joint_values']
                print('--- Going to Viewpoint %d---' %num)
                move_joints_cf = move_group.move_joints_collision_free(view_points[num], velocity_scaling = 0.2)
                await move_joints_cf.plan().execute_async()
            else:
                print('There are %s viewpoints, please enter a valid number' %view_num)
        elif command == 's':
            name = input("Enter the name of the path: ")
            if not name:
                name = "default"
            file_path = open('paths/%s.obj'%name, 'wb') 
            pickle.dump(new_path, file_path)
            print('saved as %s.obj'%name)
            break
        elif len(command.split())==2 and command.split()[0] == "r":
            if(command.split()[1].isdigit() and int(command.split()[1]) < int(view_num)):
                temp_path = list(new_path['path'].points)
                temp_path[int(command.split()[1])] = move_group.get_current_joint_positions()
                new_path = {'start':new_path['start'], 'end':new_path['end'],'path':JointPath(new_path['start'].joint_set,temp_path)}
                print("Reset Viewpoint %s to current position"%command.split()[1])
            elif command.split()[1] == "start":
                new_start_point = move_group.get_current_joint_positions()
                new_path = {'start':new_start_point, 'end':new_path['end'],'path':new_path['path']}
                print("Reset start point to current position")
            elif command.split()[1] == "end":
                new_end_point = move_group.get_current_joint_positions()
                new_path = {'start':new_path['start'], 'end':new_end_point,'path':new_path['path']}
                print("Reset end point to current position")
            else:
                print("invalid parameter")
        elif command == 'd':
            break
        else:
            print("""usage: - e: execute a test run of path
       - number: go to specified viewpoint
       - s: save the path to local directory
       - d: discard the path""")

def new_path(move_group, end_effector,view_num):
    joint_values = []
    poses = []
    for i in range(int(view_num)):
        inst = input("Move Robot to viewpoint %d, and press Enter to continue..." %i)
        poses.append(end_effector.get_current_pose())
        joint_values.append(move_group.get_current_joint_positions())
    
    path = {'poses':CartesianPath(poses), 'joint_values':JointPath(joint_values[0].joint_set, joint_values)}
    print("successfully created the new path")

    return path

if __name__ == '__main__':

    # create move group instance
    move_group = MoveGroup()
    # get default endeffector of the movegroup
    end_effector = move_group.get_end_effector()

    view_num = input("Enter the number of view points for the new path:")

    path = new_path(move_group, end_effector, view_num)

    loop = asyncio.get_event_loop()
    register_asyncio_shutdown_handler(loop)
    try:
        loop.run_until_complete(test_run(move_group,path,view_num))
    finally:
        loop.close()

