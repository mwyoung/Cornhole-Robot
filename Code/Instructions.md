Downloads used for this project: [Ubuntu Mate 16.04 for
ROS](https://ubuntu-mate.org/raspberry-pi/ubuntu-mate-16.04.2-desktop-armhf-raspberry-pi.img.xz)
and [Raspbian for
drivers](http://downloads.raspberrypi.org/raspbian_lite/images/raspbian_lite-2018-04-19/).

### Raspberry Pi Setup
Note: Only for 3B+ ([source](
https://www.raspberrypi.org/forums/viewtopic.php?p=1301685#p1301685)).

Copy the following files from Raspbian to Ubuntu Mate:
 - For Booting: copy bootcode.bin, fixup.dat, start.elf, bcm2710-rpi-3-b-plus.dtb and kernel7.img
	- also start\_cd.elf, fixup\_x.dat, and start\_x.dat
 - For keyboard/mouse: copy /lib/modules/4.9.80-v7+ (root partition)
 - For network: copy the contents of /lib/firmware/brcm/ (root partition)

If you want to boot from USB:
 - edit cmdline.txt, change root=/dev/mmcblk0p2 to root=/dev/sda2 (boot partition)
 - edit etc/fstab, change/dev/mmcblk0p2 to sda2 and /dev/mmcblk0p1 to sda1 (root partition)

### Copying files to SD card
Extract xz file:
unxz --keep <file>

To copy: use `fdisk -l <file.img>` <br \>
 - get boot sector size (512 bytes, etc)
 - get value of offset (size * start, ex 512 * 2048)

mount:
sudo mkdir /media/path/img
sudo mount -o loop,offset=<offset> <file.img> /media/path/img

2048*512 = 1048576
131072*512 = 67108864

copy files:
In directory, use sudo cp <files...> /media/path/img/path...
	cp -r may be needed if copying the entire folder

unmount:
sudo umount /media/path/img/

Copy to sd card

fdisk -l
	print all disks, find /dev/mmcblk*** number (could  be /dev/sd** if USB)
dd bs=4M if=<file.img> of=/dev/*** status=progress
	!! warning, using the wrong /dev/*** could destroy your computer/OS (dd is sometimes called disk destroyer) !!
	This could also take a bit of time as it copies over to the sd card

### Ubuntu Mate setup
Turn off auto updates
System -> administration -> software & updates -> updates tab -> automatically check for updates: never

#### Software
To uninstall software, first open a terminal (`ctrl + alt + t`). The commands `apt list
--installed` lists all of the installed packages, `sudo apt autoremove` removes packages
not needed by other packages. `sudo apt update` updates the package sources and is needed
before updating packages with `sudo apt upgrade`, `sudo apt install <package>` installs a
package, and `sudo apt remove <package>` removes a package.

The packages that can be removed include: sudo apt purge youtube-dl youtube-dlg thunderbird libreoffice-core libreoffice-common minecraft-pi brasero transmission-common deja-dup atril hexchat account-plugin-* galculator gnome-orca shotwell-common plymouth snapd squeak-*

Other changes to have a faster desktop include installing the lxde windows manager with
`sudo apt install lxde lxde-common lxsession-logout lxdm` and removing `sudo apt purge
mate mate-optimus`. Then, use `update-alternatives --config x-session-manager` to change
the default windows manager.

To be able to update the time, the command `sudo date -s "YYYY-MM-DD HH:MM:SS"` updates
the current time. This value is only updated while the Rasberry Pi is on due to it not
having a real time clock to keep track of the time while off.

Another nice tool is readlink, which is able to get the location of a file with `readlink
-f <file>`.

#### Bootloader
To edit the boot options, do `sudo nano /boot/cmdline.txt`, and remove "quiet splash" and
"plymouth.ignore-serial-consoles" to show things loading instead of an animation.

Also necessary is the ability to access the camera and ssh, which can be changed by
running the command `sudo raspi-config` and in interfacing options -> turn on camera and ssh.

One option is to reduce the [CPU
frequency](https://www.raspberrypi.org/documentation/configuration/config-txt/overclocking.md)
to reduce the power of the system, which can be done with `sudo nano /boot/config.txt` and
editing the line to `set arm_freq=1200`.

If there is a problem of a long shutdown (due to cups-browsed), the command `sudo systemctl stop cups-browsed.service && sudo systemctl disable cups-browsed.service` can disable the service.

Finally, to be able to decrease the default timeout, do `sudo nano /etc/systemd/system.conf` and on the line DefaultTimeout{Start/Stop}Sec=90s change it to 10s.

### ROS setup
[Instructions from the ROS wiki](http://wiki.ros.org/kinetic/Installation/Ubuntu to install)
Setup sources.list: `sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'`

Then set up the keys used to verify the software with `sudo apt-key adv --keyserver hkp://ha.pool.sks-keyservers.net:80 --recv-key 421C365BD9FF1F717815A3895523BAEEB01FA116`. An alternate hkp server that can be used would be hkp://pgp.mit.edu:80 or hkp://keyserver.ubuntu.com:80

Then update the sources with `sudo apt-get update`. Finally, install the Desktop-Full
(ROS, rqt, rviz, robot-generic libraries, 2D/3D simulators, navigation and 2D/3D
perception) with `sudo apt-get install ros-kinetic-desktop-full`.

Then install [ROSARIA](http://wiki.ros.org/ROSARIA), which is located at [github.com/reedhedges/AriaCoda](https://github.com/reedhedges/AriaCoda). This code can be installed with `make install`. If using catkin\_make, use catkin\_make -j 1 to limit the number of threads or else the system becomes very slow

### Wifi Hotspot setup
To be able to SSH into the Raspberry Pi when having a Wifi hotspot mode, it is helpful to know the IP address, which can
be found using `hostname -I`.

ssh ros-p3@10.x.x.1				connect from other machine to the pi, also connect to the wifi rpi-13 with password

To decrease the amount of services running, use `sudo raspi-config`, and in `boot options` enable `cli boot`. To start a GUI in command line mode, use `startx`.

To be able to autostart the wifi, edit the file `sudo nano /etc/rc.local` and add `bash /home/<username>/setup.sh &` where username is the current username. `&` allows the script to run in the background. Next, create the file `nano /home/<username>/setup.sh`, and add the following lines:
`!#/bin/bash
nmcli dev wifi hotspot ifname wlan0 ssid <ssid> password "<password>"`. Finally, allow the
file to be executed with `chmod +x /home/<username>/setup.sh`.

### ROS [USB
setup](https://askubuntu.com/questions/112568/how-do-i-allow-a-non-default-user-to-use-serial-device-ttyusb0/680328#680328)

`sudo usermod -a -G dialout $USER` allows access to usb serial output with the following
rule: <br />
Open the file (`sudo nano /etc/udev/rules.d/50-myusb.rules`) and add: <br />
`KERNEL=="ttyUSB[0-9]*",MODE="0666"
KERNEL=="ttyACM[0-9]*",MODE="0666"
SUBSYSTEM=="tty",DRIVERS="pl2303",SYMLINK+="tty_robot"
SUBSYSTEM=="tty",DRIVERS="ch341-uart",SYMLINK+="tty_arduino"`
The SYMLINK lines allow for a system link even if the ttyUSB change after a reboot. Use
`udevadm info --attribute-walk --path=/dev/ttyUSB*` to get this information from the parent
class of the device.

To start ROS, use `roscore &` and `rosrun rosaria RosAria _port:=/dev/ttyUSB0 &`, which
could be in a bash script with sleep timers.

### Streaming video
First, check the camera with `vcgencmd get_camera`, and then the command `raspistill -o
file.jpg` to be able to test the camera. To view the image (even over ssh when using `ssh
-x`), use `xdg-open file.jpg`.

The command (on the raspberry pi)
`raspivid -fps 20 -w 1280 -h 720 -vf -hf -t 0 -o - | nc -l -p 5000`
starts the video streaming, and can be placed in a bash script.
Then, the command (on the sshing computer)
`netcat <ip address> 5000 | mplayer -fps 60 -cache 512 -` can be used to view the image, where the <ip address> is the ip address that
the computer is ssh'ed to.
