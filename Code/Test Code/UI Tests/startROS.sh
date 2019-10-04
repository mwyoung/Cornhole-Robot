#!/bin/bash

#setup trap signals when exiting
trap "exit" INT TERM ERR
trap "kill 0" EXIT

#color def, ansi colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}-------------------------"
echo -e "starting roscore"
echo -e "-------------------------${NC}"

# startup ROSCORE
# 1>&2 hides messages, & goes to background
roscore &

echo -e "${RED}-------------------------"
echo -e "going to sleep"
echo -e "-------------------------${NC}"
sleep 5 
echo -e "${RED}-------------------------"
echo -e "waking up"
echo -e "-------------------------${NC}"

echo -e "${GREEN}setting up rosaria${NC}"
# start up rosaria
rosrun rosaria RosAria _port:=/dev/ttyUSB0

# wait for processes to end
wait

echo -e "${RED}quiting roscore${NC}"

sleep 2
#kill roscore if needed
echo -e "-------------------------${NC}"
echo "${RED} killing leftover processes if needed"
rosnode kill -a; killall -9 rosmaster; killall -9 roscore


