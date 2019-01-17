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
import re
import rospy
from sensor_msgs.msg import CompressedImage
from cv_bridge import CvBridge
from geometry_msgs.msg import Point32
br = CvBridge()
# pub = rospy.Publisher('rightlegAngles', Point32, queue_size=100)

def depth_calc(knownHeight,x1,y1,x2,y2,focalLength=544.7667):
	pixHeight = abs(y2-y1)
	ppi = pixHeight/knownHeight
	cx = (x1+x2)/2
	depth = (knownHeight*focalLength)/pixHeight
	X_shift = ((cx-200)*depth)/focalLength 
	return abs(depth),X_shift


def callback(ros_data):
#### direct conversion to CV2 ####
	global br
	global CLASSES
	global COLORS
	global net
	global sub
	frame = br.compressed_imgmsg_to_cv2(ros_data)
	frame = imutils.resize(frame, width=400)
	# #debug
	# cv2.imshow("Frame", frame)
	# key = cv2.waitKey(1) & 0xFF
	(h, w) = frame.shape[:2]
	blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
	net.setInput(blob)
	detections = net.forward()
	print detections.shape[2]
	for i in np.arange(0, detections.shape[2]):
		confidence = detections[0, 0, i, 2]
		if confidence > 0.2:
			idx = int(detections[0, 0, i, 1])
			if idx is 5:
				box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
				(startX, startY, endX, endY) = box.astype("int")
				label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)
				print("depth and lateral_shift ",depth_calc(10.2362,startX,startY,endX,endY))
				print(label)
				cv2.rectangle(frame, (startX, startY), (endX, endY), COLORS[idx], 2)
				y = startY - 15 if startY - 15 > 15 else startY + 15
				cv2.putText(frame, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
				# cv2.imshow("Frame", frame)
				# key = cv2.waitKey(1) & 0xFF

				# if key == ord("q"):
				# 	sub.unregister()
				# 	cv2.destroyAllWindows()
#				break
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	if key == ord("q"):
		sub.unregister()
		cv2.destroyAllWindows()

if __name__ == '__main__':
	ap = argparse.ArgumentParser()
	ap.add_argument("-p", "--prototxt", required=True, help="path to Caffe 'deploy' prototxt file")
	ap.add_argument("-m", "--model", required=True, help="path to Caffe pre-trained model")
	ap.add_argument("-c", "--confidence", type=float, default=0.2, help="minimum probability to filter weak detections")
	args = vars(ap.parse_args())
	CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	"sofa", "train", "tvmonitor"]
	COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))
	print("loading model >>>")
	net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

	rospy.init_node('detector', anonymous=True)
	sub = rospy.Subscriber("logitech_camera1/image/compressed", CompressedImage, callback)
	try:
		rospy.spin()
	except KeyboardInterrupt:
		print "Shutting down detector module"
		cv2.destroyAllWindows()
