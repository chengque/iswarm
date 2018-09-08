#!/usr/bin/env python


import sys
import yaml
import rospy
import numpy as np
import time
from std_srvs.srv import Empty
from crazyflie_driver.srv import *
from crazyflie_driver.srv import TrajectoryRef
from crazyflie_driver.msg import TrajectoryPolynomialPiece
from tf import TransformListener

from crazyflie_driver.msg import state_tg

def arrayToGeometryPoint(a):
    return geometry_msgs.msg.Point(a[0], a[1], a[2])

class TimeHelper:
    def __init__(self):
        pass
        #rospy.wait_for_service("/next_phase")
        #self.nextPhase = rospy.ServiceProxy("/next_phase", Empty)

    def time(self):
        return time.time()

    def sleep(self, duration):
        time.sleep(duration)

    def nextPhase(self):
        self.nextPhase()


class Crazyflie:
    def __init__(self, id, initialPosition, tf):
        self.id = id
        print "initialize cf "+ str(self.id)
        prefix = "/cf" + str(id)
        self.initialPosition = np.array(initialPosition)

        self.tf = tf
        '''
        rospy.wait_for_service(prefix + "/set_group_mask")
        self.setGroupMaskService = rospy.ServiceProxy(prefix + "/set_group_mask", SetGroupMask)
        rospy.wait_for_service(prefix + "/takeoff")
        self.takeoffService = rospy.ServiceProxy(prefix + "/takeoff", Takeoff)
        rospy.wait_for_service(prefix + "/land")
        self.landService = rospy.ServiceProxy(prefix + "/land", Land)
        # rospy.wait_for_service(prefix + "/stop")
        # self.stopService = rospy.ServiceProxy(prefix + "/stop", Stop)
        rospy.wait_for_service(prefix + "/go_to")
        self.goToService = rospy.ServiceProxy(prefix + "/go_to", GoTo)
        rospy.wait_for_service(prefix + "/upload_trajectory")
        self.uploadTrajectoryService = rospy.ServiceProxy(prefix + "/upload_trajectory", UploadTrajectory)
        # rospy.wait_for_service(prefix + "/start_trajectory")
        # self.startTrajectoryService = rospy.ServiceProxy(prefix + "/start_trajectory", StartTrajectory)
        rospy.wait_for_service(prefix + "/update_params")
        self.updateParamsService = rospy.ServiceProxy(prefix + "/update_params", UpdateParams)
        '''
        #rospy.wait_for_service(prefix + "/set_trajectory_ref")
        #self.trajectoryRefService = rospy.ServiceProxy(prefix + "/set_trajectory_ref", TrajectoryRef)
        self.a_flie_pub_traj_ref = rospy.Publisher(prefix + "/set_state",state_tg,queue_size=10)


    def setGroupMask(self, groupMask):
        self.setGroupMaskService(groupMask)

    def takeoff(self, targetHeight, duration, groupMask = 0):
        self.takeoffService(groupMask, targetHeight, rospy.Duration.from_sec(duration))

    def land(self, targetHeight, duration, groupMask = 0):
        self.landService(groupMask, targetHeight, rospy.Duration.from_sec(duration))

    def stop(self, groupMask = 0):
        self.stopService(groupMask)

    def goTo(self, goal, yaw, duration, relative = False, groupMask = 0):
        gp = arrayToGeometryPoint(goal)
        self.goToService(groupMask, relative, gp, yaw, rospy.Duration.from_sec(duration))

    def uploadTrajectory(self, trajectoryId, pieceOffset, trajectory):
        pieces = []
        for poly in trajectory.polynomials:
            piece = TrajectoryPolynomialPiece()
            piece.duration = rospy.Duration.from_sec(poly.duration)
            piece.poly_x   = poly.px.p
            piece.poly_y   = poly.py.p
            piece.poly_z   = poly.pz.p
            piece.poly_yaw = poly.pyaw.p
            pieces.append(piece)
        self.uploadTrajectoryService(trajectoryId, pieceOffset, pieces)

    def startTrajectory(self, trajectoryId, timescale = 1.0, reverse = False, relative = True, groupMask = 0):
        self.startTrajectoryService(groupMask, trajectoryId, timescale, reverse, relative)

    def position(self):
        self.tf.waitForTransform("/world", "/cf" + str(self.id), rospy.Time(0), rospy.Duration(10))
        position, quaternion = self.tf.lookupTransform("/world", "/cf" + str(self.id), rospy.Time(0))
        return np.array(position)

    def getParam(self, name):
        return rospy.get_param(self.prefix + "/" + name)

    def setParam(self, name, value):
        rospy.set_param(self.prefix + "/" + name, value)
        self.updateParamsService([name])

    def setParams(self, params):
        for name, value in params.iteritems():
            rospy.set_param(self.prefix + "/" + name, value)
        self.updateParamsService(params.keys())




class CrazyflieServer:
    def __init__(self):
        rospy.init_node("CrazyflieAPI", anonymous=False)
        print "wait"
        '''
        rospy.wait_for_service("/emergency")
        self.emergencyService = rospy.ServiceProxy("/emergency", Empty)
        print "ok"
        rospy.wait_for_service("/takeoff")
        self.takeoffService = rospy.ServiceProxy("/takeoff", Takeoff)
        rospy.wait_for_service("/land")
        self.landService = rospy.ServiceProxy("/land", Land)
        # rospy.wait_for_service("/stop")
        # self.stopService = rospy.ServiceProxy("/stop", Stop)
        # rospy.wait_for_service("/go_to")
        # self.goToService = rospy.ServiceProxy("/go_to", GoTo)
        rospy.wait_for_service("/start_trajectory");
        self.startTrajectoryService = rospy.ServiceProxy("/start_trajectory", StartTrajectory)
        # rospy.wait_for_service("/update_params")
        # self.updateParamsService = rospy.ServiceProxy("/update_params", UpdateParams)
        rospy.wait_for_service("/set_trajectory_ref")
        self.trajectoryRefService = rospy.ServiceProxy("/set_trajectory_ref", TrajectoryRef)
        '''
        print "okk"

        with open("../launch/crazyflies.yaml", 'r') as ymlfile:
            cfg = yaml.load(ymlfile)
            print cfg

        self.tf = TransformListener()

        self.crazyflies = []
        self.crazyfliesById = dict()
        i=0
        for crazyflie in cfg["crazyflies"]:
            id = int(crazyflie["id"])
            initialPosition = crazyflie["initialPosition"]
            cf = Crazyflie(id, initialPosition, self.tf)
            self.crazyflies.append(cf)
            self.crazyfliesById[id] = cf
            i=i+1
        print "totoal "+str(i)

    def emergency(self):
        self.emergencyService()

    def takeoff(self, targetHeight, duration, groupMask = 0):
        self.takeoffService(groupMask, targetHeight, rospy.Duration.from_sec(duration))

    def land(self, targetHeight, duration, groupMask = 0):
        self.landService(groupMask, targetHeight, rospy.Duration.from_sec(duration))

    # def stop(self, groupMask = 0):
    #     self.stopService(groupMask)

    # def goTo(self, goal, yaw, duration, groupMask = 0):
    #     gp = arrayToGeometryPoint(goal)
    #     self.goToService(groupMask, True, gp, yaw, rospy.Duration.from_sec(duration))

    def startTrajectory(self, trajectoryId, timescale = 1.0, reverse = False, relative = True, groupMask = 0):
        self.startTrajectoryService(groupMask, trajectoryId, timescale, reverse, relative)


    def setTrajectoryRef(self, refTrj):
        trj=TrajectoryRefRequest()
        trj.x=refTrj[0]
        trj.y=refTrj[1]
        trj.z=refTrj[2]
        trj.vx=refTrj[3]
        trj.vy=refTrj[4]
        trj.vz=refTrj[5]
        trj.ax=refTrj[6]
        trj.ay=refTrj[7]
        trj.az=refTrj[8]
        self.trajectoryRefService(trj)
        #print "cf "+str(self.id)+" set trajecotry"

    # def setParam(self, name, value, group = 0):
    #     rospy.set_param("/cfgroup" + str(group) + "/" + name, value)
    #     self.updateParamsService(group, [name])
