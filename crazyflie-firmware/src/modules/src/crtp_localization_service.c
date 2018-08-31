/**
 *    ||          ____  _ __
 * +------+      / __ )(_) /_______________ _____  ___
 * | 0xBC |     / __  / / __/ ___/ ___/ __ `/_  / / _ \
 * +------+    / /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
 *  ||  ||    /_____/_/\__/\___/_/   \__,_/ /___/\___/
 *
 * Crazyflie Firmware
 *
 * Copyright (C) 2011-2012 Bitcraze AB
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, in version 3.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <http://www.gnu.org/licenses/>.
 *
 *
 */
#include <string.h>
#include <stdint.h>

#include "FreeRTOS.h"
#include "task.h"

#include "crtp.h"
#include "crtp_localization_service.h"
#include "log.h"
#include "param.h"

#include "stabilizer_types.h"
#include "stabilizer.h"
#include "configblock.h"

#include "locodeck.h"

#include "estimator_kalman.h"
#include "position_external.h"
#include "commander.h"
#define NBR_OF_RANGES_IN_PACKET   5
#define DEFAULT_EMERGENCY_STOP_TIMEOUT (1 * RATE_MAIN_LOOP)
typedef enum
{
  EXT_POSITION        = 0,
  GENERIC_TYPE        = 1,
  EXT_POSITION_PACKED = 2,
  ATTSP               = 3,

} locsrvChannels_t;

typedef enum
{
    ATT_SETPOINT_PACKED = 2,
}attSpChannels_t;

typedef struct
{
  uint8_t type;
  struct
  {
    uint8_t id;
    float range;
  } __attribute__((packed)) ranges[NBR_OF_RANGES_IN_PACKET];
} __attribute__((packed)) rangePacket;

// up to 4 items per CRTP packet
typedef struct {
  uint8_t id; // last 8 bit of the Crazyflie address
  int16_t x; // mm
  int16_t y; // mm
  int16_t z; // mm
} __attribute__((packed)) extPositionPackedItem;

typedef struct {
    uint8_t id; // last 8 bit of the Crazyflie address
    int8_t roll; // deg
    int8_t pitch; // deg
    int8_t yaw; // deg
    int16_t thrust;
} __attribute__((packed)) attSetpointPackedItem;

/**
 * Position data cache
 */
typedef struct
{
  struct CrtpExtPosition targetVal[2];
  bool activeSide;
  uint32_t timestamp; // FreeRTOS ticks
} ExtPositionCache;

/**
 * Attitute setpoint cache
 */
typedef struct
{
    struct CrtpAttSp targetVal[2];
    bool activeSide;
    uint32_t timestamp; // FreeRTOS ticks
} AttSpCache;


// Struct for logging position information
static positionMeasurement_t ext_pos;
static ExtPositionCache crtpExtPosCache;
//static attituteSetpoint_t att_sp;
static AttSpCache crtpAttSpCache;
static CRTPPacket pkRange;
static uint8_t rangeIndex;
static bool enableRangeStreamFloat = false;
static float extPosStdDev = 0.01;
static bool isInit = false;
static uint8_t my_id;

static void locSrvCrtpCB(CRTPPacket* pk);
//static void attSpSrvCrtpCB(CRTPPacket* pk);

static void extPositionHandler(CRTPPacket* pk);
static void genericLocHandle(CRTPPacket* pk);
static void extPositionPackedHandler(CRTPPacket* pk);
static void attSetpointPackedHandler(CRTPPacket* pk);


void locSrvInit()
{
  if (isInit) {
    return;
  }

  uint64_t address = configblockGetRadioAddress();
  my_id = address & 0xFF;

  crtpRegisterPortCB(CRTP_PORT_LOCALIZATION, locSrvCrtpCB);
//  crtpRegisterPortCB(CRTP_PORT_ATTSETPOINT, attSpSrvCrtpCB);
  isInit = true;
}

//static void attSpSrvCrtpCB(CRTPPacket* pk)
//{
//  switch (pk->channel)
//  {
//    case ATT_SETPOINT_PACKED:
//      attSetpointPackedHandler(pk);
//    default:
//      break;
//  }
//}

static void locSrvCrtpCB(CRTPPacket* pk)
{
  switch (pk->channel)
  {
    case EXT_POSITION:
      extPositionHandler(pk);
      break;
    case GENERIC_TYPE:
      genericLocHandle(pk);
    case EXT_POSITION_PACKED:
      extPositionPackedHandler(pk);
    case ATTSP:
        attSetpointPackedHandler(pk);
    default:
      break;
  }
}

static void extPositionHandler(CRTPPacket* pk)
{
  crtpExtPosCache.targetVal[!crtpExtPosCache.activeSide] = *((struct CrtpExtPosition*)pk->data);
  crtpExtPosCache.activeSide = !crtpExtPosCache.activeSide;
  crtpExtPosCache.timestamp = xTaskGetTickCount();
}

static void genericLocHandle(CRTPPacket* pk)
{
  uint8_t type = pk->data[0];
  if (pk->size < 1) return;

  if (type == LPS_SHORT_LPP_PACKET && pk->size >= 2) {
    bool success = lpsSendLppShort(pk->data[1], &pk->data[2], pk->size-2);

    pk->port = CRTP_PORT_LOCALIZATION;
    pk->channel = GENERIC_TYPE;
    pk->size = 3;
    pk->data[2] = success?1:0;
    crtpSendPacket(pk);
  } else if (type == EMERGENCY_STOP) {
    stabilizerSetEmergencyStop();
  } else if (type == EMERGENCY_STOP_WATCHDOG) {
    stabilizerSetEmergencyStopTimeout(DEFAULT_EMERGENCY_STOP_TIMEOUT);
  }
}

static void extPositionPackedHandler(CRTPPacket* pk)
{
  uint8_t numItems = pk->size / sizeof(extPositionPackedItem);
  for (uint8_t i = 0; i < numItems; ++i) {
    const extPositionPackedItem* item = (const extPositionPackedItem*)&pk->data[i * sizeof(extPositionPackedItem)];
    if (item->id == my_id) {
      struct CrtpExtPosition position;
      position.x = item->x / 1000.0f;
      position.y = item->y / 1000.0f;
      position.z = item->z / 1000.0f;

      crtpExtPosCache.targetVal[!crtpExtPosCache.activeSide] = position;
      crtpExtPosCache.activeSide = !crtpExtPosCache.activeSide;
      crtpExtPosCache.timestamp = xTaskGetTickCount();

      break;
    }
  }
}
static void attSetpointPackedHandler(CRTPPacket* pk)
{
  uint8_t numItems = pk->size / sizeof(attSetpointPackedItem);
  for (uint8_t i = 0; i < numItems; ++i) {
    const attSetpointPackedItem* item = (const attSetpointPackedItem*)&pk->data[i * sizeof(attSetpointPackedItem)];
    if ((item->id == my_id) && (item->yaw==0x55)) {
      struct CrtpAttSp attSp;
      attSp.roll = item->roll/5.0f;
      attSp.pitch = (item->pitch)/5.0f;
      attSp.thrust = item->thrust*10.0f;
//      attSp.yaw = item->yaw;

      crtpAttSpCache.targetVal[!crtpAttSpCache.activeSide] = attSp;
      crtpAttSpCache.activeSide = !crtpAttSpCache.activeSide;
      crtpAttSpCache.timestamp = xTaskGetTickCount();

      break;
    }
  }
}


bool getExtPosition(state_t *state)
{
  if (!estimatorKalmanTest()) {
    return false;
  }

  // Only use position information if it's valid and recent
  if ((xTaskGetTickCount() - crtpExtPosCache.timestamp) < M2T(5)) {
    // Get the updated position from the mocap
    ext_pos.x = crtpExtPosCache.targetVal[crtpExtPosCache.activeSide].x;
    ext_pos.y = crtpExtPosCache.targetVal[crtpExtPosCache.activeSide].y;
    ext_pos.z = crtpExtPosCache.targetVal[crtpExtPosCache.activeSide].z;
    ext_pos.stdDev = extPosStdDev;
    estimatorKalmanEnqueuePosition(&ext_pos);

    return true;
  }

  // allow the official kalman filter to work with Crazyswarm position service
  float x, y, z, q0, q1, q2, q3, vx, vy, vz;
  uint16_t last_time_in_ms;
  positionExternalGetLastData(
    &x, &y, &z,
    &q0, &q1, &q2, &q3,
    &vx, &vy, &vz,
    &last_time_in_ms);
  if (positionExternalFresh2) {
    ext_pos.x = x;
    ext_pos.y = y;
    ext_pos.z = z;
    ext_pos.stdDev = extPosStdDev;
    estimatorKalmanEnqueuePosition(&ext_pos);
    positionExternalFresh2 = false;
  }

  return false;
}


bool getAttSetpoint(setpoint_t *setpoint)
{
  /*if (!estimatorKalmanTest()) {
    return false;
  }*/

  // Only use position information if it's valid and recent
    uint32_t currentTime = xTaskGetTickCount();
    if ((currentTime - crtpAttSpCache.timestamp) > COMMANDER_WDT_TIMEOUT_SHUTDOWN) {
      setpoint->mode.x = modeDisable;
      setpoint->mode.y = modeDisable;
      setpoint->mode.z = modeDisable;
      setpoint->mode.roll = modeAbs;
      setpoint->mode.pitch = modeAbs;
      setpoint->mode.yaw = modeAbs;

      setpoint->attitude.roll = 0.0f;
      setpoint->attitude.pitch = 0.0f;
      setpoint->attitudeRate.yaw = 0.0f;
      setpoint->thrust = 0.0f;
        return false;
    }
  if ((xTaskGetTickCount() - crtpAttSpCache.timestamp) < M2T(5)) {
    // Get the updated attitude setpoint from the pc
    setpoint->mode.x = modeDisable;
    setpoint->mode.y = modeDisable;
    setpoint->mode.z = modeDisable;
    setpoint->mode.roll = modeAbs;
    setpoint->mode.pitch = modeAbs;
    setpoint->mode.yaw = modeAbs;

    setpoint->attitude.roll = crtpAttSpCache.targetVal[crtpAttSpCache.activeSide].roll;
    setpoint->attitude.pitch = crtpAttSpCache.targetVal[crtpAttSpCache.activeSide].pitch;
    setpoint->attitude.yaw = 0.0f;//192.6f; crtpAttSpCache.targetVal[crtpAttSpCache.activeSide].yaw;
    setpoint->thrust = crtpAttSpCache.targetVal[crtpAttSpCache.activeSide].thrust;
//    att_sp.stdDev = extPosStdDev;
//    estimatorKalmanEnqueuePosition(&att_sp); //TODO: modify

    return true;
  }
  return false;
  // allow the official kalman filter to work with Crazyswarm position service
//  float x, y, z, q0, q1, q2, q3, vx, vy, vz;
//  uint16_t last_time_in_ms;
//  positionExternalGetLastData(
//          &x, &y, &z,
//          &q0, &q1, &q2, &q3,
//          &vx, &vy, &vz,
//          &last_time_in_ms);
//  if (positionExternalFresh2) {
//    att_sp.roll  = x;
//    att_sp.pitch = y;
//    att_sp.yaw   = z;
//    att_sp.stdDev = extPosStdDev;
//    estimatorKalmanEnqueuePosition(&ext_pos);
//    positionExternalFresh2 = false;
//  }
//
//  return false;
}


void locSrvSendPacket(locsrv_t type, uint8_t *data, uint8_t length)
{
  CRTPPacket pk;

  ASSERT(length < CRTP_MAX_DATA_SIZE);

  pk.port = CRTP_PORT_LOCALIZATION;
  pk.channel = GENERIC_TYPE;
  memcpy(pk.data, data, length);
  crtpSendPacket(&pk);
}

void locSrvSendRangeFloat(uint8_t id, float range)
{
  rangePacket *rp = (rangePacket *)pkRange.data;

  ASSERT(rangeIndex <= NBR_OF_RANGES_IN_PACKET);

  if (enableRangeStreamFloat)
  {
    rp->ranges[rangeIndex].id = id;
    rp->ranges[rangeIndex].range = range;
    rangeIndex++;

    if (rangeIndex >= 5)
    {
      rp->type = RANGE_STREAM_FLOAT;
      pkRange.port = CRTP_PORT_LOCALIZATION;
      pkRange.channel = GENERIC_TYPE;
      pkRange.size = sizeof(rangePacket);
      crtpSendPacket(&pkRange);
      rangeIndex = 0;
    }
  }
}

LOG_GROUP_START(ext_pos)
  LOG_ADD(LOG_FLOAT, X, &ext_pos.x)
  LOG_ADD(LOG_FLOAT, Y, &ext_pos.y)
  LOG_ADD(LOG_FLOAT, Z, &ext_pos.z)
LOG_GROUP_STOP(ext_pos)

PARAM_GROUP_START(locSrv)
  PARAM_ADD(PARAM_UINT8, enRangeStreamFP32, &enableRangeStreamFloat)
  PARAM_ADD(PARAM_FLOAT, extPosStdDev, &extPosStdDev)
PARAM_GROUP_STOP(locSrv)
