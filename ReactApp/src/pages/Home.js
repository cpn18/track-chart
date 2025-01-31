// src/pages/Home.js
import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import { usePoi } from '../PoiContext';
import './Home.css';

const poiIcon = new L.Icon({
  iconUrl: `${process.env.PUBLIC_URL}/mapMarker.png`, // marker icon
  iconSize: [30, 30],
  iconAnchor: [15, 30],
  popupAnchor: [0, -30],
});

const userIcon = new L.Icon({
  iconUrl: `${process.env.PUBLIC_URL}/train.png`, // icon
  iconSize: [25, 25],
  iconAnchor: [12, 25],
  popupAnchor: [0, -25],
});

const Home = () => {
  const [userLocation, setLocation] = useState(null);
  const [pois, setPois] = usePoi();
  const [zoom, setZoom] = useState(12);

  useEffect(() => {
    // get the user's cur location
    const fetchLocation = () => {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          });
          setZoom(13);
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

    // helper to create the marker upon clicking add POI
  const handleAddPoi = () => {
    if (!userLocation) {
      alert("Location not available. Please wait...");
      return;
    }

    const description = prompt("Enter a description for this POI:");
    if (description) {
      // add the new POI to the state
      setPois((prevPois) => [
        ...prevPois,
        { lat: userLocation.lat, lng: userLocation.lng, description },
      ]);
    }
  };

  return (
    <div className="home-container">
      <MapContainer
        center={userLocation || { lat: 0, lng: 0 }}
        zoom={zoom}
        className="map-container"
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        {/* display the user's current location */}
        {userLocation && (
          <Marker position={userLocation} icon={userIcon}>
            <Popup>You are here</Popup>
          </Marker>
        )}
        {/* display all POIs on the map */}
        {pois.map((poi, index) => (
          <Marker key={index} position={{ lat: poi.lat, lng: poi.lng }} icon={poiIcon}>
            <Popup>
              <strong>Description:</strong> {poi.description} <br />
              <strong>Latitude:</strong> {poi.lat.toFixed(5)} <br />
              <strong>Longitude:</strong> {poi.lng.toFixed(5)}
            </Popup>
          </Marker>
        ))}
      </MapContainer>

      <div className="info-container">
        <h2>INFORMATION:</h2>
        <div className="info-grid">
          <div className="info-item">Speed:</div>
          <div className="info-item">
            LAT: {userLocation ? userLocation.lat.toFixed(5) : "Loading..."}
          </div>
          <div className="info-item">Distance:</div>
          <div className="info-item">
            LONG: {userLocation ? userLocation.lng.toFixed(5) : "Loading..."}
          </div>
          <div className="info-item">Altitude:</div>
          <div className="info-item">Time:</div>
        </div>
        <div className="button-group">
          <button className="add-poi-button" onClick={handleAddPoi}>
            ADD POI
          </button>
          <button className="view-satellites-button">VIEW SATELLITES</button>
        </div>
      </div>
    </div>
  );
};

export default Home;