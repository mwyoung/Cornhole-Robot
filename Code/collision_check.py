#!/usr/bin/env python

# Every python controller needs these lines
import rospy
import pdb
import math

# The velocity command message

# The laser scan message
from sensor_msgs.msg import PointCloud

from std_msgs.msg import Int32

# This is called every time we get a LaserScan message from ROS.
def sonar_callback(msg):
	

	# Drive forward at a given speed.  The robot points up the x-axis.
    
    stopping_distance=rospy.get_param('stopping_distance')
    detected=detect_obstacle(msg,stopping_distance)

	# Publish the command using the global publisher
    pub.publish(detected)
    
def detect_obstacle(reading,stopping_distance):
    
    
    #pdb.set_trace()
    detected=0
    output = {}
    for i in range(3,4):
	val = abs(reading.points[i].x)
        if val>0.01 and val<stopping_distance:
	    output[i] = round(val, 5)
            detected+=1
    
    for i in range(11,12):
	val = abs(reading.points[i].x)
        if val>0.01 and val<stopping_distance:
	    output[i] = round(val, 5)
            detected+=2
        
    print output
	
    return detected
        

if __name__ == '__main__':
    rospy.init_node('obstacle_detector')
    # A publisher for the move data
    pub = rospy.Publisher('collision_check', Int32, queue_size=1)
    # A subscriber for the laser scan data
    sub = rospy.Subscriber('/RosAria/sonar', PointCloud, sonar_callback)

    rospy.set_param('stopping_distance',0.70) #initial value of stopping distance! 

    rospy.spin()
