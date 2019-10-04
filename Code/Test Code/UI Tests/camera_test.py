#!/usr/bin/python
import Tkinter as tk
import picamera
from time import sleep

camera = picamera.PiCamera()

def CameraOn():
    camera.preview_fullscreen=False
    camera.preview_window=(90,100,320,240)
    camera.resolution=(640,480)
    camera.start_preview()

def CameraOff():
    camera.stop_preview()

root = tk.Tk()

CameraOn()

root.mainloop()

root.destroy

camera.stop_preview()
camera.close()
