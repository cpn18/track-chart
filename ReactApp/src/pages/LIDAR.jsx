// src/pages/LIDAR.jsx
import React, { useEffect, useState } from 'react';
import '../App.css';
import Footer from '../components/Footer';
import LidarView from '../components/LIDAR/LidarView';

const LIDAR = () => {
  const [enabled, setEnabled] = useState(false);
  const [config, setConfig] = useState(null);
  const [lidarData, setLidarData] = useState(null);

  useEffect(() => {
    // 1) fetch config
    fetch('/config')
      .then((res) => res.json())
      .then((data) => {
        setConfig(data);
        setEnabled(Boolean(data.lidar?.enable) || Boolean(data.hpslidar?.enable) || Boolean(data.sim?.enable));
        console.log('Config fetched for LIDAR, enabled=', data.lidar?.enable);
      })
      .catch((err) => {
        console.error('Error fetching config:', err);
      });

    // 2) open SSE
    const lidarStream = new EventSource('/packets?count=1000');
    lidarStream.addEventListener('pirail_LIDAR', handleDataUpdate);

    lidarStream.onopen = () => {
      console.log('LIDAR SSE connection opened');
    };

    lidarStream.onerror = () => {
      console.log('LIDAR SSE connection error');
      // handle error or close
    };

    // Cleanup
    return () => {
      lidarStream.close();
    };
  }, []);

  const handleDataUpdate = (event) => {
    const data = JSON.parse(event.data);
    console.log('LIDAR SSE data:', data);
    // Store the entire object (2D or 3D) in state
    setLidarData(data);
  };

  return (
    <div className="imu-container">
      <div className="nav-container"></div>
      
      {enabled ? (
        <LidarView lidarData={lidarData} />
      ) : (
        <div>LIDAR disabled – turn on in settings</div>
      )}

      <Footer />
    </div>
  );
};

export default LIDAR;
