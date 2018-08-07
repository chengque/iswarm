import numpy as np
from pycrazyswarm import *
import uav_trajectory
import time
import datetime

if __name__ == "__main__":
    swarm = Crazyswarm()
    timeHelper = swarm.timeHelper
    allcfs = swarm.allcfs

    traj1 = uav_trajectory.Trajectory()
    traj1.loadcsv("figure8.csv")

    dt = 0.02
    tt = traj1.duration
    t = 0

    trise=0.1
    lst=datetime.datetime.now()
    while t<trise:
        while (datetime.datetime.now()-lst).total_seconds()<dt:
            pass
        lst=datetime.datetime.now()
        t=t+dt
        for cf in allcfs.crazyflies:
            cf.setTrajectoryRef([0, 0, t*10-1, 0, 0, 0, 0, 0, 0]);

    trise=1
    t=0

    lst=datetime.datetime.now()
    while t<trise:
        while (datetime.datetime.now()-lst).total_seconds()<dt:
            pass
        lst=datetime.datetime.now()
        t=t+dt
        for cf in allcfs.crazyflies:
            cf.setTrajectoryRef([0, 0, t/2, 0, 0, 0, 0, 0, 0]);

    timeHelper.sleep(5)

    t=0
    lst=datetime.datetime.now()
    while t < tt :

    	pos = traj1.eval(t).pos
    	vel = traj1.eval(t).vel
    	acc = traj1.eval(t).acc
    	#traj_tmp = [pos[0], pos[1], pos[2],  vel[0], vel[1], vel[2], acc[0], acc[1], acc[2]]
        traj_tmp = [pos[0], pos[1], 0.5,  0, 0, 0, 0, 0, 0]
    	print t
    	print traj_tmp
    	for cf in allcfs.crazyflies:
        	cf.setTrajectoryRef(traj_tmp);
        while (datetime.datetime.now()-lst).total_seconds()<dt:
            pass
        lst=datetime.datetime.now()
        t=t+dt/2

    lst=datetime.datetime.now()
    t=0
    while t < tt :
    	pos = traj1.eval(t).pos
    	vel = traj1.eval(t).vel
    	acc = traj1.eval(t).acc
    	#traj_tmp = [-pos[0], -pos[1], pos[2],  -vel[0], -vel[1], vel[2], -acc[0], -acc[1], acc[2]]
        traj_tmp = [-pos[0], -pos[1], 0.5,  0, 0, 0, 0, 0, 0]
    	print t+tt
        print t
    	print traj_tmp
    	for cf in allcfs.crazyflies:
        	cf.setTrajectoryRef(traj_tmp);
        while (datetime.datetime.now()-lst).total_seconds()<dt:
            pass
        lst=datetime.datetime.now()
        t=t+dt/2


    for cf in allcfs.crazyflies:
        cf.setTrajectoryRef([0, 0, 0, 0, 0, 0, 0, 0, 0]);

    timeHelper.sleep(2)

    for cf in allcfs.crazyflies:
        cf.setTrajectoryRef([0, 0, -1, 0, 0, 0, 0, 0, 0]);
    
    time.sleep(100)

    TRIALS = 1
    TIMESCALE = 1.0


