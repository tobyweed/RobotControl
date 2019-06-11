import asyncio
import pickle
import sys
from pyquaternion import Quaternion
from xamla_motion.data_types import CartesianPath, JointPath, Pose, JointValues
from xamla_motion.v2.motion_client import EndEffector, MoveGroup
from xamla_motion.utility import register_asyncio_shutdown_handler

#functions for supervised executation


async def next(stepped_motion_client):
    while True:
        await asyncio.sleep(0.1)
        if stepped_motion_client.state:
            stepped_motion_client.step()
            print('progress {:5.2f} percent'.format(
                stepped_motion_client.state.progress))


async def run_supervised(stepped_motion_client):
    print('start supervised execution')

    task_next = asyncio.ensure_future(next(stepped_motion_client))

    await stepped_motion_client.action_done_future
    task_next.cancel()

    print('finished supervised execution')

def new_trajectory_joint_values(move_group):
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

def new_trajectory_cartesian_path(move_group):
    
    # get default endeffector of the movegroup
    end_effector = move_group.get_end_effector()
    i = 0;
    input("Move Robot Arm to viewpoint %d, and press Enter to continue..." %i)
    startingPoint = end_effector.get_current_pose()
    newPath = [startingPoint]
    while True:
        i += 1
        inst = input("Move Robot to viewpoint %d, and press Enter to continue...\nOtherwise, enter 'end' to finish\n" %i)
        if inst == 'end':
            break
        newPath.append(end_effector.get_current_pose())
    cartesian_path = CartesianPath(newPath)

    return cartesian_path

async def joint_moves(move_group,path):
    velocity = input("enter desired velocity (float point number range 0-1):")
    while True:
        instruction = input("Enter Command: ")
        if instruction.isdigit():
            view_points = path.points
            num = int(instruction)
            if num <= len(view_points):
                print('--- Going to Viewpoint %d---' %num)
                move_joints_cf = move_group.move_joints_collision_free(view_points[num], velocity_scaling = velocity)
                await move_joints_cf.plan().execute_async()
            else:
                print('There are %d viewpoints, please enter a valid number' %len(view_points))
        elif instruction == "e":
            print("--- moving to the first viewpoint ---")
            move_joints_cf = move_group.move_joints_collision_free(path.points[0], velocity_scaling = velocity)
            await move_joints_cf.plan().execute_async()
            print("--- executing the path ---")
            move_joints = move_group.move_joints(path, velocity_scaling = velocity)
            await move_joints.plan().execute_async()
            print("--- Finished ---")
        elif instruction == "v":
            new_velocity = float(input('current velocity is: %s, enter new velocity (float point number range 0-1):' %velocity))
            if new_velocity>0 and new_velocity<=1:
                velocity = str(new_velocity)
            else:
                print('please enter a valid number')
        elif instruction == "s":
            name = input("Enter the name of the path: ")
            file_path = open('%s.obj'%name, 'wb') 
            pickle.dump(path, file_path)
            print('saved as %s.obj\n'%name)
        elif instruction == "q":
            break
        else:
            print("""usage: - e: execute the path from the beginning
       - number: go to specified viewpoint
       - v: change the velocity
       - s: save the path to local directory
       - q: quit the program""")

    
async def cartesian_moves(move_group,path):
    # get default endeffector of the movegroup
    end_effector = move_group.get_end_effector()
    velocity = input("enter desired velocity (float point number range 0-1):")
    while True:
        instruction = input("Enter Command: ")
        if instruction.isdigit():
            view_points = path.points
            num = int(instruction)
            if num <= len(view_points):
                print('--- Going to Viewpoint %d---' %num)
                move_poses_cf = end_effector.move_cartesian_collision_free(path.points[num], velocity_scaling = velocity)
                await move_poses_cf.plan().execute_async()
            else:
                print('There are %d viewpoints, please enter a valid number' %len(view_points))
        elif instruction == "e":
            print("--- moving to the first viewpoint ---")
            move_poses_cf = end_effector.move_cartesian_collision_free(path.points[0], velocity_scaling = velocity)
            await move_poses_cf.plan().execute_async()
            print("--- executing the path ---")
            move_poses = end_effector.move_cartesian(path, velocity_scaling = velocity)
            await move_poses.plan().execute_async()
            print("--- Finished ---")
        elif instruction == "v":
            new_velocity = float(input('current velocity is: %s, enter new velocity (float point number range 0-1):' %velocity))
            if new_velocity>0 and new_velocity<=1:
                velocity = str(new_velocity)
            else:
                print('please enter a valid number')
        elif instruction == "s":
            name = input("Enter the name of the path: ")
            file_path = open('%s.obj'%name, 'wb') 
            pickle.dump(path, file_path)
            print('saved as %s.obj\n'%name)
        elif instruction == "q":
            break
        else:
            print("""usage: - e: execute the path from the beginning
       - number: go to specified viewpoint
       - v: change the velocity
       - s: save the path to local directory
       - q: quit the program""")

if __name__ == '__main__':


    if len(sys.argv) != 1 and len(sys.argv) != 2:
        print("""usage: python3 RobotImitation.py [pathname]
        - without pathname: create a new path
        - with pathname: load the path with specified pathname""")    
        exit()
    
    # create move group instance
    move_group = MoveGroup()
    # get default endeffector of the movegroup
    end_effector = move_group.get_end_effector()

    if len(sys.argv) == 1:
        path = new_trajectory_joint_values(move_group)
        # path = new_trajectory_cartesian_path(move_group)
        # path = end_effector.inverse_kinematics_many(cartesian_path,True,attempts=5).path

    if len(sys.argv) == 2:
        name = sys.argv[1]
        try:
            file_path = open('%s.obj'%name, 'rb') 
        except:
            print('An error occurs while loading %s.obj'%name)
            exit()
        else:
            print('Sucessfully loaded %s.obj'%name)
            path = pickle.load(file_path)


    loop = asyncio.get_event_loop()
    register_asyncio_shutdown_handler(loop)

    try:
        loop.run_until_complete(joint_moves(move_group,path))
        # loop.run_until_complete(cartesian_moves(move_group,path))
    finally:
        loop.close()
