#!/usr/bin/env python

# with help from teleop_keyboard.py, 
#   https://github.com/ros-teleop/teleop_twist_keyboard/blob/master/teleop_twist_keyboard.py
# Graylin Trevor Jay and Austin Hendrix, BSD licensed
#check with rostopic echo /cmd_vel

#import roslib
#import rospy
#from geometry_msgs.msg import Twist
#from std_msgs.msg import Int32
#from std_msgs.msg import Float64

import Tkinter as tk
from Tkinter import *

import os
import signal
import subprocess

import serial

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

def sonar_callback(msg):
    global obstacle
    if msg.data==1:
        obstacle = 1
        print "obstacle found"
    else:
        obstacle = 0
    print obstacle

def voltage_callback(msg):
    global voltage
    voltage = msg.data

#global variables
rosActive = False
if (rosActive):
    if (os.path.exists("/dev/tty_p3")):
        pub = rospy.Publisher('/RosAria/cmd_vel', Twist, queue_size = 5)
        sonar = rospy.Subscriber('/collision_check', Int32, sonar_callback)
        #voltage= rospy.Subscriber('/RosAria/battery_voltage', Float64, voltage_callback)
    else:
        rosActive = False
        print "P3 not connected"
speed = 0.0
turn = 0.0 
obstacle = 0

x = 0; y = 0; z = 0; th = 0
camera_text = ["Camera Off", "Camera On"]
camera_btn_text = ""
camera_status = 0
camera_process = None

root = Tk()

#setup serial
arduinoActive = True
if (arduinoActive):
    if (os.path.exists("/dev/ttyUSB0")):
        print "Connected to arduino"
        serial1 = serial.Serial("/dev/ttyUSB0",9600,timeout=0.05)
    elif (os.path.exists("/dev/ttyUSB1")):
        print "Connected to arduino"
        serial1 = serial.Serial("/dev/ttyUSB1",9600,timeout=0.05)
    #elif (os.path.exists("/dev/ttyACM0")):
    #    print "using ACM0"
    #    serial1 = serial.Serial("/dev/ttyACM0",9600,timeout=0.05)
    else: 
        ArduinoActive = False
        print "Arduino is not active!!"
strRcvBytes = b"" #serial input

# setup of overall program
class App():
    def __init__(self, root):
        # functions
        global text_box_move; global camera_btn_text
        self.buttons = {} #dictionary

        col = 0; row = 0
        temp_btn_color=Button(root, command=self.resetBtnColor)
        self.no_color = temp_btn_color.cget('bg') #get default color
        temp_btn_color.destroy()

        #speed/turn info
        Label(root, text="Speed").grid(row=row, column=col)
        self.speed_text = tk.Text(root, width=10, height=1)
        col += 1
        self.speed_text.grid(row=row,column=col)
        self.speed_text.insert("end-1c",speed)
        
        Button(root, text="+", command=self.add_0_5).grid(row=row,column=col+1)
        Button(root, text="-", command=self.sub_0_5).grid(row=row,column=col+2)
        col = 0
        row += 1
        
        Label(root, text="Turn").grid(row=row, column=col)
        self.turn_text = tk.Text(root, width=10, height=1)
        self.turn_text.grid(row=row,column=col+1)
        self.turn_text.insert("end-1c",speed)
        col+=2
        
        Button(root, text="+", command=self.addt_0_5).grid(row=row,column=col)
        Button(root, text="-", command=self.subt_0_5).grid(row=row,column=col+1)
        root.grid_columnconfigure(2, weight=0)
        root.grid_columnconfigure(3, weight=0)
        row = 0

        #current direction info
        Label(root, text="Direction:").grid(row=row, column=4)
        self.text_box = tk.Text(root, width=12, height=1)
        self.text_box.grid(row=row, column = 5, columnspan=2)
        self.text_box.insert("end-1c", "Ready!")
        
        #misc
        Button(root, text="Quit", fg="red", command=root.quit).grid(row=0, column=7)
        row += 1 
        camera_btn_text = tk.StringVar() 
        Button(root, textvariable=camera_btn_text, command=self.camera).grid(row=row, column=7)
        camera_btn_text.set(camera_text[0])

        #serial output
        self.serial_text = tk.Text(root, width=20, height=1)
        self.serial_text.grid(row=row, column = 4, columnspan=3)
        self.serial_text.insert("end-1c", "No data (yet)")
        row += 1

        #launch/load
        self.buttons['launch'] = Button(root, text="Launch", command=self.launch)
        self.buttons['load'] = Button(root, text="Load", command=self.load)
        self.buttons['launch'].grid(row=row,column=4)
        self.buttons['load'].grid(row=row, column=5)
        row += 1

        #special functions
        self.buttons['lock'] = Button(root, text="Lock", command=self.lock)
        self.buttons['resetld'] = Button(root, text="Rst Ld", command=self.resetLoad)
        self.buttons['windback'] = Button(root, text="W Back", command=self.windBack)
        self.buttons['windfwd'] = Button(root, text="W Fwd", command=self.windForward)
        self.buttons['sonar'] = Button(root, text="sonar", command=self.sonar)
        
        self.buttons['lock'].grid(row=row, column=3)
        self.buttons['resetld'].grid(row=row, column=4)
        self.buttons['windback'].grid(row=row, column=5)
        self.buttons['windfwd'].grid(row=row, column=6)
        self.buttons['sonar'].grid(row=row, column=1)

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
   
        if (arduinoActive):
            self.getSerial(self)
        self.resetBtnColor(self)

    def up(self, _event=NONE):
        self.text_box_move("up")
    def left(self, _event=NONE):
        self.text_box_move("left")
    def down(self, _event=NONE):
        self.text_box_move("down")
    def right(self, _event=NONE):
        self.text_box_move("right")
    def stop(self, _event=NONE):
        self.text_box_move("stop")
    def text_box_move(self, output):
        self.text_box.delete(1.0, "end-1c")
        self.text_box.insert("end-1c", output)
        print output
        move(output) 

    def add_0_5(self, _event=NONE):
        self.speed_change(0.25)
    def sub_0_5(self, _event=NONE):
        self.speed_change(-0.25)
    def speed_change(self, change):
        global speed
        if (speed > 0 and speed <= 5):
            speed += change
        else:
            speed = .25
        self.speed_text.delete(1.0,'end-1c')
        self.speed_text.insert("end-1c", speed)

    def addt_0_5(self, _event=NONE):
        self.turn_change(0.25) 
    def subt_0_5(self, _event=NONE):
        self.turn_change(-0.25)
    def turn_change(self, change):
        global turn
        if (turn > 0 and turn <= 5):
            turn += change
        else:
            turn = .25
        self.turn_text.delete(1.0,'end-1c')
        self.turn_text.insert("end-1c", turn)

    def launch(self, _event=NONE):
        global serial1
        self.printSerial("launching...")
        self.buttons['launch'].config(bg="green")
        serial1.write("l")
    def load(self, _event=NONE):
        global serial1
        self.printSerial("loading...")
        self.buttons['load'].config(bg="green")
        serial1.write("o")

    def lock(self, _event=NONE):
        global serial1
        self.printSerial("getting lock status...")
        self.buttons['lock'].config(bg="green")
        serial1.write("c")
    def resetLoad(self, _event=NONE):
        global serial1
        self.printSerial("resetting bean bag loader")
        self.buttons['resetld'].config(bg="green")
        serial1.write("r")
    def windBack(self, _event=NONE):
        global serial1
        self.printSerial("winding back")
        serial1.write("b")
        #self.buttons['windback'].config(bg="green")
    def windForward(self, _event=NONE):
        global serial1
        self.printSerial("winding forward")
        serial1.write("f")
        #self.buttons['windfwd'].config(bg="green")

    def sonar(self, _event=NONE):
        print "sonar button"

    def camera(self, _event=NONE):
        global camera_status; global camera_text; global camera_process
        if (camera_status==0):
            print "Turning camera on, use: nc 10.42.0.1 5000 | mplayer -fps 60 -cache 512 -"
            raspi_stream_cmd = "raspivid -fps 20 -w 1280 -h 720 -t 0 -o - | nc -l -p 5000"
            camera_process = subprocess.Popen("exec " + raspi_stream_cmd, stdout=subprocess.PIPE,
                    shell=True, preexec_fn=os.setsid)
            camera_status = 1
        else:
            print "Turning camera off"
            os.killpg(os.getpgid(camera_process.pid), signal.SIGTERM)
            camera_status = 0
        camera_btn_text.set(camera_text[camera_status])

    def getSerial(self, _event=NONE):
        global strRcvBytes; global serial1; global root
        if (not ('\n' or '') in strRcvBytes):
            if (arduinoActive):
                strRcvBytes += serial1.read(serial1.inWaiting()) #read all in buffer
        
        if ('\n' in strRcvBytes):
            #strRcv = str(strRcvBytes, 'utf-8').rstrip('\n')
            #strRcvBytes = strRcvBytes.rstrip('\n')
            strList = strRcvBytes.split('\n')
            strList.remove('')

            for i in strList:
                if (i == "ln"):
                    self.buttons['launch'].config(bg=self.no_color)
                    self.printSerial("launched")
                    self.resetBtnColor()
                elif (i[:2] == "ld"):
                    self.buttons['load'].config(bg=self.no_color)
                    self.printSerial("loaded #" + i[2])
                elif (i == "ul"):
                    self.buttons['lock'].config(bg=self.no_color)
                    self.printSerial("unlocked")
                elif (i == "lk"):
                    self.buttons['lock'].config(bg='green')
                    self.printSerial("locked")
                elif (i == "rl"):
                    self.buttons['resetld'].config(bg=self.no_color)
                    self.printSerial("reset load")
                elif (i == "wf"):
                    self.printSerial("winding foward")
                    self.buttons['windfwd'].config(bg='green')
                    self.buttons['windback'].config(bg=self.no_color)
                elif (i == "wb"):
                    self.printSerial("winding backwards")
                    self.buttons['windback'].config(bg='green')
                    self.buttons['windfwd'].config(bg=self.no_color)
                elif (i == "rcv"):
                    self.printSerial("received signal")
                elif (i == "cl"):
                    self.resetBtnColor()
                elif (i == "rdy"):
                    self.printSerial("Ready")
                    self.resetBtnColor()
                else:
                    print i
            
            serial1.flushInput()
            strRcvBytes=""

        root.after(100,self.getSerial) #every 100 ms recheck serial
    def printSerial(self, string):
        self.serial_text.delete(1.0,'end-1c')
        self.serial_text.insert("end-1c", string)
        print string

    def resetBtnColor(self, _event=NONE):
        global root;
        for key in self.buttons:
            if (self.buttons[key].cget('bg') != self.no_color):
                self.buttons[key].config(bg=self.no_color)
        #root.after(5000,self.resetBtnColor)

def move(key):
    global obstacle
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
    if (rosActive):     
        twist = Twist()
        print(obstacle)
        twist.linear.x = x*speed; twist.linear.y = y*speed; twist.linear.z = z*speed
        twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = th*turn
        print "velocity: speed %s turn %s" % (speed, turn)
        pub.publish(twist)

def kill_camera():
    global camera_status; global camera_process
    # kill camera if needed
    if (camera_status):
        os.killpg(os.getpgid(camera_process.pid), signal.SIGTERM)
        camera_status = 0
    camera_btn_text.set(camera_text[camera_status])

    subprocess.call("exec pkill raspivid", shell=True)

def main():
    global speed; global turn
    if (rosActive):
        #rospy stuff
        #pub = rospy.Publisher('cmd_vel', Twist, queue_size = 1)
        rospy.init_node('gui_teleop')
        # get battery info?

        speed = 1.0; turn = 1.0 
        speed = rospy.get_param("~speed", 1.0)
        turn = rospy.get_param("~turn", 1.0)
        
    print(starting_msg)
    print "velocity: speed %s turn %s" % (speed, turn)

    #setup app class instance
    global root
    app = App(root)
    root.minsize(200,200)
    root.title("P3 RC")

    root.mainloop() #infinite loop
    print "end"
    kill_camera()

def exit_cmd(signum, frame):
    if (camera_status):
        kill_camera()
    sys.exit(1)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, exit_cmd)
    main()
