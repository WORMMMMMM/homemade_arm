# Homemade Arm

Prerequisites: Ubuntu 20.04, ROS noetic

## How to install

```shell
git clone git@github.com:Grange007/homemade_arm.git
cd homemade_arm/src/
rosdep install -y --from-paths . --ignore-src --rosdistro noetic
cd ..
catkin_make
source ./devel/setup.sh
roslaunch ave_arm_config ave_arm.launch
```