import asyncio
import pickle 
from pyquaternion import Quaternion
from xamla_motion.data_types import CartesianPath, JointPath, Pose, JointValues
from xamla_motion.motion_client import EndEffector, MoveGroup
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
    i = 1;
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

async def example_moves(move_group,path):
    velocity = input("enter desired velocity (float point number range 0-1):")
    while True:
        instruction = input("Enter Command: ")
        if instruction.isdigit():
            view_points = path.points
            num = int(instruction)
            if num <= len(view_points):
                print('--- Going to Viewpoint %d---' %num)
                await move_group.move_joints(path.points[num-1], velocity_scaling = velocity)
            else:
                print('There are %d viewpoints, please enter a valid number' %len(view_points))
        elif instruction == "e":
            await move_group.move_joints(path, velocity_scaling = velocity)
        elif instruction == "v":
            new_velocity = input('current velocity is: %d, enter new velocity (float point number range 0-1):' %velocity)
            if new_velocity>0 and new_velocity<=1:
                velocity = new_velocity
            else:
                print('please enter a valid number')
        elif instruction == "s":
            name = input("Enter the name of the path you want to save: ")
            file_path = open('%s.obj'%name, 'wb') 
            pickle.dump(path, file_path)
        elif instruction == "q":
            break

def main():
    # create move group instance
    move_group = MoveGroup()
    # get default endeffector of the movegroup
    end_effector = move_group.get_end_effector()

    joint_set = move_group.get_current_joint_states().joint_set;
    position1 = JointValues(joint_set,[
    0.6314885020256042,
    -1.9915106932269495,
    -2.6588473955737513,
    1.2166744470596313,
    -0.09501058260072881,
    1.9019759893417358
    ])
    position2 = JointValues(joint_set,[
    -0.45846635500063115,
    -2.0101736227618616,
    -2.0828221479998987,
    0.7453490495681763,
    1.5895854234695435,
    1.644828200340271
    ])
    position3 = JointValues(joint_set,[
    -0.3339021841632288,
    -2.3484495321856897,
    -1.211771313344137,
    0.16919183731079102,
    1.9967894554138184,
    1.475343108177185
    ])
    example_path = JointPath(joint_set,[position1,position2,position3])

    loop = asyncio.get_event_loop()
    register_asyncio_shutdown_handler(loop)

    #new_joint_path = new_trajectory_joint_values(move_group)
    try:
        file_path = open('foo.obj', 'rb') 
    except:
        print('error')
        load_path=example_path
    else:
        load_path = pickle.load(file_path)

    try:
        loop.run_until_complete(example_moves(move_group,load_path))
    finally:
        loop.close()
        print("Finished")


if __name__ == '__main__':
    main()