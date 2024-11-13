// src/index.js
import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import { StatusProvider } from './StatusContext';

ReactDOM.render(
  <StatusProvider>
    <App />
  </StatusProvider>,
  document.getElementById('root')
);
