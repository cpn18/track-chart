import React, { createContext, useContext, useState } from 'react';

// new context for managing sensor status
const StatusContext = createContext();

/**
 * StatusProvider Comp.
 * state management for sensors
 * react context API -> share status values across app
 */
export const StatusProvider = ({ children }) => {
  // state for each sensor (+ its setter)
  const [gps, setGps] = useState(true); // GPS sensor status
  const [imu, setImu] = useState(true); // IMU sensor status
  const [gpsimu, setGpsimu] = useState(true); // GPS and IMU status
  const [lidar360, setLidar360] = useState(true); // 360-degree LIDAR status
  const [hps3d, setHps3d] = useState(true); // HPS 3D LIDAR status
  const [lpcm, setLpcm] = useState(true); // LPCM sensor status

  // overall LIDAR status based on individual LIDAR sensors
  const isLidarOn = lidar360 || hps3d; // if either LIDAR is on, LIDAR is a go!

  return (
    <StatusContext.Provider
      value={{
        gps,
        setGps,
        imu,
        setImu,
        gpsimu,
        setGpsimu,
        lidar360,
        setLidar360,
        hps3d,
        setHps3d,
        lpcm,
        setLpcm,
        isLidarOn,
      }}
    >
      {children} {/* child components that consume this context */}
    </StatusContext.Provider>
  );
};

/**
 * hook to use the StatusContext
 * components can access sensor status values and setter funcs.
 */
export const useStatus = () => useContext(StatusContext);