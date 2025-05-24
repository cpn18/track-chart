import React, { useEffect, useState } from 'react';
import '../App.css';
import { useTheme } from '../ThemeContext';
import Footer from '../components/Footer';

/**
 * LPCM Page:
 * Display the cur time and an image representing LPCM. 
 * Time update every second.
 * End goal is to have audio output when clicking the audio icon.
 */
const LPCM = () => {
  // track cur time, set to the cur date and time
  const [config, setConfig] = useState(null);
  const [enabled, setEnabled] = useState(false);
  const [time, setTime] = useState(null);
  const { isDarkMode } = useTheme(); 
  
  
  useEffect(() => {
    fetch('/config')
      .then((res) => res.json())
      .then((data) => {
        setConfig(data);
        setEnabled(Boolean(data.lpcm?.enable) || Boolean(data.sim?.enable));
        console.log('Config fetched');
      })
      .catch((err) => {
        console.error('Error fetching config:', err);
    });

	      const settingsStream = new EventSource('/packets?count=1000');
    settingsStream.addEventListener('pirail_LPCM', handleDataUpdate);

    settingsStream.onopen = () => {
      console.log('packet connection opened');
    };

    settingsStream.onerror = () => {
      console.log('packet connection error');
    };

  }, []);

    const handleDataUpdate = (event) => {
    console.log(event);
    var lpcm = JSON.parse(event.data);
    console.log(lpcm);
    if (lpcm.time != undefined) {
      setTime(lpcm.time.split('.')[0]);
    }
  }

  return (
    <div className="imu-container">
      <div className="nav-container"></div>
      {/* LPCM place holder image */}
      {enabled ? ( <img
        src={`/${isDarkMode ? 'lpcm_white.gif' : `lpcm_black.gif`}`}
        alt="LPCM Representation"
        className="lidar-image"
      /> ) : (
	 <div>LPCM disabled - turn on in settings</div>
      )}
      <label>{time}</label>
      
      {/* footer */}
      <Footer />
    </div>
  );
};

export default LPCM;
