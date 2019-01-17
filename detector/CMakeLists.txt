cmake_minimum_required(VERSION 2.8.3)
project(detector)

## Compile as C++11, supported in ROS Kinetic and newer
# add_compile_options(-std=c++11)
include_directories(
# include
  ${catkin_INCLUDE_DIRS}
  ${PYTHON_INCLUDE_DIRS}
  src
)
## Find catkin macros and libraries
## if COMPONENTS list like find_package(catkin REQUIRED COMPONENTS xyz)
## is used, also find other catkin packages
find_package(catkin REQUIRED COMPONENTS
  geometry_msgs
  rospy
  sensor_msgs
  std_msgs
)

catkin_package(
   INCLUDE_DIRS src
#  LIBRARIES detector
   CATKIN_DEPENDS geometry_msgs rospy sensor_msgs std_msgs
#  DEPENDS system_lib
)

###########
## Build ##
###########

## Specify additional locations of header files
## Your package locations should be listed before other locations


