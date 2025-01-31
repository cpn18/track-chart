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
import AdvancedSettings from './pages/AdvancedSettings';
import './App.css';

const AppContent = () => {
  const { isDarkMode } = useTheme();

  return (
    <div className={isDarkMode ? 'dark-mode' : 'light-mode'}>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/imu" element={<IMU />} />
        <Route path="/lidar" element={<LIDAR />} />
        <Route path="/lpcm" element={<LPCM />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/simulator" element={<Simulator />} />
        <Route path="/advancedsettings" element={<AdvancedSettings />} /> 
      </Routes>
    </div>
  );
};

const App = () => {
  return (
    <ThemeProvider>
      <Router>
        <AppContent />
      </Router>
    </ThemeProvider>
  );
};

export default App;
