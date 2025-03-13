import React, { useState } from 'react';
import { useTheme } from '../ThemeContext';
import { useStatus } from '../StatusContext';
import { useNavigate } from 'react-router-dom';
import './settings.css';
import Footer from '../components/Footer';

/**
 * Page exists to manage the controls for:
 * Toggling various sensors on/off
 * Accessibility options like dark mode / imperial
 * Resetting the rasp-pi and turning off
 * Accessing the simulator
 */

const Settings = () => {
  const { isDarkMode, toggleDarkMode } = useTheme(); // get global state for dark mode
  const navigate = useNavigate(); // allows for navigation (to simulator)
  const { gps, setGps, imu, setImu, lidar360, setLidar360, hps3d, setHps3d, lpcm, setLpcm } = useStatus(); // get global sensor states
  const [showPower, setPower] = useState(false); // state - power pop-up
  const [showReset, setReset] = useState(false); // state - reset pop-up

  // track dropdown visibility
  const [dropdowns, setDropdowns] = useState({
    gps: false,
    imu: false,
    lidar: false,
    lpcm: false,
  });

  /**
   * func. to toggle dropdown menu for sensors
   * takes in the sensor name (gps, imu, lidar, lpcm).
   */
  const toggleDropdown = (sensor) => {
    setDropdowns((prev) => ({
      ...prev,
      [sensor]: !prev[sensor],
    }));
  };

  const togglePower = () => {
    setPower(!showPower);
  };

  const toggleReset = () => {
    setReset(!showReset);
  };

  return (
    <div className="settings-container">
      {/* STATUS */}
      <div className="status-section">
        <h3>STATUS:</h3>
        <div className="status-grid">
          {/* GPS */}
          <div
            className="status-item"
            onMouseEnter={(e) => e.currentTarget.classList.add('hover')}
            onMouseLeave={(e) => e.currentTarget.classList.remove('hover')}
            onClick={() => toggleDropdown('gps')} // Click toggles the dropdown
          >
            <span className="dropdownText">GPS: </span>
            <span className={gps ? 'status-on' : 'status-off'}>
              {gps ? 'ON' : 'OFF'}{' '}
              <span className="dropdown-arrow">
                {dropdowns.gps ? '\u25B2' : '\u25BC'}
              </span>
            </span>
            {dropdowns.gps && (
              <div
                className="dropdown-menu"
                onClick={(e) => e.stopPropagation()} // Prevent dropdown toggle
              >
                <label>
                  Enable GPS
                  <label className="switch">
                    <input
                      type="checkbox"
                      checked={gps}
                      onChange={() => setGps(!gps)}
                    />
                    <span className="slider"></span>
                  </label>
                </label>
              </div>
            )}
          </div>

          {/* IMU */}
          <div
            className="status-item"
            onMouseEnter={(e) => e.currentTarget.classList.add('hover')}
            onMouseLeave={(e) => e.currentTarget.classList.remove('hover')}
            onClick={() => toggleDropdown('imu')} // Click toggles the dropdown
          >
            <span className="dropdownText">IMU: </span>
            <span className={imu ? 'status-on' : 'status-off'}>
              {imu ? 'ON' : 'OFF'}{' '}
              <span className="dropdown-arrow">
                {dropdowns.imu ? '\u25B2' : '\u25BC'}
              </span>
            </span>
            {dropdowns.imu && (
              <div
                className="dropdown-menu"
                onClick={(e) => e.stopPropagation()} // Prevent dropdown toggle
              >
                <label>
                  Enable IMU
                  <label className="switch">
                    <input
                      type="checkbox"
                      checked={imu}
                      onChange={() => setImu(!imu)}
                    />
                    <span className="slider"></span>
                  </label>
                </label>
                <div>
                  <label>Forward</label>
                  <select>
                    <option value="x">x</option>
                    <option value="y">y</option>
                    <option value="z">z</option>
                  </select>
                </div>
                <div>
                  <label>Side</label>
                  <select>
                    <option value="x">x</option>
                    <option value="y">y</option>
                    <option value="z">z</option>
                  </select>
                </div>
                <div>
                  <label>Vertical</label>
                  <select>
                    <option value="x">x</option>
                    <option value="y">y</option>
                    <option value="z">z</option>
                  </select>
                </div>
              </div>
            )}
          </div>

          {/* LIDAR */}
          <div
            className="status-item"
            onMouseEnter={(e) => e.currentTarget.classList.add('hover')}
            onMouseLeave={(e) => e.currentTarget.classList.remove('hover')}
            onClick={() => toggleDropdown('lidar')} // Click toggles the dropdown
          >
            <span className="dropdownText">LIDAR: </span>
            <span className={(lidar360 || hps3d) ? 'status-on' : 'status-off'}>
              {(lidar360 || hps3d) ? 'ON' : 'OFF'}{' '}
              <span className="dropdown-arrow">
                {dropdowns.lidar ? '\u25B2' : '\u25BC'}
              </span>
            </span>
            {dropdowns.lidar && (
              <div
                className="dropdown-menu"
                onClick={(e) => e.stopPropagation()} // Prevent dropdown toggle
              >
                <label>
                  Enable 360 LIDAR
                  <label className="switch">
                    <input
                      type="checkbox"
                      checked={lidar360}
                      onChange={() => setLidar360(!lidar360)}
                    />
                    <span className="slider"></span>
                  </label>
                </label>
                <label>
                  Enable HPS 3D LIDAR
                  <label className="switch">
                    <input
                      type="checkbox"
                      checked={hps3d}
                      onChange={() => setHps3d(!hps3d)}
                    />
                    <span className="slider"></span>
                  </label>
                </label>
              </div>
            )}
          </div>

          {/* LPCM */}
          <div
            className="status-item"
            onMouseEnter={(e) => e.currentTarget.classList.add('hover')}
            onMouseLeave={(e) => e.currentTarget.classList.remove('hover')}
            onClick={() => toggleDropdown('lpcm')} // click -> toggles dropdown
          >
            <span className="dropdownText">LPCM: </span>
            <span className={lpcm ? 'status-on' : 'status-off'}>
              {lpcm ? 'ON' : 'OFF'}{' '}
              <span className="dropdown-arrow">
                {dropdowns.lpcm ? '\u25B2' : '\u25BC'}
              </span>
            </span>
            {dropdowns.lpcm && (
              <div
                className="dropdown-menu"
                onClick={(e) => e.stopPropagation()} // prevent dropdown toggle
              >
                <label>
                  Enable LPCM
                  <label className="switch">
                    <input
                      type="checkbox"
                      checked={lpcm}
                      onChange={() => setLpcm(!lpcm)}
                    />
                    <span className="slider"></span>
                  </label>
                </label>
              </div>
            )}
          </div>

          {/* GPU Temp */}
          <div className="status-item gpu-temp">
            <span className="dropdownText">CPU Temp: </span>
            {/* INPUT REAL GPU TEMP HERE*/}
            <span className="gpu-temp-value">49°C</span>
          </div>
        </div>
      </div>

      {/* accessibility section */}
      <div className="accessibility-section">
        <h3>ACCESSIBILITY:</h3>
        <div className="setting-item">
          <label>
            Dark Mode
            <label className="switch">
              <input
                type="checkbox"
                checked={isDarkMode}
                onChange={toggleDarkMode}
              />
              <span className="slider"></span>
            </label>
          </label>
        </div>
        <div className="setting-item">
          <label>
            Imperial Measurements
            <label className="switch">
              <input type="checkbox" />
              <span className="slider"></span>
            </label>
          </label>
        </div>
      </div>

      {/* action section */}
      <div className="setting-item">
        <h3>ACTIONS:</h3>
        <div className="button-group">
          <button className="action-button" onClick={setReset}>RESET</button>
          <button className="action-button" onClick={setPower}>POWER</button>
        </div>
        <div className="simulator-button-container">
          <button
            className="simulator-button"
            onClick={() => navigate('/simulator')}
          >
            SIMULATOR
          </button>
        </div>
      </div>

      {showPower && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h1>Power Unit:</h1>
              <p>
                Are you sure you'd like to reset the PiRail unit?
              </p>
              <div className="modal-buttons">
                <button className="modal-button">
                  POWER OFF
                </button>
                <button className="modal-button cancel" onClick={togglePower}>
                  CANCEL
                </button>
              </div>
          </div>
        </div>
      )}

      {showReset && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h1>Reset Settings:</h1>
              <p>
                Are you sure you'd like to reset the PiRail unit?
              </p>
              <div className="modal-buttons">
                <button className="modal-button">
                  RESET
                </button>
                <button className="modal-button cancel" onClick={toggleReset}>
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

export default Settings;
