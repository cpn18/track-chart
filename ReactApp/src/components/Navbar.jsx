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
    <nav className={`navbar ${isDarkMode ? 'dark' : 'light'}`}> {/* theme based styling */}
      <div className="logo-container">
        {/* click logo -> homepage */}
        <NavLink to="/">
          <img src={isDarkMode ? logoDark : logoLight} alt="PiRail Logo" className="logo" />
        </NavLink>
      </div>
      <div className="nav-links">
        {/* all other nav links (imu, lidar, etc.) */}
        <NavLink
          to="/imu"
          className={({ isActive }) => (isActive ? 'nav-link active-link' : 'nav-link')}
        >
          IMU
        </NavLink>
        <NavLink
          to="/lidar"
          className={({ isActive }) => (isActive ? 'nav-link active-link' : 'nav-link')}
        >
          LIDAR
        </NavLink>
        <NavLink
          to="/lpcm"
          className={({ isActive }) => (isActive ? 'nav-link active-link' : 'nav-link')}
        >
          LPCM
        </NavLink>
        <NavLink
          to="/settings"
          className={({ isActive }) =>
            isActive || location.pathname === '/advancedsettings' // highlight if on settings / advanced settings
              ? 'nav-link active-link'
              : 'nav-link'
          }
        >
          Settings
        </NavLink>
      </div>
    </nav>
  );
};

export default Navbar;
