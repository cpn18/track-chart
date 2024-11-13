// src/pages/Home.js
import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import './Home.css';

const userIcon = new L.Icon({
  iconUrl: `${process.env.PUBLIC_URL}/train.png`, // icon
  iconSize: [25, 25],
  iconAnchor: [12, 25],
  popupAnchor: [0, -25],
});

const Home = () => {
  const [location, setLocation] = useState(null);

  useEffect(() => {
    // get the user's cur location
    const fetchLocation = () => {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          });
        },
        (error) => {
          console.error("ERROR getting location:", error);
        }
      );
    };

    // get location - set interval to update every (5) sec
    fetchLocation();
    const interval = setInterval(fetchLocation, 5000);

    return () => clearInterval(interval); // clean up interval
  }, []);

  return (
    <div className="home-container">
      <MapContainer center={location || { lat: 0, lng: 0 }} zoom={13} className="map-container">
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        {location && (
          <Marker position={location} icon={userIcon}>
            <Popup>You are here</Popup>
          </Marker>
        )}
      </MapContainer>

      <div className="info-container">
        <h2>INFORMATION:</h2>
        <div className="info-grid">
          <div className="info-item">Speed:</div>
          <div className="info-item">LAT: {location ? location.lat.toFixed(5) : "Loading..."}</div>
          <div className="info-item">Distance:</div>
          <div className="info-item">LONG: {location ? location.lng.toFixed(5) : "Loading..."}</div>
          <div className="info-item">Altitude:</div>
          <div className="info-item">Time:</div>
        </div>
        <div className="button-group">
          <button className="add-poi-button">ADD POI</button>
          <button className="view-satellites-button">VIEW SATELLITES</button>
        </div>
      </div>
    </div>
  );
};

export default Home;
