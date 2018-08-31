//
// Created by chengque on 18-8-21.
//

#ifndef PROJECT_CFTRACKER_H
#define PROJECT_CFTRACKER_H
#include <pcl/point_cloud.h>
#include <pcl/point_types.h>
#include <pcl/common/transforms.h>

using Point = pcl::PointXYZ;
using Cloud = pcl::PointCloud<Point>;

class cftracker {

public:
    void update(Cloud::Ptr pointCloud);

};


#endif //PROJECT_CFTRACKER_H
