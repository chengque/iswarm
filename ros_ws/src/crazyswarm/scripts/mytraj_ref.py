#!/usr/bin/env python
import numpy as np
from pycrazyswarm import *
import rospy
import uav_trajectory
import time
from crazyflie_driver.msg import state_tg
import datetime

if __name__ == '__main__':
    try:
        swarm = Crazyswarm()
        timeHelper = swarm.timeHelper
        allcfs = swarm.allcfs

        traj1 = uav_trajectory.Trajectory()
        traj1.loadcsv("figure8.csv")

        dt = 0.02
        tt = traj1.duration
        trise = 2
        t=0

        state_tmp = state_tg()
        time.sleep(2)

        trise=0.1
        lst=datetime.datetime.now()
        while t<trise:
            while (datetime.datetime.now()-lst).total_seconds()<dt:
                pass
            lst=datetime.datetime.now()
            t=t+dt
            for cf in allcfs.crazyflies:
                state_tmp.p_x = 0
                state_tmp.p_y = 0
                state_tmp.p_z = t*10-1
                state_tmp.v_x = 0
                state_tmp.v_y = 0
                state_tmp.v_z = 0
                state_tmp.a_x = 0
                state_tmp.a_y = 0
                state_tmp.a_z = 0
                cf.a_flie_pub_traj_ref.publish(state_tmp)


        trise=1
        t=0

        lst=datetime.datetime.now()
        while t<trise:
            while (datetime.datetime.now()-lst).total_seconds()<dt:
                pass
            lst=datetime.datetime.now()
            t=t+dt
            for cf in allcfs.crazyflies:
                h = 1;
                state_tmp.p_x = 0
                state_tmp.p_y = 0
                state_tmp.p_z = h *t
                state_tmp.v_x = 0
                state_tmp.v_y = 0
                state_tmp.v_z = 0
                state_tmp.a_x = 0
                state_tmp.a_y = 0
                state_tmp.a_z = 0
                cf.a_flie_pub_traj_ref.publish(state_tmp)

        timeHelper.sleep(3)

        t = 0
        lst=datetime.datetime.now()
        while t < tt :
            while (datetime.datetime.now()-lst).total_seconds()<dt:
                pass
            lst=datetime.datetime.now()
            for cf in allcfs.crazyflies:
                state_tmp.p_x = traj1.eval(t).pos[0]
                state_tmp.p_y = traj1.eval(t).pos[1]
                state_tmp.p_z = 1
                state_tmp.v_x = traj1.eval(t).vel[0]
                state_tmp.v_y = traj1.eval(t).vel[1]
                state_tmp.v_z = traj1.eval(t).vel[2]
                state_tmp.a_x = traj1.eval(t).acc[0]
                state_tmp.a_y = traj1.eval(t).acc[1]
                state_tmp.a_z = traj1.eval(t).acc[2]
                cf.a_flie_pub_traj_ref.publish(state_tmp)
            t=t+dt/2

        lst=datetime.datetime.now()
        while t < tt + 2 :
            while (datetime.datetime.now()-lst).total_seconds()<dt:
                pass
            lst=datetime.datetime.now()
            t=t+dt/2
            for cf in allcfs.crazyflies:
                h = 1
                u = (t - tt)/2
                state_tmp.p_x = 0
                state_tmp.p_y = 0
                state_tmp.p_z = h*(1-u) + 0.1*u
                state_tmp.v_x = 0
                state_tmp.v_y = 0
                state_tmp.v_z = 0
                state_tmp.a_x = 0
                state_tmp.a_y = 0
                state_tmp.a_z = 0
                cf.a_flie_pub_traj_ref.publish(state_tmp)

        lst=datetime.datetime.now()
        while t < tt + 5 :
            while (datetime.datetime.now()-lst).total_seconds()<dt:
                pass
            lst=datetime.datetime.now()
            t=t+dt/2
            for cf in allcfs.crazyflies:
                state_tmp.p_x = 0
                state_tmp.p_y = 0
                state_tmp.p_z = -1
                state_tmp.v_x = 0
                state_tmp.v_y = 0
                state_tmp.v_z = 0
                state_tmp.a_x = 0
                state_tmp.a_y = 0
                state_tmp.a_z = 0
                cf.a_flie_pub_traj_ref.publish(state_tmp)

    except rospy.ROSInterruptException:
        pass


