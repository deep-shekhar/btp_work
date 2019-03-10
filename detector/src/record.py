#!/usr/bin/env python
from imutils.video import VideoStream
from imutils.video import FPS

import argparse
import imutils
import time
import sys, time
import numpy as np
from scipy.ndimage import filters
import cv2
import roslib
import rospy
from sensor_msgs.msg import CompressedImage
from cv_bridge import CvBridge
from geometry_msgs.msg import Point32
br = CvBridge()
# pub = rospy.Publisher('rightlegAngles', Point32, queue_size=100)


count = 0

def callback(ros_data):
#### direct conversion to CV2 ####
	global br, count
        count += 1
	frame = br.compressed_imgmsg_to_cv2(ros_data)
	frame = imutils.resize(frame, width=400)
	# #debug
	frame = frame[50:,:]
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF
        if(count%15==0):
            frame = cv2.resize(frame, (360,200))
            cv2.imwrite("/home/deep/catkin_ws/src/detector/src/img_folder/frame_{}.jpg".format(count),frame)
	if key == ord("q"):
		sub.unregister()
		cv2.destroyAllWindows()

if __name__ == '__main__':
	rospy.init_node('record', anonymous=True)
	sub = rospy.Subscriber("/logitech_camera1/image/compressed", CompressedImage, callback)
	try:
		rospy.spin()
	except KeyboardInterrupt:
		print "Shutting down display module"
		cv2.destroyAllWindows()
