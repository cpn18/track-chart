// src/App.js
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { ThemeProvider, useTheme } from './ThemeContext';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import IMU from './pages/IMU';
import LIDAR from './pages/LIDAR';
import LPCM from './pages/LPCM';
import Settings from './pages/Settings';
import Simulator from './pages/Simulator';
import './App.css'; // global styles

/**
 * AppContent comp.
 * structure and navigation of PiRail React
 * use useTheme to apply dark/light mode based on toggle in Settings
 */

const AppContent = () => {
  const { isDarkMode } = useTheme(); // get theme state

  return (
    <div className={isDarkMode ? 'dark-mode' : 'light-mode'}> {/* theme based styling */}
      <Navbar /> {/* include nav bar */}
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/imu" element={<IMU />} />
        <Route path="/lidar" element={<LIDAR />} />
        <Route path="/lpcm" element={<LPCM />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/simulator" element={<Simulator />} />
      </Routes>
    </div>
  );
};

/**
 * App comp.
 * wraps app in ThemeProvider (manage dark mode)
 * Router -> enable client side routing w/ React Router
 */

const App = () => {

  return (
    <ThemeProvider> {/* theme context to entire app */}
      <Router> {/* routing functionality */}
        <AppContent />
      </Router>
    </ThemeProvider>
  );
};

export default App;
