#!/usr/bin/env python

import rospy, time
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String

def scan_callback(msg):
    global range_front
    global range_right
    global range_left
    global ranges
    global min_front,i_front, min_right,i_right, min_left ,i_left 
    
    ranges = msg.ranges
    # get the range of a few points
    # in front of the robot (between 25 to -24 degrees)
    range_front[:25] = msg.ranges[25:0:-1]  
    range_front[25:] = msg.ranges[360:345:-1]
    # to the right (between 330 to 270 degrees)
    range_right = msg.ranges[270:330]
    # to the left (between 30 to 90 degrees)
    range_left = msg.ranges[90:30:-1]
    # get the minimum values of each range 
    # minimum value means the shortest obstacle from the robot
    min_range,i_range = min( (ranges[i_range],i_range) for i_range in xrange(len(ranges)) )
    min_front,i_front = min( (range_front[i_front],i_front) for i_front in xrange(len(range_front)) )
    min_right,i_right = min( (range_right[i_right],i_right) for i_right in xrange(len(range_right)) )
    min_left ,i_left  = min( (range_left [i_left ],i_left ) for i_left  in xrange(len(range_left )) )
    

def voice_cmd(word):
    global start, wait, left, right, forward, backward
    if word.data.find('go') > -1: 
        start = 1
        wait = 0
	left = 0
	right = 0
	forward = 0
	backward = 0
    elif word.data.find('wait') > -1:
        start = 0
        wait = 1
	left = 0
	right = 0
	forward = 0
	backward = 0

    if wait==1:
        if word.data.find('left') > -1:
	    left = 1
        elif word.data.find('right') > -1:
	    right = 1
        elif word.data.find('forward') > -1:
	    forward = 1
        elif word.data.find('backward') > -1:
	    backward = 1

    return


# Initialize all variable
range_front = []
range_right = []
range_left  = []
min_front = 0
i_front = 0
min_right = 0
i_right = 0
min_left = 0
i_left = 0
same_cmd_cnt = 0
last_cmd = -1
start = 0
wait = 1
left = 0
right = 0
forward = 0
backward = 0

# Create the node
cmd_vel_pub = rospy.Publisher('cmd_vel', Twist, queue_size = 1) # to move the robot

voice_sub = rospy.Subscriber('cmd_data',String, voice_cmd)
scan_sub = rospy.Subscriber('scan', LaserScan, scan_callback)   # to read the laser scanner
rospy.init_node('path_explorer')


command = Twist()
command.linear.x = 0.0
command.angular.z = 0.0
        
rate = rospy.Rate(8)
time.sleep(1) # wait for node to initialize

near_wall = 0 # start with 0, when we get to a wall, change to 1

# Turn the robot right at the start
# to avoid the 'looping wall'
print("Starting15...")
command.angular.z = 0.0
command.linear.x = 0.0
cmd_vel_pub.publish(command)
time.sleep(2)
       
while not rospy.is_shutdown():
    # The left hand on wall algorithm:
    
    if start == 0 or wait == 1:
        #print("Stopped!!")
	if left == 1:
           command.angular.z = 0.6
           command.linear.x = 0.0
           cmd_vel_pub.publish(command)
	   time.sleep(1)
	   left = 0
	elif right == 1:
           command.angular.z = -0.6
           command.linear.x = 0.0
           cmd_vel_pub.publish(command)
	   time.sleep(1)
	   right = 0
	elif forward == 1:
           command.angular.z = 0.0
           command.linear.x = 0.08
           cmd_vel_pub.publish(command)
	   time.sleep(1)
	   forward = 0
	elif backward == 1:
           command.angular.z = 0.0
           command.linear.x = -0.08
           cmd_vel_pub.publish(command)
	   time.sleep(1)	
	   backward = 0
	else:
           command.angular.z = 0.0
           command.linear.x = 0.0
           cmd_vel_pub.publish(command)

        if start == 0:
            continue
    
    print("min_front={} , min_left={}, min_right={} ".format(min_front,min_left,min_right))
    
    
    if(same_cmd_cnt > 160):
        if(last_cmd == 5):
            if(min_right < min_left):
                command.angular.z = 0.5
                command.linear.x = 0.0
            else:
                command.angular.z = -0.5
                command.linear.x = 0.0
            cmd_vel_pub.publish(command)
            same_cmd_cnt = 0
            time.sleep(2)

    elif(same_cmd_cnt > 80):
        print("seems like stuck at a place try to get out")
        #ts = int(time.time())
        if(last_cmd == 0):
            command.angular.z = -1.4  
            command.linear.x = -0.09
        elif(last_cmd == 3):
            command.angular.z = 1.4   
            command.linear.x = -0.09
                
        cmd_vel_pub.publish(command)
        same_cmd_cnt = 0
        time.sleep(2)

    if (min_front < 0.19):
	if(last_cmd == 5):
            same_cmd_cnt += 1
        else:
            last_cmd = 5
            same_cmd_cnt = 0
        print("front wall too close backup a little")
        command.angular.z = 0
        command.linear.x = -0.08
        cmd_vel_pub.publish(command)
        while(min_front < 0.25 and not rospy.is_shutdown()):      
            pass
		
    elif(min_left < 0.15):
	print("too close to left wall")
	command.angular.z = -0.1
	command.linear.x = 0.08
        cmd_vel_pub.publish(command)
        time.sleep(1)      
    elif(min_right < 0.15):
	print("too close to right wall")
	command.angular.z = 0.1
	command.linear.x = 0.08
	cmd_vel_pub.publish(command)
	time.sleep(1)      


    if((min_left < 0.26 or min_right < 0.26) and min_front > 0.32):
        if(last_cmd == 5):
            same_cmd_cnt += 1
        else:
            last_cmd = 5
            same_cmd_cnt = 0

        print("along wall but front is clear")
		
        command.angular.z = 0.0   
        command.linear.x = 0.08
        cmd_vel_pub.publish(command)    

    elif(min_left > 0.25 and not rospy.is_shutdown()):
        if(last_cmd == 0):
            same_cmd_cnt += 1
        else:
            last_cmd = 0
            same_cmd_cnt = 0

        print("Can turn Left so turing Left")
        if(min_front > 0.33 and min_right > 0.20):       
            command.angular.z = 0.08   
            command.linear.x = 0.11
	    cmd_vel_pub.publish(command)
        else:
            command.angular.z = 0.5    
            command.linear.x = 0.0 
            cmd_vel_pub.publish(command)
	    while(min_front < 0.33):
		pass
    
    
    elif(min_front > 0.33 and not rospy.is_shutdown()):
        if(last_cmd == 2):
            same_cmd_cnt += 1
        else:
            last_cmd = 2
            same_cmd_cnt = 0
        
        print("Can go ahead straight so going straight")
        command.angular.z = 0.0
        command.linear.x = 0.11
        # publish command 
        cmd_vel_pub.publish(command)

    elif(min_right > 0.25 and not rospy.is_shutdown()):
        if(last_cmd == 3):
            same_cmd_cnt += 1
        else:
            last_cmd = 3
            same_cmd_cnt = 0

        print("Can turn Right so turing Right")
        if(min_front > 0.33 and min_left > 0.20):       
            command.angular.z = -0.08    
            command.linear.x = 0.11
        else:
            command.angular.z = -0.5    
            command.linear.x = 0.0

        # publish command 
        cmd_vel_pub.publish(command)
	while(min_left < 0.30):
	    pass
    
    else:
        if(last_cmd == 4):
            same_cmd_cnt += 1
        else:
            last_cmd = 4
            same_cmd_cnt = 0
            
        print("At dead end so turn around")
	if(min_left < min_right):
            command.angular.z = -0.5
	else:
	    command.angular.z = 0.5
        command.linear.x = 0.0
        # publish command 
        cmd_vel_pub.publish(command)
        while(min_front < 0.33 and not rospy.is_shutdown()):      
            pass
    
    # wait for the loop
    rate.sleep()
    
