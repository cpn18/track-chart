import React, { useEffect, useState } from 'react';
import '../App.css';
import Footer from '../components/Footer';

/**
 * LIDAR Page:
 * Show the current time + date
 * an image representing a LIDAR stream.
 * End goal is to have a constantly updating LIDAR feed.
 */

const LIDAR = () => {
  const [currentTime, setCurrentTime] = useState(new Date()); // store cur system time 

  /**
   * useEffect
   * Interval to update `currentTime` every sec.
   * To prevent mem leak, clean up interval when comp. is unmounted.
   */

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(interval); // clean on unmount
  }, []);

  return (
    <div className="imu-container">
       {/* LIDAR placeholder below */}
       <video 
        src={`/LIDARexample_video.mp4`} 
        className="lidar-video" 
        autoPlay 
        loop 
        muted 
      />
      {/* display cur date and time */}
      <p className="imu-timestamp">
        LIDAR as of: {currentTime.toLocaleDateString()} {currentTime.toLocaleTimeString()}
      </p>
      <Footer />
    </div>
  );
};

export default LIDAR;

