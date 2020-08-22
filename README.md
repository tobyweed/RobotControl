# Robot Control with Rosvita
The goal of this project is to control UR5 robot arm to specified viewpoints through Rosvita using a socket server written in python, MLRobotControl.py, which could communicates with a C++ socket program that is incorporated into the main MobileLighting program. This repository also includes the scripts which are useful to record and process the trajectories recorded using HTC VIVE tracker. All these python scripts are designed for Rosvita and only works on the terminal of Rosvita user interface.

## Getting Started

These instructions will illustrate how to start Rosvita, load the project, and communicate with both robot arm and main program in order to execute the python scripts. These instructions are adapted from [Xamla Documentation](https://github.com/Xamla/docs.xamla.com), a private GitHub repository which could only be accessed using permitted account.

### Connecting Rosvita to UR5 Robot Arm

1. On the ubuntu machine where Rosvita is installed, open the terminal and run the start script by simply typing:

  ```
  rosvita_start
  ```

  As a result, the Rosvita login screen will appear in your default web. After successful login with username and password (the default login credential are u: **admin**, p: **r2d2c3po**), the main development environment opens.

  To stop Rosvita, simply run the stop script:
  ```
  rosvita_stop
  ```

1. In order to control the robot arm from Rosvita, you must first open a project. If using the same laptop I was using, you could simply open the project I created (*ur5_test*). After getting to the main development environment, by clicking on the Xamla icon in the upper-left corner, a selection bar appears, in which you could select the menu item **Open Project**. You can also just click on the **Open Project** directly in the middle of the start screen, select ur5_test and then click on the open button. The project will be loaded and its name will appear on the top header.  Alternatively, you can also create a new project by clicking on **New Project**. Then, a text box will appear in which you can enter the desired project name.

1. After loading the project, the next step is to create a robot configuration. When clicking on the Xamla icon in the top left corner and selecting the menu item **Configuration**, a new window for robot configuration will appear in the middle. In the left menu bar, make sure that under the RobotPart menu item, it contains the **ur5_xamla_cap**, and under the actuator menu item contains the corresponding actuator **Robot Arm UR**. If not, you could add the items on the right-hand side of browser.

1. In the Properties menu of the Actuator(**Robot Arm UR**), you can find a **simulate** checkmark. If setting this checkmark to true, then all the instructions and scripts will control the robot arm in simulation mode. If you want to configure a real robot, you have to remove this checkmark and enter the IP address of the robot. The IP address of the robot can be found under the **Network** tab of the robot panel. (default value is: **192.168.1.2** if using the Netgear router)

1. To compile an existing configuration, press the **Compile** button at the top bar of the Configuration View. In the output terminal at the bottom, a message indicating the sucess will appear. In addition, the message **not configured** next to the warning triangle on the top right is replaced by the message **ROS core stopped**.

1. Now, you can start ROS by pressing the button **Start ROS** in the top bar. If everything works fine, after a few seconds, a green **GO** replaces the warning message on the top right. Rosvita is then successfully connect to the robot arm. (**Note**: If instead the message Heartbeat failure appears next to the warning triangle and stays there for more than a few seconds, it is most likely that the IP address provided in the configuration is wrong, or the robot arm and the laptop running Rosvita are connected to different networks.)

### Connecting MobileLighting to Rosvita

The main application, MobileLighting Mac, communicates with MLRobotControl via a wireless socket. To establish a successful connection, both the mac running MobileLighting and the ubuntu laptop should connect to the same network. In addition, the IP address, which is currently hardcoded in LoadPath_client.cpp,  should match the IP address of the ubuntu laptop. (default value is: **192.168.1.102** if using the Netgear router)

### Installing the program

You simply need to clone this repository to your local directory of the project in the terminal of Rosvita. No further installations are required. Now you are ready to run the program.

## Running the program

### The MLRobotControl server

To run the MLRobotControl server, simply navigate to the RobotControl folder. In the Rosvita terminal, type the following command:

```
python3 MLRobotControl.py
```

When the message "MLRobotControl server started" is printed in the terminal, the server has been run successfully, and is ready to listen to commands from MobileLighting.

If this command causes an `OSError: [Errno 98] Address already in use`, it's most likely that the default port (60000) for **MLRobotControl** is already occupied by a previous instance of the server. In this case, run the following commands from Terminal (_not_ from the Rosvita web IDE):
 * Locate the process running on 60000 with `lsof -i -n -P | grep TCP`
 * Kill it with `kill -9 <PID>` where PID is the PID indicated in the output of the pior command (should be a 3-5 digit number in the second column of the output, something like `29290`.
 
If running the program causes the error `No module named simplejson`, the Rosvita IDE has for some reason reset what software is downloaded. Fix this by running `sudo easy_install simplejson`

#### Local test client

After the server is running, you could also communicate with the server locally by running the following command(either on the ubuntu terminal or on the Rosvita terminal):

```
python3 test_client.py
```

the program would prompt "Enter command: " and you can enter different commands to send to the server.

Below is a list of all commands that could be understood by server:

- e: execute the path from the start point
- l: execute the recorded trajectory of SteamVR if there is one
- number: go to specified viewpoint
- v [value]: change the velocity scaling to specified value (value range: 0-1)
- load [pathname]: load path with specified path name
- s: go to the start point of video
- q: quit the program

#### Quit the server

There are two ways to stop the server from running. The easiest way is to send a "q" command to the server from the local client. Alternatively, hit "Control+Z", then enter "ps a" in the Rosvita terminal, looking for the id of the server, then enter "kill -9 [id]". Both ways will quit the program so that the PORT will not be occupied.

### Defining a new path

There are two ways to define a new path. The first method is using NewPath.py to define a path locally in Rosvita without a realistic human motion. The second method is to record a realistic human motion using HTC VIVE tracker, and then select several viewpoints in between the movement.

#### Without realistic human motion
In order to define a new path locally with specified number of viewpoints, type the following command in Rosvita terminal:

```
python3 NewPath.py
```

The program will prompt you to enter number of viewpoints. Afterwards, the program will ask you to move the robot to different places (start point, viewpoints, and end point). After moving the robot to the desired place (either using free drive mode on the robot panel, or moving the robot through Rosvita), hit "Enter". The program will then record the **Joint Positions** of the current position of the robot arm, and save them in a list. When all the positions are defined, the program would prompt "Enter command: " and you can enter different commands to examine the path, change the path, and finally save it to local directory.

Below is a list of all commands included in the program NewPath.py and their explanations:
- e: execute a test run of path
- number: go to specified viewpoint
- start: go to start point
- end: go to end point
- r [number | start | end]: reset the specified viewpoint to current position
- s: save the path to local directory
- d: discard the path

After saving the path to local directory, it will ask you to enter a name for the path. Then, the path should be ready to be loaded by the server.

##### Note:

I find it easier to first set all the viewpoints to an arbitrary position, then use the "r" command to reset them. In this way, you do not have to set the viewpoints in order.

#### With realistic human motion

In order to define a new path with realistic human motion, you first need the data recorded with SteamVR using the HTC VIVE tracker. The detailed instructions could be found in the README of the [GitHub repository of SteamVR Tracking](https://github.com/tianshengs/SteamVR_Tracking). After having the .obj file, you could upload the recorded data to the RobotControl folder in Rosvita by using the **Upload** button in the file browser.

Before running the program which translates the data to joint path, open the script motion_track, and change the lines in **data_to_joint_path** function according to the current frame of robot arm. Then, type the following command in Rosvita terminal:

```
python3 motion_track.py [file name of recorded data]
```

The program will prompt you to move the robot arm to desired reference point, which means the start point where you want the robot to execute the recorded trajectory. After hitting enter, the program will convert the data to a set of joint positions which allows the robot to move according to the recorded human motion. Afterwards, the program would prompt "Enter command: " and you can enter different commands to define and examine viewpoints.

Below is a list of all commands included in the program motion_track.py and their explanations:

- e: execute a test run of path
- t: execute the recorded trajectory
- t [index number]: go to specified index position of the recorded trajectory
- number: go to specified viewpoint
- add [index number]: add the specified index position as the next viewpoint
- start: go to start point
- end: go to end point
- set [viewpoint number | start | end] [index number]: Set the specified viewpoint to the specified index position
- s: save the path to local directory
- d: discard the path

After saving the path to local directory, it will ask you to enter a name for the path. Then, the path should be ready to be loaded by the server.

##### Note:
Before setting the viewpoints, it is suggested to look at the png file generated along with the recorded data to have a general idea of the total number of index numbers, the turning points of the trajectory, and what position does each index number represent.

## Connection issue

The Netgear router has limited resources to handle the connection between devices. When sending videos or photos from the phone to main application, the connection between UR5 and Rosvita may be dropped temporarily, and the message **Heartbeat failure** will appear on the top-right side of Rosvita interface. If trying to control robot during the connection is dropped, the server will exit with an error. Therefore, it is suggested that only move the robot arm when the sending of videos and photos is completed.

## Author
- Gunanghan pan

## Acknowledgements
- Thanks to Professor Daniel Scharstein from Middlebury College for overseeing this project.
