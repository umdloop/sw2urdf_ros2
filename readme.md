# sw2urdf_ros2

This is an adapted version of a [script](https://github.com/xiaoming-sun6/sw2urdf_ros2) by xiaoming-sun6.
It allows you to convert a ROS 1 robot description package that is created by the sw2urdf exporter of SolidWorks to ROS 2.
It will propably also mostly work with other ROS 1 URDF packages, but might require some small fixes for individual cases.

Tested with the following environment, but will propably also work with others.
- Solidworks 2020
- Ubuntu 22.04
- ROS 2 Rolling
- Python == 3.10

Download the tool from github

~~~ bash
git clone https://github.com/SammyRamone/sw2urdf_ros2.git
~~~

Change the configuration variables at the top of the conversion_urdf_ros_2_ros2.py

Run the script.

```bash
python3 conversion_urdf_ros_2_ros2.py
```

Build the package in your workspace and source it.
~~~ bash
cd PATH:_TO_WORKSPACE && colcon build && source install/setup.bash
~~~

Launch the package to bring up RViz with the robot.
~~~ bash
ros2 launch test_urdf_tool launch.py
~~~

A default RViz config should be loaded that shows the robot, but you might need to perform further changes.


[Original Implementation of this script](https://github.com/xiaoming-sun6/sw2urdf_ros2)

[sw2urdf plugin](http://wiki.ros.org/sw_urdf_exporter)

