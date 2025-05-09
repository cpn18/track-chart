import React, { useState, useEffect } from 'react';
import './IMU.css';
import '../App.css';
import Footer from '../components/Footer';
import Gauge from '../components/IMU/Gauge'

const IMU = () => {
  const [enabled, setEnabled] = useState(true);
  const [config, setConfig] = useState(null);
  const [pitch, setPitch] = useState(null);
  const [roll, setRoll] = useState(null);
  const [temp, setTemp] = useState(null);
  const [time, setTime] = useState(null);
  const [showZero, setShowZero] = useState(false); 
  const [acc_x, setAcc_x] = useState(false);
  const [acc_y, setAcc_y] = useState(false);
  const [acc_z, setAcc_z] = useState(false);
  


  useEffect(() => {
    fetch('/config')
      .then((res) => res.json())
      .then((data) => {
        setConfig(data);
        setEnabled(Boolean(data.imu?.enable));
        console.log('Config fetched');
      })
      .catch((err) => {
        console.error('Error fetching config:', err);
    });

    if (enabled) {
      // Initialize SSE connection to gps_stream
      const imuStream = new EventSource("/packets?count=1000");
      imuStream.addEventListener("pirail_ATT", handleDataUpdate);
      
        imuStream.onopen = function() {
          console.log("imu connection opened");
        };
  
        imuStream.onerror = function() {
          console.log("imu connection error");
        };
  
        return () => {
          imuStream.close();
        };
      }
    
    }, []);
  
  const handleDataUpdate = (event) => {
    var att = JSON.parse(event.data);
    console.log(att);
    // Pitch
    if (att.pitch != undefined) {
      setPitch(att.pitch.toFixed(3))
    }
    // Roll
    if (att.roll != undefined) {
      setRoll(att.roll.toFixed(3));
    }
    // CPU Temp
    if (att.temp != undefined) {
      setTemp(att.temp.toFixed(0));
    }
    // Time
    if (att.time != undefined) {
      setTime(att.time.split('T')[1].split('.')[0])
    }
    if (att.acc_x != undefined) {
      setAcc_x(att.acc_x);
    }
    if (att.acc_y != undefined) {
      setAcc_y(att.acc_y);
    }
    if (att.acc_z != undefined) {
      setAcc_z(att.acc_z);
    }
  }

  const handleZero = () => {
    // TODO: Make request to /IMUzero endpoint, zeroing will be handled on server side
  };

  const toggleZero = () => {
    setShowZero(!showZero);
  };

  return (
    <div className="imu-container">
      <div className="nav-container"></div>
      {enabled ?
      <div>
        <Gauge att={ {pitch, roll, acc_x, acc_y, acc_z } } decay={5} />
      </div>
      : <div>IMU disabled - turn on in settings</div>}

      <p className="imu-timestamp">
        IMU as of: {time}Z
      </p>

      <div className="info-box-container">
        <div className="info-box-grid">
          <div className="info-box-item">Pitch: {pitch ? `${pitch}°` : 'Loading...'}</div>
          <div className="info-box-item">Roll: {roll ? `${roll}°` : 'Loading...'}</div>
          <div className="info-box-item">CPU Temp: {temp ? `${temp}°` : 'Loading...'}</div>
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
