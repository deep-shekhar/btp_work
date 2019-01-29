from imutils.video import VideoStream,FileVideoStream
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
import sys
   

def depth_calc(knownHeight,x1,y1,x2,y2,focalLength=544.7667):
	pixHeight = abs(y2-y1)
	ppi = pixHeight/knownHeight
	cx = (x1+x2)/2
	depth = (knownHeight*focalLength)/pixHeight
	X_shift = ((cx-150)*depth)/focalLength 
	return abs(depth),X_shift



def callback(ros_data):
#### direct conversion to CV2 ####
	global br
	global CLASSES
	global COLORS
	global net
	global sub
	global count

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
		if confidence > 0.3:
			idx = int(detections[0, 0, i, 1])
			if idx is 5:
				box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])

				## my code changes				
				(startX, startY, endX, endY) = box.astype("int")
				print(startX, startY, endX, endY)
				print("depth and lateral_shift ",depth_calc(10.2362,startX,startY,endX,endY))
				label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)
				(startX, startY, endX, endY) = box.astype("int")
				print("(%d,%d),(%d,%d),label=%s"%(startX,startY,endX,endY,CLASSES[idx]))                                     

				x1,y1,x2,y2 = startX,startY,endX,endY

				bbox = (x1,y1,x2,y2)

				label = "{}: {:.2f}%".format(CLASSES[idx],
						confidence * 100)
		   


if __name__ == '__main__':
	# construct the argument parse and parse the arguments
	count = 0 

	ap = argparse.ArgumentParser()
	ap.add_argument("-p", "--prototxt", required=True,
		    help="path to Caffe 'deploy' prototxt file")
	ap.add_argument("-m", "--model", required=True,
		    help="path to Caffe pre-trained model")
	ap.add_argument("-c", "--confidence", type=float, default=0.2,
		    help="minimum probability to filter weak detections")
	args = vars(ap.parse_args())

	# initialize the list of class labels MobileNet SSD was trained to
	# detect, then generate a set of bounding box colors for each class
	CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
		    "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
		    "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
		    "sofa", "train", "tvmonitor"]
	COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

	# load our serialized model from disk
	print("[INFO] loading model...")
	net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])


	rospy.init_node('detector', anonymous=True)
	sub = rospy.Subscriber("/burgercam/image_raw/ompressed", CompressedImage, callback)
	try:
		rospy.spin()
	except KeyboardInterrupt:
		print "Shutting down detector module"
		cv2.destroyAllWindows()    




