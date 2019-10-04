#!/usr/bin/python

# with help from teleop_keyboard.py, 
#   https://github.com/ros-teleop/teleop_twist_keyboard/blob/master/teleop_twist_keyboard.py
# Graylin Trevor Jay and Austin Hendrix, BSD licensed

import roslib; #roslib.load_manifest('teleop_move')
import rospy

from geometry_msgs.msg import Twist

import sys, select, termios, tty

starting_msg = """Move with:
    i
j   k   l
(or wasd, space to stop)
CTRL-C to quit
"""

movement={
    'i':(1,0,0,0),
    'j':(0,0,0,1),
    'k':(0,0,0,-1),
    'l':(-1,0,0,0),

    'w':(1,0,0,0),
    'a':(0,0,0,1),
    's':(0,0,0,-1),
    'd':(-1,0,0,0),

    ' ':(0,0,0,0),
    }

def checkForArrowKeys(key):
    if (key=='\x1b[A'):
        return "i"
    elif (key=='\x1b[D'):
        return "j"
    elif (key=='\x1b[B'):
        return "k"
    elif (key=='\x1b[C'):
        return "l" 
    else:
        return key

def getKey():
    tty.setraw(sys.stdin.fileno())
    select.select([sys.stdin], [], [], 0)
    key = sys.stdin.read(1)
    key = checkForArrowKeys(key)
    print key
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

def current_vel(speed,turn):
    return "velocity: speed %s turn %s" % (speed, turn)

def main():
    # control terminal printing
    global settings
    settings = termios.tcgetattr(sys.stdin)

    #rospy stuff
    #pub = rospy.Publisher('cmd_vel', Twist, queue_size = 1)
    #rospy.init_node('teleop_move')
    # get battery info?

    #speed = rospy.get_param("~speed", 0.5)
    #turn = rospy.get_param("~turn", 1.0)
    speed = 0.5; turn = 1.0; 
    x = 0; y = 0; z = 0; th = 0; status = 0

    try: 
        print(starting_msg)
        print(current_vel(speed,turn))
        #execute always
        while(1):
            key = getKey()
            if key in movement.keys():
                x  = movement[key][0]
                y  = movement[key][1]
                z  = movement[key][2]
                th = movement[key][3]
                print("x ", x, " y ", y, " z ", z, " th ", th)
            else:
                x = 0; y = 0; z = 0; th = 0
                # if control key
                if (key == '\x03'): 
                    break
                
                print("??")
            
            key = ""

            #twist = Twist()
            #twist.linear.x = x*speed; twist.linear.y = y*speed; twist.linear.z = z*speed
            #twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = th*turn
            #pub.publish(twist)

    except Exception as e:
        print(e)

    finally: 
        #twist = Twist()
        #twist.linear.x = x*speed; twist.linear.y = y*speed; twist.linear.z = z*speed
        #twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = th*turn

        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

if __name__=="__main__":
    main()
