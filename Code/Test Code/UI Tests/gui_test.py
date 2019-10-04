#!/usr/bin/python

# with help from teleop_keyboard.py, 
#   https://github.com/ros-teleop/teleop_twist_keyboard/blob/master/teleop_twist_keyboard.py
# Graylin Trevor Jay and Austin Hendrix, BSD licensed
#check with rostopic echo /cmd_vel

import roslib
import rospy
from geometry_msgs.msg import Twist

import Tkinter as tk
from Tkinter import *

import os
import signal
import subprocess

starting_msg = """Move with:
    i
j   k   l
(or wasd, space to stop)
"""

movement={
    "up":(1,0,0,0),
    "left":(0,0,0,1),
    "down":(-1,0,0,0),
    "right":(0,0,0,-1),
    "stop":(0,0,0,0)
    }
#global variables
rosActive = False
if (rosActive):
    pub = rospy.Publisher('/RosAria/cmd_vel', Twist, queue_size = 1)
speed = 1.0
turn = 0.5 
x = 0; y = 0; z = 0; th = 0
camera_text = ["Turn Camera On", "Turn Camera Off"]
camera_btn_text = ""
camera_status = 0
camera_process = None

# setup of overall program
class App():
    def __init__(self, root):
        # functions
        global text_box_print; global camera_btn_text

        col = 0; row = 0
        #speed/turn info
        Label(root, text="Speed").grid(row=row, column=col)
        self.speed_text = tk.Text(root, width=10, height=1)
        col += 1
        self.speed_text.grid(row=row,column=col)
        self.speed_text.insert("end-1c",speed)
        
        Button(root, text="+", command=self.add_0_5).grid(row=row,column=col+1)
        Button(root, text="-", command=self.sub_0_5).grid(row=row,column=col+2)
        col+=3
        
        Label(root, text="Turn").grid(row=row, column=col)
        self.turn_text = tk.Text(root, width=10, height=1)
        self.turn_text.grid(row=row,column=col+1)
        self.turn_text.insert("end-1c",speed)
        col+=2
        
        Button(root, text="+", command=self.addt_0_5).grid(row=row,column=col)
        Button(root, text="-", command=self.subt_0_5).grid(row=row,column=col+1)

        row += 1
        #misc
        camera_btn_text = tk.StringVar() 
        Button(root, textvariable=camera_btn_text, command=self.camera).grid(row=row, column=0, columnspan=2)
        camera_btn_text.set(camera_text[0])
        Button(root, text="Quit", fg="red", command=root.quit).grid(row=row, column=6)

        #current direction info
        self.text_box = tk.Text(root, width=10, height=1)
        self.text_box.grid(row=row, column = 3, columnspan=2)
        self.text_box.insert("end-1c", "Ready!")
        
        root.grid_columnconfigure(2, weight=0)
        root.grid_columnconfigure(3, weight=0)

        keyArray = [['i', 'w', '<Up>'], 
                ['j', 'a', '<Left>'],
                ['k', 's', '<Down>'], 
                ['l', 'd', '<Right>']]

        for i in keyArray[0]:
            root.bind(i, self.up)
        for i in keyArray[1]:
            root.bind(i, self.left)
        for i in keyArray[2]:
            root.bind(i, self.down)
        for i in keyArray[3]:
            root.bind(i, self.right)
        root.bind('<space>', self.stop)

    def up(self, _event=NONE):
        self.text_box_print("up")
        move("up") 
    
    def left(self, _event=NONE):
        self.text_box_print("left")
        move("left") 
    
    def down(self, _event=NONE):
        self.text_box_print("down")
        move("down") 
    
    def right(self, _event=NONE):
        self.text_box_print("right")
        move("right") 
    
    def stop(self, _event=NONE):
        self.text_box_print("stop")
        move("stop") 

    def text_box_print(self, output, term=True):
        if (term):
            print output
        self.text_box.delete(1.0, "end-1c")
        self.text_box.insert("end-1c", output)

    def add_0_5(self, _event=NONE):
        global speed
        if (speed >= 0 and speed < 5):
            speed += 0.5
        self.speed_text.delete(1.0,'end-1c')
        self.speed_text.insert("end-1c", speed)
    
    def sub_0_5(self, _event=NONE):
        global speed
        if (speed > 0 and speed <= 5):
            speed -= 0.5
        self.speed_text.delete(1.0,'end-1c')
        self.speed_text.insert("end-1c", speed)

    def addt_0_5(self, _event=NONE):
        global turn
        if (turn >= 0 and turn < 5):
            turn += 0.5
        self.turn_text.delete(1.0,'end-1c')
        self.turn_text.insert("end-1c", turn)
    
    def subt_0_5(self, _event=NONE):
        global turn
        if (turn > 0 and turn <= 5):
            turn -= 0.5
        self.turn_text.delete(1.0,'end-1c')
        self.turn_text.insert("end-1c", turn)

    def camera(self, _event=NONE):
        global camera_status; global camera_text; global camera_process
        if (camera_status==0):
            print "Turning on, use: nc 10.42.0.1 500 | mplayer -fps 40 -cache 512 -"
            raspi_stream_cmd = "raspivid -fps 20 -w 1280 -h 720 -vf -hf -t 0 -o - | nc -l -p 5000"
            camera_process = subprocess.Popen("exec " + raspi_stream_cmd, stdout=subprocess.PIPE,
                    shell=True, preexec_fn=os.setsid)
            camera_status = 1
        else:
            print "Turning off"
            os.killpg(os.getpgid(camera_process.pid), signal.SIGTERM)
            camera_status = 0
        camera_btn_text.set(camera_text[camera_status])

def move(key):
    #try: 
    if key in movement.keys():
        x  = movement[key][0]
        y  = movement[key][1]
        z  = movement[key][2]
        th = movement[key][3]
        #print("x ", x, " y ", y, " z ", z, " th ", th)
    else:
        x = 0; y = 0; z = 0; th = 0
        print("??")
    if (False):     
        twist = Twist()
        twist.linear.x = x*speed; twist.linear.y = y*speed; twist.linear.z = z*speed
        twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = th*turn
        pub.publish(twist)

def kill_camera():
    # kill camera if needed
    subprocess.call("exec pkill raspivid", shell=True)

def main():
    global speed; global turn
    if (rosActive):
        #rospy stuff
        #pub = rospy.Publisher('cmd_vel', Twist, queue_size = 1)
        rospy.init_node('gui_teleop')
        # get battery info?

        speed = rospy.get_param("~speed", 0.5)
        turn = rospy.get_param("~turn", 1.0)
        
    print(starting_msg)
    print "velocity: speed %s turn %s" % (speed, turn)

    root = Tk()
    #setup app class instance
    app = App(root)

    root.mainloop()
    print "end"
    kill_camera()

def exit_cmd(signum, frame):
    if (camera_status):
        kill_camera()
    sys.exit(1)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, exit_cmd)
    main()
