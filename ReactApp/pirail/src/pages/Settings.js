// src/pages/Settings.js
import React from 'react';
import { useTheme } from '../ThemeContext';
import { useStatus } from '../StatusContext';
import { Link } from 'react-router-dom';
import './settings.css';

const Settings = () => {
  const { isDarkMode, toggleDarkMode } = useTheme();
  const { gps, imu, gpsimu, isLidarOn, lpcm } = useStatus();

  return (
    <div className="settings-container">
      <h3>BASIC SETTINGS:</h3>

      <div className="setting-item">
        <label>
          Dark Mode
          <input type="checkbox" checked={isDarkMode} onChange={toggleDarkMode} />
        </label>
      </div>

      <div className="setting-item">
        <label>
          Imperial Measurements
          <input type="checkbox" />
        </label>
      </div>

      <div className="setting-item">
        <label>
          Simulator
          <input type="checkbox" />
        </label>
      </div>

      {/* status */}
      <div className="status-section">
        <h3>STATUS:</h3>
        <div className="status-grid">
          <div className="status-item">
            <span>GPS:</span>
            <span className={gps ? 'status-on' : 'status-off'}>{gps ? 'ON' : 'OFF'}</span>
          </div>
          <div className="status-item">
            <span>LIDAR:</span>
            <span className={isLidarOn ? 'status-on' : 'status-off'}>{isLidarOn ? 'ON' : 'OFF'}</span>
          </div>
          <div className="status-item">
            <span>IMU:</span>
            <span className={imu ? 'status-on' : 'status-off'}>{imu ? 'ON' : 'OFF'}</span>
          </div>
          <div className="status-item">
            <span>LPCM:</span>
            <span className={lpcm ? 'status-on' : 'status-off'}>{lpcm ? 'ON' : 'OFF'}</span>
          </div>
          <div className="status-item gpu-temp">
            <span>GPU Temp:</span>
            <span className="gpu-temp-value">49°C</span>
          </div>
        </div>
      </div>

      <div className="setting-item">
        <h3>ACTIONS:</h3>
        <div className="button-group">
          <button className="action-button">RESET</button>
          <button className="action-button">POWER</button>
        </div>
        <div className="advanced-settings-button-container">
          <Link to="/advancedsettings">
            <button className="advanced-settings-button">ADVANCED SETTINGS</button>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Settings;
