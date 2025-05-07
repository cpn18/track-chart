import React from 'react';
import { NavLink, useLocation } from 'react-router-dom'; // useLocation (track cur route)
import { useTheme } from '../ThemeContext';
import logoLight from './pirailBlack.png'; // dark logo
import logoDark from './pirailWhite.png'; // white logo
import './Navbar.css';

/**
 * Navbar
 * navigation links for different pages of PiRail app
 * switches between light/dark mode
 * highlight active navigation link
 */
const Navbar = () => {
  const { isDarkMode } = useTheme(); // access dark mode
  const location = useLocation(); // get the cur URL path

  return (
    <div className="desktop-nav">
      {/* PiRail Logo */}
      <div className="nav-logo-bubble">
        <NavLink to="/">
          <img src={isDarkMode ? logoDark : logoLight} alt="PiRail Logo" className="logo" />
        </NavLink>
      </div>

      {/* nav links */}
      <div className="nav-buttons">
        <NavLink to="/imu" className={({ isActive }) => (isActive ? 'nav-button active' : 'nav-button')}>
          <img
            src={`/${isDarkMode ? 'imuDARK.png' : 'imu.png'}`}
            alt="IMU"
            className="nav-icon"
          />
          <span>IMU</span>
        </NavLink>
        <NavLink to="/lidar" className={({ isActive }) => (isActive ? 'nav-button active' : 'nav-button')}>
          <img
            src={`/${isDarkMode ? 'cameraiconDARK.png' : 'cameraicon.png'}`}
            alt="LIDAR"
            className="nav-icon"
          />
          <span>LIDAR</span>
        </NavLink>
        <NavLink to="/lpcm" className={({ isActive }) => (isActive ? 'nav-button active' : 'nav-button')}>
          <img
            src={`/${isDarkMode ? 'waveformDARK.png' : 'waveform.png'}`}
            alt="LPCM"
            className="nav-icon"
          />
          <span>LPCM</span>
        </NavLink>
        <NavLink to="/settings" className={({ isActive }) => (isActive ? 'nav-button active' : 'nav-button')}>
          <img
            src={`/${isDarkMode ? 'gearIconSettingsDARK.png' : 'gearIconSettings.png'}`}
            alt="Settings"
            className="nav-icon"
          />
          <span>Settings</span>
        </NavLink>
      </div>
    </div>
  );
};

export default Navbar;
