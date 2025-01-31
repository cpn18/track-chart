// src/pages/AdvancedSettings.js
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useStatus } from '../StatusContext';
import './AdvancedSettings.css';

const AdvancedSettings = () => {
  const navigate = useNavigate(); // init use nav
  const {
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
  } = useStatus();

  return (
    <div className="advanced-settings">
      <h2>Advanced Settings:</h2>

      <div className="setting-section">
        <label className="setting-label">GPS:</label>
        <div className="setting-toggle">
          <input type="checkbox" checked={gps} onChange={() => setGps(!gps)} />
          <span>Enable GPS</span>
        </div>
      </div>

      <div className="setting-section">
        <label className="setting-label">IMU:</label>
        <div className="setting-toggle">
          <input type="checkbox" checked={imu} onChange={() => setImu(!imu)} />
          <span>Enable IMU</span>
        </div>
        <div className="sub-options">
          <label>Forward</label>
          <select multiple>
            <option value="x">x</option>
            <option value="y">y</option>
            <option value="z">z</option>
          </select>
          <label>Side</label>
          <select multiple>
            <option value="x">x</option>
            <option value="y">y</option>
            <option value="z">z</option>
          </select>
          <label>Vertical</label>
          <select multiple>
            <option value="x">x</option>
            <option value="y">y</option>
            <option value="z">z</option>
          </select>
        </div>
      </div>

      <div className="setting-section">
        <label className="setting-label">GPSIMU:</label>
        <div className="setting-toggle">
          <input type="checkbox" checked={gpsimu} onChange={() => setGpsimu(!gpsimu)} />
          <span>Enable GPSIMU</span>
        </div>
        <div className="sub-options">
          <label>Forward</label>
          <select multiple>
            <option value="x">x</option>
            <option value="y">y</option>
            <option value="z">z</option>
          </select>
          <label>Side</label>
          <select multiple>
            <option value="x">x</option>
            <option value="y">y</option>
            <option value="z">z</option>
          </select>
          <label>Vertical</label>
          <select multiple>
            <option value="x">x</option>
            <option value="y">y</option>
            <option value="z">z</option>
          </select>
        </div>
      </div>

      <div className="setting-section">
        <label className="setting-label">360 LIDAR:</label>
        <div className="setting-toggle">
          <input type="checkbox" checked={lidar360} onChange={() => setLidar360(!lidar360)} />
          <span>Enable 360 LIDAR</span>
        </div>
      </div>

      <div className="setting-section">
        <label className="setting-label">HPS 3D LIDAR:</label>
        <div className="setting-toggle">
          <input type="checkbox" checked={hps3d} onChange={() => setHps3d(!hps3d)} />
          <span>Enable HPS 3D LIDAR</span>
        </div>
      </div>

      <div className="setting-section">
        <label className="setting-label">LPCM:</label>
        <div className="setting-toggle">
          <input type="checkbox" checked={lpcm} onChange={() => setLpcm(!lpcm)} />
          <span>Enable LPCM</span>
        </div>
      </div>

      <div className="button-group">
        <button className="save-button">SAVE</button>
        <button className="back-button" onClick={() => navigate('/settings')}>BACK</button>
      </div>
    </div>
  );
};

export default AdvancedSettings;
