import asyncio
import sys

from pyquaternion import Quaternion
from xamla_motion.data_types import CartesianPath, JointPath, Pose
from xamla_motion.v2.motion_client import EndEffector, MoveGroup
from xamla_motion.utility import register_asyncio_shutdown_handler
from xamla_motion import MoveJointsCollisionFreeOperation, MoveCartesianCollisionFreeOperation
import pickle
import numpy as np

def data_to_joint_path(end_effector,reference,data):

    path = []
    
    for pose in data:
        coordinate = pose[:3]
        coordinate[0], coordinate[1],coordinate[2] = coordinate[2], coordinate[0], coordinate[1]
        coordinate = np.array(coordinate) + reference.translation
        quat_element = pose[3:7]
        quat = Quaternion(quat_element[0], quat_element[3], quat_element[1], quat_element[2])
        quat = quat * reference.quaternion
        pose = Pose(coordinate,quat)
        path.append(pose)
    
    cartesian_path = CartesianPath(path)
    joint_path = end_effector.inverse_kinematics_many(cartesian_path,False).path
    return joint_path 

def main():

    # create move group instance
    move_group = MoveGroup()
    # get default endeffector of the movegroup
    end_effector = move_group.get_end_effector()
    
    if(len(sys.argv)==2):
        try:
            file_path = open('%s'%sys.argv[1], 'rb')
        except:
            print("file does not exist!")
        else:
            data = pickle.load(file_path)
            reference = end_effector.get_current_pose()
            data_joint_path = data_to_joint_path(end_effector,reference,data)
            loop = asyncio.get_event_loop()
            register_asyncio_shutdown_handler(loop)

            async def new_trajectory(data):
                data_joint_path = data
                num_points = len(data_joint_path.points)
                start_point = None
                start_index = 0
                end_point = None
                end_index = num_points -1
                views = []
                num_views = 0
                while 1:
                    command = input("Enter command:")
                    if command == "t":
                        print('--- start test run of trajectory from start point to end point ---')
                        move_joints = move_group.move_joints(JointPath(data_joint_path.joint_set,data_joint_path.points[start_index:end_index+1]))
                        move_joints = move_joints.with_velocity_scaling(0.1)
                        await move_joints.plan().execute_async()
                    elif len(command.split())==2 and command.split()[0] == "t" and command.split()[1].isdigit() and int(command.split()[1]) < num_points:
                        index = int(command.split()[1])
                        print('--- moving to point with index number %d'%index)
                        move_joints_cf = move_group.move_joints_collision_free(data_joint_path.points[index], velocity_scaling = 0.2)
                        await move_joints_cf.plan().execute_async()
                    elif command == "e" and start_point and end_point and num_views > 0:
                        print("--- moving to the start point ---")
                        move_joints_cf = move_group.move_joints_collision_free(start_point, velocity_scaling = 0.2)
                        await move_joints_cf.plan().execute_async()
                        print('start test run')
                        temp_path = JointPath(start_point.joint_set,views).append(end_point)
                        move_joints_cf = move_group.move_joints_collision_free(temp_path)
                        move_joints_cf = move_joints_cf.with_velocity_scaling(0.1)
                        await move_joints_cf.plan().execute_async()
                        print('test run finished')
                    elif command.isdigit():
                        num = int(command)
                        if num < num_views:
                            print('--- Going to Viewpoint %d---' %num)
                            move_joints_cf = move_group.move_joints_collision_free(views[num], velocity_scaling = 0.2)
                            await move_joints_cf.plan().execute_async()
                        else:
                            print('There are %d viewpoints, please enter a valid number' %num_views)
                    elif command == 'start':
                        print("--- moving to the start point ---")
                        move_joints_cf = move_group.move_joints_collision_free(start_point, velocity_scaling = 0.2)
                        await move_joints_cf.plan().execute_async()
                    elif command == 'end':
                        print("--- moving to the end point ---")
                        move_joints_cf = move_group.move_joints_collision_free(end_point, velocity_scaling = 0.2)
                        await move_joints_cf.plan().execute_async()
                    elif command == 's':
                        name = input("Enter the name of the path: ")
                        file_path = open('paths/%s.obj'%name, 'wb')
                        new_path = {'start':start_point, 'end':end_point,'path':JointPath(start_point.joint_set,views),
                            'traj':JointPath(data_joint_path.joint_set,data_joint_path.points[start_index:end_index+1])}
                        pickle.dump(new_path, file_path)
                        print('saved as %s.obj'%name)
                        break
                    elif len(command.split())==2 and command.split()[0] == "add" and command.split()[1].isdigit() and int(command.split()[1]) < num_points:
                        index = int(command.split()[1])
                        pose = data_joint_path.points[index]
                        num_views += 1
                        views.append(pose)
                        print("Add point with index %d as Viewpoint %d" %(index,num_views-1))
                    elif len(command.split())==3 and command.split()[0] == "set" and command.split()[2].isdigit() and int(command.split()[2]) < num_points:
                        index = int(command.split()[2])
                        pose = data_joint_path.points[index]
                        if(command.split()[1].isdigit() and int(command.split()[1]) < num_views):
                            views[int(command.split()[1])] = pose
                            print("Set Viewpoint %d to point with index %d"%(int(command.split()[1]),index))
                        elif command.split()[1] == "start":
                            if(index < end_index):
                                start_point = pose
                                start_index = index
                                print("Set start point to point with index %d"%index)
                            else:
                                print("Start point must be before end point ")
                        elif command.split()[1] == "end":
                            if(index > start_index):
                                end_point = pose
                                end_index = index
                                print("Set end point to point with index %d"%index)
                            else:
                                print("End point must be after start point ")
                        else:
                            print("invalid parameter")
                    elif command == 'd':
                        break
                    else:
                        print("""usage: - e: execute a test run of path
                - number: go to specified viewpoint
                - start: go to start point
                - end: go to end point
                - set [number | start | end] [index_num]: Set the specified viewpoint to the pose of index number
                - save: save the path to local directory
                - d: discard the path""")

            try:
                loop.run_until_complete(new_trajectory(data_joint_path))
            finally:
                loop.close()


if __name__ == '__main__':
    main()