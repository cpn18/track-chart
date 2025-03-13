import React, { useState, useEffect } from 'react';
import './IMU.css';
import '../App.css';
import Footer from '../components/Footer';

/**
 * IMU Page
 * image representing an IMU
 * info for IMU (pitch, roll, CPU temp)
 */

const IMU = () => {
  const [currentTime, setCurrentTime] = useState(new Date()); // store current system time
  const [showZero, setShowZero] = useState(false); 
  const [imuData, setImuData] = useState({
    pitch: 0,
    roll: 0,
    cpuTemp: 49, // ex: starting temperature (change this to be real-time)
  });

  /**
   * useEffect
   * interval to update currentTime every sec.
   * prevent mem leak, clean up interval when comp. is unmounted.
   */
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer); // cleanup on unmount
  }, []);

  /**
   * reset IMU data to zero when the zero is clicked.
   */
  const handleZero = () => {
    setImuData({
      pitch: 0,
      roll: 0,
      cpuTemp: imuData.cpuTemp, // retain temp as it doesn't reset
    });
  };

  const toggleZero = () => {
    setShowZero(!showZero);
  };

  return (
    <div className="imu-container">
      <img
        src={`IMUexample.png`}
        alt="IMU Example"
        className="imu-image"
      />

      {/* show cur date and time */}
      <p className="imu-timestamp">
        IMU as of: {currentTime.toLocaleDateString()} {currentTime.toLocaleTimeString()}
      </p>

      {/* info box for IMU numbers */}
      <div className="info-box-container">
        <h2 className="info-box-title">INFORMATION:</h2>
        {/* 2x2 grid for pitch, roll, temp, and zero out IMU */}
        <div className="info-box-grid">
          <div className="info-box-item">Pitch: {imuData.pitch}°</div>
          <div className="info-box-item">Roll: {imuData.roll}°</div>
          <div className="info-box-item">CPU Temp: {imuData.cpuTemp}°C</div>
          <button className="imu-zero-button" onClick={toggleZero} >
            ZERO
          </button>
        </div>
      </div>

      {showZero && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h1>Zero IMU:</h1>
              <p>
                Are you sure you'd like to zero the IMU?
              </p>
              <div className="modal-buttons">
                <button className="modal-button">
                  ZERO
                </button>
                <button className="modal-button cancel" onClick={toggleZero}>
                  CANCEL
                </button>
              </div>
          </div>
        </div>
      )}

      <Footer />
    </div>
  );
};

export default IMU;
