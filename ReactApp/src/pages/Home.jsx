import React, { useEffect, useState, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap, LayersControl } from 'react-leaflet';
import L from 'leaflet';
import { usePoi } from '../PoiContext';
import './Home.css';
import Footer from '../components/Footer';

// Metric to imperial conversions
var m_to_ft = 3.28084;
var ms_to_mph = 2.23694;
var deg_to_rad = 0.0174533;

// icons for POI and user location
const poiIcon = new L.Icon({
  iconUrl: `mapMarker.png`,
  iconSize: [30, 30],
  iconAnchor: [15, 30],
  popupAnchor: [0, -30],
});

const userIcon = new L.Icon({
  iconUrl: `train.gif`,
  iconSize: [25, 25],
  iconAnchor: [12, 25],
  popupAnchor: [0, -25],
});

// recenter map when user location changes (only if user hasn't interacted in 5 seconds)
const RecenterMap = ({ center }) => {
  const map = useMap();
  const [isInteracting, setIsInteracting] = useState(false);
  const interactionTimeout = useRef(null);

  useEffect(() => {
    // called after an interaction
    const handleStartInteraction = () => { 
      setIsInteracting(true); // set interacting to true
      clearTimeout(interactionTimeout.current); // clear the timeout
    };

    const handleEndInteraction = () => {
      clearTimeout(interactionTimeout.current); // clear previous timeouts
      interactionTimeout.current = setTimeout(() => {
        setIsInteracting(false);
      }, 3000); // start 3-second timer *after* user stops interacting
    };

    // detect interactions
    map.on("dragstart", handleStartInteraction);
    map.on("zoomstart", handleStartInteraction);
    map.on("dragend", handleEndInteraction);
    map.on("zoomend", handleEndInteraction);

    // remove listeners and clear timeouts after unmount
    return () => {
      map.off("dragstart", handleStartInteraction);
      map.off("zoomstart", handleStartInteraction);
      map.off("dragend", handleEndInteraction);
      map.off("zoomend", handleEndInteraction);
      clearTimeout(interactionTimeout.current);
    };
  }, [map]); // when map is init, run

  useEffect(() => {
    // only recenter map if use is not interacting
    if (!isInteracting && center) {
      map.setView(center); // move map to center
    }
  }, [isInteracting, center, map]); // center or isInteracting has changed, run!
  return null;
};

const Home = () => {
  const [userLocation, setUserLocation] = useState(null);
  const [altitude, setAltitude] = useState(null);
  const [userSpeed, setSpeed] = useState(null);
  const [userDistance, setDistance] = useState(null);
  const [pois, setPois] = usePoi();
  const [zoom] = useState(13);
  const [currentTime, setCurrentTime] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [poiDescription, setPoiDescription] = useState('');
  const [editingIndex, setEditingIndex] = useState(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteIndex, setDeleteIndex] = useState(null);

  useEffect(() => {
  // Initialize SSE connection to gps_stream
  const gpsStream = new EventSource("/packets?count=1000");
    gpsStream.addEventListener("pirail_TPV", handleDataUpdate);
  
    return () => {
      gpsStream.close();
    };
  }, []);

  const handleDataUpdate = (event) => {
    console.log(event);
    var tpv = JSON.parse(event.data);

    // Location
    if (tpv.lat !== undefined && tpv.lon !== undefined) {
      setUserLocation({ lat: tpv.lat, lng: tpv.lon });
    }
    // Altitude
    if (tpv.alt != undefined) {
      setAltitude(tpv.alt.toLocaleString('en-US',{minimumFractionDigits:1, maximumFractionDigits: 1}))
    } 
    // Speed
    if (tpv.speed != undefined) {
      setSpeed(Math.round(tpv.speed*ms_to_mph))
    }
    // Odometer
    if (tpv.odometer != undefined) {
      setDistance(tpv.odometer.toFixed(3))
    }
    // Time
    if (tpv.time != undefined) {
      setCurrentTime(tpv.time.split('T')[1].split('.')[0])
    }
  };

  const handleAddPoi = () => {
    if (!userLocation) {
      alert('Location not available. Please wait...');
      return;
    }
    setShowModal(true);
    setEditingIndex(null);
  };

  const handleModalSubmit = () => {
    if (poiDescription.trim()) {
      if (editingIndex !== null) {
        // editing existing POI
        const updatedPois = [...pois];
        updatedPois[editingIndex].description = poiDescription;
        setPois(updatedPois);
      } else {
        // adding new POI
        setPois((prevPois) => [
          ...prevPois,
          { lat: userLocation.lat, lng: userLocation.lng, description: poiDescription },
        ]);
      }

      setPoiDescription('');
      setShowModal(false);
    } else {
      alert('Description cannot be empty.');
    }
  };

  const handleEditPoi = (index) => {
    setEditingIndex(index);
    setPoiDescription(pois[index].description);
    setShowModal(true);
  };

  const handleDeletePoi = (index) => {
    setDeleteIndex(index);
    setShowDeleteModal(true);
  };

  const confirmDeletePoi = () => {
    if (deleteIndex !== null) {
      const updatedPois = pois.filter((_, i) => i !== deleteIndex);
      setPois(updatedPois);
      setShowDeleteModal(false);
      setDeleteIndex(null);
    }
  };

  const handleModalClose = () => {
    setPoiDescription('');
    setShowModal(false);
  };

  return (
    <div className="home-container">
      <MapContainer
        center={userLocation || { lat: 0, lng: 0 }}
        zoom={zoom}
        className="map-container"
      >
        <LayersControl position="topright">
          {/* base: OSM */}
          <LayersControl.BaseLayer checked name="OpenStreetMap">
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            />
          </LayersControl.BaseLayer>

          {/* layer: ORM */}
          <LayersControl.Overlay checked name="Railways (OpenRailwayMap)">
            <TileLayer
              url="https://{s}.tiles.openrailwaymap.org/standard/{z}/{x}/{y}.png"
              attribution='&copy; <a href="https://www.openrailwaymap.org/">OpenRailwayMap</a> contributors'
              opacity={0.7}
            />
          </LayersControl.Overlay>
        </LayersControl>

        {userLocation && <RecenterMap center={userLocation} />}

        {userLocation && (
          <Marker position={userLocation} icon={userIcon}>
            <Popup>You are here!</Popup>
          </Marker>
        )}

        {pois.map((poi, index) => (
          <Marker key={index} position={{ lat: poi.lat, lng: poi.lng }} icon={poiIcon}>
            <Popup>
              <strong>Description:</strong> {poi.description} <br />
              <strong>Latitude:</strong> {poi.lat.toFixed(5)} <br />
              <strong>Longitude:</strong> {poi.lng.toFixed(5)} <br />
              <button onClick={() => handleEditPoi(index)} className="edit-button">Edit</button>
              <button onClick={() => handleDeletePoi(index)} className="delete-button">Delete</button>
            </Popup>
          </Marker>
        ))}
      </MapContainer>

      <div className="info-container">
        <h2>INFORMATION:</h2>
        <div className="info-grid">
          <div className="info-item">
            Speed: {userSpeed ? `${userSpeed} mph` : 'Loading...'}
          </div>
          <div className="info-item">
            LAT: {userLocation ? userLocation.lat.toFixed(5) : 'Loading...'}
          </div>
          <div className="info-item">
            Distance: {userDistance ? `${userDistance} mi` : 'Loading...'}
          </div>
          <div className="info-item">
            LONG: {userLocation ? userLocation.lng.toFixed(5) : 'Loading...'}
          </div>
          <div className="info-item">
            Altitude: {altitude ? `${altitude}'` : 'Loading...'}
          </div>
          <div className="info-item">
            Time: {currentTime ? `${currentTime}` : 'Loading...'}
          </div>
        </div>
        <div className="button-group">
          <button className="add-poi-button" onClick={handleAddPoi}>
            ADD POI
          </button>
          <button className="view-satellites-button">VIEW SATELLITES</button>
        </div>
      </div>

      {showModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h2>{editingIndex !== null ? "Edit a Point of Interest" : "Add a Point of Interest"}</h2>
            <textarea
              placeholder="Enter a description for this POI"
              value={poiDescription}
              onChange={(e) => setPoiDescription(e.target.value)}
              className="modal-textarea"
            ></textarea>
            <div className="modal-buttons">
              <button className="modal-button" onClick={handleModalSubmit}>
                {editingIndex !== null ? "EDIT" : "ADD"}
              </button>
              <button className="modal-button cancel" onClick={handleModalClose}>
                CANCEL
              </button>
            </div>
          </div>
        </div>
      )}
      {showDeleteModal && deleteIndex !== null && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h2>Confirm Delete</h2>
            <p>Are you sure you'd like to delete the POI: <strong>{pois[deleteIndex]?.description}</strong>?</p>
            <div className="modal-buttons">
              <button className="modal-button delete" onClick={confirmDeletePoi}>
                DELETE
              </button>
              <button className="modal-button cancel" onClick={() => setShowDeleteModal(false)}>
                CANCEL
              </button>
            </div>
          </div>
        </div>
      )}

      <Footer />
    </div>
  );
};

export default Home;