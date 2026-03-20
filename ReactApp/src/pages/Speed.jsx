import React, { useState, useEffect } from 'react';
import './IMU.css';
import '../App.css';
import Footer from '../components/Footer';
import SpeedChart from '../components/IMU/SpeedChart'

const Speed = () => {
  const [enabled, setEnabled] = useState(true);
  const [config, setConfig] = useState(null);
  const [temp, setTemp] = useState(null);
  const [time, setTime] = useState([]);
  const [showZero, setShowZero] = useState(false);
  const [speed, setSpeed] = useState([]);
  const [gyroYangle, setgyroYangle] = useState([]);
  const [acc_z, setAcc_z] = useState([]);



  useEffect(() => {
    fetch('/config')
      .then((res) => res.json())
      .then((data) => {
        setConfig(data);
        setEnabled(Boolean(data.imu?.enable) || Boolean(data.sim?.enable));
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
    // console.log(event)
    var att = JSON.parse(event.data);
    // console.log(att);

    // Speed
    if (att.speed != undefined) {
      if (speed.length >= 100) {
        speed.shift()
      }
      speed.push(att.speed.toFixed(3))
    }
    // Gyroscopic Y angle
    if (att.gyro_y_angle != undefined) {
      if (gyroYangle.length >= 100) {
        gyroYangle.shift()
      }
      gyroYangle.push(att.gyro_y_angle.toFixed(3));
    }
    // Acc z
    if (att.acc_z != undefined) {
      if (acc_z.length >= 100) {
        acc_z.shift()
      }
      acc_z.push(att.acc_z.toFixed(3));
    }
    // CPU Temp
    if (att.temp != undefined) {
      setTemp(att.temp.toFixed(0));
    }
    // Time
    if (att.time != undefined) {
      if (time.length >= 100) {
        time.shift()
      }
      time.push(att.time.split('T')[1].split('.')[0])
    }
  }

  const handleZero = () => {
    fetch("/imu/zero", {
	    "method": "PUT"
    })
    .then(response => response.json())
    .then((data) => {
	    console.log(data)
	    toggleZero()
    })
  };

  const toggleZero = () => {
    setShowZero(!showZero);
  };

  return (
    <div className="imu-container">
      <div className="nav-container"></div>
      {enabled ?
      <div>
        <SpeedChart att={ {speed, gyroYangle, acc_z, time } } />
      </div>
      : <div>IMU disabled - turn on in settings</div>}

      <div className="info-box-container">
        <div className="info-box-grid">
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
                <button className="modal-button" onClick={handleZero}>
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

export default Speed;
