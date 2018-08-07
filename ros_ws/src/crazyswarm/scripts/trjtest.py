#!/usr/bin/env python

import numpy as np

from pycrazyswarm import *
import uav_trajectory
import time

if __name__ == "__main__":
    swarm = Crazyswarm()

    timeHelper = swarm.timeHelper
    allcfs = swarm.allcfs

    for cf in allcfs.crazyflies:
        cf.setTrajectoryRef([0, 0, 0.5, 0, 0, 0, 0, 0, 0]);

    timeHelper.sleep(5)

    for cf in allcfs.crazyflies:
        cf.setTrajectoryRef([0, 0, 0.0, 0, 0, 0, 0, 0, 0]);
    time.sleep(100)





