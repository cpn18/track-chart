// src/index.js
import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import './index.css';
import { StatusProvider } from './StatusContext'; // this is for on/off of gpu, lidar, etc.
import { PoiProvider } from './PoiContext'; // this makes poi's stay on map after changing tabs

ReactDOM.render(
  <React.StrictMode>
    <StatusProvider>
      <PoiProvider>
        <App />
      </PoiProvider>
    </StatusProvider>
  </React.StrictMode>,
  document.getElementById('root')
);
