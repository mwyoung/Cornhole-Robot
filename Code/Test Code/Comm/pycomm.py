#!/usr/bin/python3

import serial
import time


def getValue(s1):
    strRcvBytes = b"" #byte string
    while (not '\n' in str(strRcvBytes,'utf-8') ):
        time.sleep(0.1) #100 ms
        strRcvBytes += s1.read(s1.inWaiting())
    strRcv = str(strRcvBytes, 'utf-8').rstrip('\n')
    print(strRcv)

    rcvValue = s1.read() #read 10 bytes, times out
    #time.sleep(0.2)
    #data_left = s1.inWaiting() #get leftover chars
    #rcvValue += s1.read(data_left)
     
    #if(len(rcvValue)>0):
    #    rcvValue = str(rcvValue, 'utf-8')
    #    print(rcvValue)
    #s1.flushInput()

def main():
    port = "/dev/ttyACM0"
    rate = 9600

    s1 = serial.Serial(port, rate, timeout=1)
    #wait for ready
    while True:
        if (s1.in_waiting > 0):
            getValue(s1)
            break
        time.sleep(0.1)

    time.sleep(.5)

    while True:
        readInput = input("Enter a char: ")

        if (readInput != "") :
            s1.write(readInput[0].encode())
            time.sleep(0.1) #100 ms
            getValue(s1)
        s1.flushInput();

if __name__ == '__main__':
    main()
