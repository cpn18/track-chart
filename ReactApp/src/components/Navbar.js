// src/components/Navbar.js
import React from 'react';
import { NavLink } from 'react-router-dom';
import { useTheme } from '../ThemeContext';
import logoLight from './pirailBlack.png'; // dark logo
import logoDark from './pirailWhite.png';  // white logo
import './Navbar.css';

const Navbar = () => {
  const { isDarkMode } = useTheme();

  return (
    <nav className={`navbar ${isDarkMode ? 'dark' : 'light'}`}>
      <div className="logo-container">
        <NavLink to="/">
          <img src={isDarkMode ? logoDark : logoLight} alt="PiRail Logo" className="logo" />
        </NavLink>
      </div>
      <div className="nav-links">
        <NavLink to="/imu" className={({ isActive }) => (isActive ? "nav-link active-link" : "nav-link")}>IMU</NavLink>
        <NavLink to="/lidar" className={({ isActive }) => (isActive ? "nav-link active-link" : "nav-link")}>LIDAR</NavLink>
        <NavLink to="/lpcm" className={({ isActive }) => (isActive ? "nav-link active-link" : "nav-link")}>LPCM</NavLink>
        <NavLink to="/settings" className={({ isActive }) => (isActive ? "nav-link active-link" : "nav-link")}>Settings</NavLink>
        <NavLink to="/advancedsettings" className={({ isActive }) => (isActive ? "nav-link active-link" : "nav-link")}>Advanced Settings</NavLink>
        <NavLink to="/simulator" className={({ isActive }) => (isActive ? "nav-link active-link" : "nav-link")}>Simulator</NavLink>
      </div>
    </nav>
  );
};

export default Navbar;
