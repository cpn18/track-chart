// src/StatusContext.js
import React, { createContext, useContext, useState } from 'react';

const StatusContext = createContext();

export const StatusProvider = ({ children }) => {
  const [gps, setGps] = useState(false);
  const [imu, setImu] = useState(false);
  const [gpsimu, setGpsimu] = useState(false);
  const [lidar360, setLidar360] = useState(false);
  const [hps3d, setHps3d] = useState(false);
  const [lpcm, setLpcm] = useState(false);

  const isLidarOn = lidar360 || hps3d; // Either LIDAR being on means LIDAR status is "ON"

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
      {children}
    </StatusContext.Provider>
  );
};

export const useStatus = () => useContext(StatusContext);
