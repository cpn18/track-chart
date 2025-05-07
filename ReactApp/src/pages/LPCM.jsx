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
  const [enabled, setEnabled] = useState(true);
  const { isDarkMode } = useTheme(); 
  
  
  useEffect(() => {
    fetch('/config')
      .then((res) => res.json())
      .then((data) => {
        setConfig(data);
        setEnabled(Boolean(data.lpcm?.enable));
        console.log('Config fetched');
      })
      .catch((err) => {
        console.error('Error fetching config:', err);
    });
  }, []);

  return (
    <div className="imu-container">
      <div className="nav-container"></div>
      {/* LPCM place holder image */}
      {enabled ? <img
        src={`/${isDarkMode ? 'lpcm_white.gif' : `lpcm_black.gif`}`}
        alt="LPCM Representation"
        className="lidar-image"
      /> : <div>LPCM disabled - turn on in settings</div>}
      
      {/* footer */}
      <Footer />
    </div>
  );
};

export default LPCM;
