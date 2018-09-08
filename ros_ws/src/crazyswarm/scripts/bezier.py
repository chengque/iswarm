#!/usr/bin/env python
import numpy as np
from pycrazyswarm import *
import rospy
import uav_trajectory
import time
from crazyflie_driver.msg import state_tg
import datetime
import matplotlib.pyplot as plt
import scipy.io as scio
'''
plt.ion()
plt.figure()
for i in range(100):
    plt.plot([i], [i], 'o')
    plt.draw()
    plt.pause(0.0001)
'''
sim=False

if __name__ == '__main__':
    try:
        swarm = Crazyswarm()
        timeHelper = swarm.timeHelper
        allcfs = swarm.allcfs
        trj = scio.loadmat("trj.mat")
        print "start"
        if sim==True:
            plt.ion()
            fig=plt.figure()
            plt.axis([-2,2,-2,1])




        dt = 0.02
        print  "figure"
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
                if not sim:
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
                if not sim:
                    cf.a_flie_pub_traj_ref.publish(state_tmp)

        timeHelper.sleep(3)

        print "now start plan"
        t = 0
        index=0
        flag=0
        lst=datetime.datetime.now()
        while flag<1:
            flag=1
            while (datetime.datetime.now()-lst).total_seconds()<dt:
                pass
            lst=datetime.datetime.now()
            #if(sim==True):
                #ax.cla()

            for cf in allcfs.crazyflies:
                p=trj["cf"+str(cf.id)]
                ti=index
                if(ti>=len(p[:,0])):
                    ti=len(p[:,0])-1
                else:
                    flag=flag-1
                state_tmp.p_x = trj["cf"+str(cf.id)][ti,0]
                state_tmp.p_y = trj["cf"+str(cf.id)][ti,1]
                state_tmp.p_z = 1
                state_tmp.v_x = 0
                state_tmp.v_y = 0
                state_tmp.v_z = 0
                state_tmp.a_x = 0
                state_tmp.a_y = 0
                state_tmp.a_z = 0
                if not sim:
                    cf.a_flie_pub_traj_ref.publish(state_tmp)
                if(sim==True):
                    plt.plot(p[ti,0]+cf.initialPosition[0],p[ti,1]+cf.initialPosition[1],'o')
            if (sim == True):
                plt.draw()
                index=index+9
            t=t+dt/2
            #lst = datetime.datetime.now()
            index=index+1


        lst=datetime.datetime.now()

        t=0
        while t <2 :
            while (datetime.datetime.now()-lst).total_seconds()<dt:
                pass
            lst=datetime.datetime.now()
            t=t+dt/2
            for cf in allcfs.crazyflies:
                h = 1
                u = (t)/2
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
        t=0
        while t < 5 :
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