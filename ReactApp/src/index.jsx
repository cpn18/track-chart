// index.jsx
import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import './index.css'
import { StatusProvider } from './StatusContext'
import { PoiProvider } from './PoiContext'

// Find the DOM element where we will mount our React app
const container = document.getElementById('root')
const root = createRoot(container)

// Render the app inside React.StrictMode (best practice)
root.render(
  <React.StrictMode>
    <StatusProvider>
      <PoiProvider>
        <App />
      </PoiProvider>
    </StatusProvider>
  </React.StrictMode>
)
