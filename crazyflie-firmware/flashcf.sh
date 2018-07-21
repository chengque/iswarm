#!/bin/bash
cd '/home/chengque/workspace/catkin_ws/src/crazyswarm/crazyflie-firmware' 
make PLATFORM=CF2
cd '/mnt/disk/workspace/src/crazyflie-clients-python' 
cfloader flash '/home/chengque/workspace/catkin_ws/src/crazyswarm/crazyflie-firmware/cf2.bin' stm32-fw
