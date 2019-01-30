#!/usr/bin/env python
import argparse
import sys, time
import roslib
import rospy
from std_msgs.msg import String


if __name__ == '__main__':
	pub_ = rospy.Publisher('cmd_data', String, queue_size=1)
	rospy.init_node('publish_cmd', anonymous=True)
	
	while not rospy.is_shutdown():
		word = raw_input(">")
		if(len(word) > 0):
			pub_.publish(word)
