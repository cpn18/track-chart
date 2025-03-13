import React, { useEffect, useState } from 'react';
import '../App.css';
import Footer from '../components/Footer';

/**
 * LPCM Page:
 * Display the cur time and an image representing LPCM. 
 * Time update every second.
 * End goal is to have audio output when clicking the audio icon.
 */
const LPCM = () => {
  // track cur time, set to the cur date and time
  const [currentTime, setCurrentTime] = useState(new Date());

  /**
   * useEffect
   * Interval to update `currentTime` every sec.
   * To prevent mem leak, clean up interval when comp. is unmounted.
   */
  
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="imu-container">
      {/* LPCM place holder image */}
      <img
        src={`/audio.png`}
        alt="LPCM Representation"
        className="lidar-image"
      />
      
      {/* show cur date and time */}
      <p className="imu-timestamp">
        LPCM as of: {currentTime.toLocaleDateString()} {currentTime.toLocaleTimeString()}
      </p>
      
      {/* footer */}
      <Footer />
    </div>
  );
};

export default LPCM;
