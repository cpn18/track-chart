import React, { useState, useEffect } from 'react';
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
  const [gps, setGps] = useState(false);
  const [imu, setImu] = useState(false);
  const [lidar, setLidar] = useState(false);
  const [hpslidar, setHpsLidar] = useState(false);
  const [lpcm, setLpcm] = useState(false);  const [showPower, setPower] = useState(false); // state - power pop-up
  const [showReset, setReset] = useState(false); // state - reset pop-up
  const [showApply, setApply] = useState(false);
  const [config, setConfig] = useState(null); // config served by web server
  const [temp, setTemp] = useState(null);
  const [output, setOutput] = useState(null);
  const [used, setUsed] = useState(null);
  const [swver, setSwVer] = useState(null);
  const [osver, setOsVer] = useState(null);
  const [hwname, setHwName] = useState(null);
  const [pendingApply, setPendingApply] = useState(false);


  // track dropdown visibility
  const [dropdowns, setDropdowns] = useState({
    gps: false,
    imu: false,
    lidar: false,
    lpcm: false,
  });

  const toggleApply = () => {
    setApply(!showApply);
  }

  const togglePower = () => {
    setPower(!showPower);
  };

  const toggleReset = () => {
    setReset(!showReset);
  };
/*
  useEffect(() => {
    fetch('/config')
      .then((res) => {
        if (!res.ok) {
          throw new Error(`Failed to fetch. Status code: ${res.status}`);
        }
        return res.json();
      })
      .then((data) => {
        console.log('Fetched config:', data);
        setConfig(data);
        initSensors(data);
        console.log('Config fetched');
      })
      .catch((err) => {
        console.error('Error fetching config:', err);
      });

    const settingsStream = new EventSource('/packets?count=1000');
    settingsStream.addEventListener('pirail_ATT', handleDataUpdate);

    settingsStream.onopen = () => {
      console.log('connection opened');
    };

    settingsStream.onerror = () => {
      console.log('connection error');
    };
  }, []);
  */
  
/*
  const handleDataUpdate = (event) => {
    console.log(event);
    var att = JSON.parse(event.data);
    // CPU Temp
    if (att.temp != undefined) {
      setTemp(att.temp);
    }
  }

  const initSensors = (data) => {
    setGps(data?.gps?.enable || false);
    setImu(data?.imu?.enable || false);
    setLidar(data?.lidar?.enable || false);
    setHpsLidar(data?.hpslidar?.enable || false);
    setLpcm(data?.lpcm?.enable || false);
  
    console.log('Lidar enabled?', data?.lidar?.enable);
    console.log('HPSLidar enabled?', data?.hpslidar?.enable);
  };

  const toggleDropdown = (sensor) => {
    console.log(config);
    setDropdowns((prev) => ({
      ...prev,
      [sensor]: !prev[sensor],
    }));
  };

  const toggleSensor = (sensor) => {
    // toggle sensor in local config
    const updatedConfig = {
      ...config,
      [sensor]: {
        ...config[sensor],
        enable: !config[sensor].enable,
      },
    };
    setConfig(updatedConfig);
  
    // Send all keys ['gps','imu','lidar','hpslidar','lpcm','simulator']
    // each time any toggle is switched
    fetch('/setup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        gps: config.gps,
        imu: config.imu,
        lidar: config.lidar,
        hpslidar: config.hpslidar,
        lpcm: config.lpcm,
      }),
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error(`Request failed with status ${res.status}`);
        }
        return res.json();
      })
      .then((data) => {
        console.log(data.message);
      })
      .catch((err) => {
        console.error('Error updating config:', err);
      });
  }
 */

  const toggleDropdown = (sensor) => {
    console.log(config);
    setDropdowns((prev) => ({
      ...prev,
      [sensor]: !prev[sensor],
    }));
  };

  // -1 → force OFF
  //  0 → force ON
  //  1 → invert current value (default)
  //  2 → leave as‑is but refresh visual flags
  const toggleSensor = (data, sensor, toggle = 1) => {
    // current state
    const currEnable = data[sensor].enable;

    // compute desired state
    const newEnable =
      toggle === -1 ? false :
      toggle ===  0 ? true  :
      toggle ===  2 ? currEnable :
      !currEnable;               

    // push to shared config (even if unchanged – harmless)
    const updatedConfig = {
      ...data,
      [sensor]: {
        ...data[sensor],
        enable: newEnable,
      },
    };
    setConfig(updatedConfig);

    switch (sensor) {
      case 'gps':      setGps(newEnable);      break;
      case 'imu':      setImu(newEnable);      break;
      case 'lidar':    setLidar(newEnable);    break;
      case 'hpslidar': setHpsLidar(newEnable); break;
      case 'lpcm':     setLpcm(newEnable);     break;
      default:         return;
    }
  };

  const toggleLogging = (data, sensor, toggle = 1) => {
    // current state
    const currLogging = data[sensor].logging;

    // compute desired state
    const newLogging =
      toggle === -1 ? false :
      toggle ===  0 ? true  :
      toggle ===  2 ? currLogging :
      !currLogging;               

    // push to shared config (even if unchanged – harmless)
    const updatedConfig = {
      ...data,
      [sensor]: {
        ...data[sensor],
        logging: newLogging,
      },
    };
    setConfig(updatedConfig);
	  console.log("logging is " + newLogging)
  };

  // toggle: value to set sensor to (see above)
  const initSensors = (data, toggle = 1) => {
    Object.keys(data).forEach((sensor) => {
      toggleSensor(data, sensor, toggle);               
    });
  };

  const resetDevice = () => {
    fetch('/reset')
      .then((res) => {
        if (!res.ok) {
          throw new Error(`Failed to reset: ${res.status}`);
        }
        return res.json();
      })
      .then((data) => {
        console.log(data);
        toggleReset()
      })
  }

  const powerOff = () => {
    fetch('/poweroff')
      .then((res) => {
        if (!res.ok) {
          throw new Error(`Failed to power off: ${res.status}`);
        }
        return res.json();
      })
      .then((data) => {
        console.log(data);
        togglePower()
      })
  }

  useEffect(() => {
    fetch('/config')
      .then((res) => {
        if (!res.ok) {
          throw new Error(`Failed to fetch. Status code: ${res.status}`);
        }
        return res.json();
      })
      .then((data) => {
        console.log('Fetched config:', data);
        setConfig(data);
        initSensors(data, 2);
        console.log('Config fetched');
      })
      .catch((err) => {
        console.error('Error fetching config:', err);
      });

    const settingsStream = new EventSource('/packets?count=1000');
    settingsStream.addEventListener('pirail_ATT', handleDataUpdate);
    settingsStream.addEventListener('pirail_SYS', handleSysDataUpdate);

    settingsStream.onopen = () => {
      console.log('ATT connection opened');
    };

    settingsStream.onerror = () => {
      console.log('ATT connection error');
    };
  }, []);

  useEffect(() => {
    if (pendingApply) {          
      applySettings();           
      setPendingApply(false);
    }
  }, [config, pendingApply]);

  const applySettings = () => {
	  console.log(config)
    fetch('/config', {
      "method": "PUT",
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        gps: config.gps,
        imu: config.imu,
        lidar: config.lidar,
        hpslidar: config.hpslidar,
        lpcm: config.lpcm,
	sim: config.sim,
      }),
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error(`Failed to fetch. Status code: ${res.status}`);
        }
	      toggleApply();
      })
  };
  
  const handleDataUpdate = (event) => {
    //console.log(event);
    var att = JSON.parse(event.data);
    console.log(att);
    // CPU Temp
    if (att.temp != undefined) {
      setTemp(att.temp.toFixed(0));
    }
  }

  const handleSysDataUpdate = (event) => {
    //console.log(event);
    var sys = JSON.parse(event.data);
    console.log(sys);
    // Output
    if (sys.output != undefined) {
      setOutput(sys.output);
      setUsed(sys.used_percent.toFixed(0));
    }
    if (sys.sw_version != undefined) {
      setSwVer(sys.sw_version);
    }
    if (sys.hwname != undefined) {
      setHwName(sys.hwname);
    }
    if (sys.os_version != undefined) {
      setOsVer(sys.os_version);
    }
  }

  

  return (
    <div className="settings-container">
      <div className="nav-container"></div>
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
                      checked={config?.gps?.enable || false}
                      onChange={() => toggleSensor(config, 'gps')}
                    />
                    <span className="slider"></span>
                  </label>
                </label>
                <label>
		    Logging
		    <label className="switch">
                <input
                      type="checkbox"
                      checked={config?.gps?.logging || false}
                      onChange={() => toggleLogging(config, 'gps')}
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
		    Enable
		    <label className="switch">
                <input
                      type="checkbox"
                      checked={config?.imu?.enable || false}
                      onChange={() => toggleSensor(config, 'imu')}
                 />
                    <span className="slider"></span>
		    </label>
		    </label>
                <label>
		    Logging
		    <label className="switch">
                <input
                      type="checkbox"
                      checked={config?.imu?.logging || false}
                      onChange={() => toggleLogging(config, 'imu')}
                 />
                    <span className="slider"></span>
		    </label>
		    </label>
                <div>
                  <label>Forward</label>
                  <select value={config?.imu?.x}>
                    <option value="x">x</option>
                    <option value="y">y</option>
                    <option value="z">z</option>
                  </select>
                </div>
                <div>
                  <label>Side</label>
                  <select value={config?.imu?.y}>
                    <option value="x">x</option>
                    <option value="y">y</option>
                    <option value="z">z</option>
                  </select>
                </div>
                <div>
                  <label>Vertical</label>
                  <select value={config?.imu?.z}>
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
            <span className={(lidar || hpslidar) ? 'status-on' : 'status-off'}>
              {(lidar || hpslidar) ? 'ON' : 'OFF'}{' '}
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
                      checked={config?.lidar?.enable || false}
                      onChange={() => toggleSensor(config, 'lidar')}
                    />
                    <span className="slider"></span>
                  </label>
                </label>
                <label>
                  Enable HPS 3D LIDAR
                  <label className="switch">
                    <input
                      type="checkbox"
                      checked={hpslidar}
                      onChange={() => toggleSensor(config, 'hpslidar')}
                    />
                    <span className="slider"></span>
                  </label>
                </label>
                <label>
		    Logging
		    <label className="switch">
                <input
                      type="checkbox"
                      checked={config?.lidar?.logging || false}
                      onChange={() => toggleLogging(config, 'lidar')}
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
                      onChange={() => toggleSensor(config, 'lpcm')}
                    />
                    <span className="slider"></span>
                  </label>
                </label>
                <label>
		    Logging
		    <label className="switch">
                <input
                      type="checkbox"
                      checked={config?.lpcm?.logging || false}
                      onChange={() => toggleLogging(config, 'lpcm')}
                 />
                    <span className="slider"></span>
		    </label>
		    </label>
              </div>
            )}
          </div>

          {/* CPU Temp */}
          <div className="status-item gpu-temp">
            <span className="dropdownText">CPU Temp: {temp ? `${temp}°` : 'Loading...'}</span>
            <span className="gpu-temp-value"></span>
          </div>
          {/* Output */}
          <div className="status-item">
            <span className="dropdownText">Output: {output ? `${output} ${used}%` : 'Loading...'}</span>
          </div>
          {/* Software */}
          <div className="status-item">
            <span className="dropdownText">Software: {swver ? `${swver}` : 'Loading...'}</span>
          </div>
          {/* Hardware */}
          <div className="status-item">
            <span className="dropdownText">Hardware: {hwname ? `${hwname}` : 'Loading...'}</span>
          </div>
          {/* OS Version */}
          <div className="status-item">
            <span className="dropdownText">OS Version: {osver ? `${osver}` : 'Loading...'}</span>
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
          <button className="action-button apply-button" onClick={setApply}>APPLY</button>
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

      
      {showApply && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h1>Apply Settings:</h1>
              <p>
                Are you sure you'd like to save settings and reboot?
              </p>
              <div className="modal-buttons">
                <button className="modal-button" onClick={applySettings}>
                  APPLY
                </button>
                <button className="modal-button cancel" onClick={toggleApply}>
                  CANCEL
                </button>
              </div>
          </div>
        </div>
      )}

      {showPower && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h1>Power Unit:</h1>
              <p>
                Are you sure you'd like to power off the PiRail unit?
              </p>
              <div className="modal-buttons">
                <button className="modal-button" onClick={powerOff}>
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
                <button className="modal-button" onClick={resetDevice}>
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
