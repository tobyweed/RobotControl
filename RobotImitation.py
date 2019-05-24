import asyncio
import pickle 
from pyquaternion import Quaternion
from xamla_motion.data_types import CartesianPath, JointPath, Pose
from xamla_motion.motion_client import EndEffector, MoveGroup
from xamla_motion.utility import register_asyncio_shutdown_handler

# functions for supervised executation


# async def next(stepped_motion_client):
#     while True:
#         await asyncio.sleep(0.1)
#         if stepped_motion_client.state:
#             stepped_motion_client.step()
#             print('progress {:5.2f} percent'.format(
#                 stepped_motion_client.state.progress))


# async def run_supervised(stepped_motion_client):
#     print('start supervised execution')

#     task_next = asyncio.ensure_future(next(stepped_motion_client))

#     await stepped_motion_client.action_done_future
#     task_next.cancel()

#     print('finished supervised execution')


def main():
    # create move group instance
    move_group = MoveGroup()
    # get default endeffector of the movegroup
    end_effector = move_group.get_end_effector()

    
    input("Move Robot to desired starting point, and press Enter to continue...")
    startingPoint = move_group.get_current_joint_positions();
    newPath = JointPath.from_one_point(startingPoint)
    # print(newPath);

    while True:
        inst = input("Move Robot to next desired position, and press Enter to continue...\nOtherwise, enter 'end' to set the ending point\n")
        newPath = newPath.append(move_group.get_current_joint_positions())
        # print(newPath)
        if inst == 'end':
            break

    loop = asyncio.get_event_loop()
    register_asyncio_shutdown_handler(loop)

    velocity = input("enter desired velocity (float point number range 0-1):")

    async def example_moves():
        input("press enter to imitate the path with velocity " + velocity)
        print('--- Imitating the Path ---')
        await move_group.move_joints_collision_free(newPath, velocity_scaling = velocity)


    try:
        loop.run_until_complete(example_moves())
    finally:
        loop.close()
        print("Finished")


if __name__ == '__main__':
    main()