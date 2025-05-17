import React, { useEffect, useState, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap, LayersControl } from 'react-leaflet';
import L from 'leaflet';
import { usePoi } from '../PoiContext';
import { NavLink, useLocation } from 'react-router-dom';
import { useTheme } from '../ThemeContext';
import './Home.css';
import Footer from '../components/Footer';

// PiRail logo - light and dark mode
const logoLight = `/pirailBlack.png`;
const logoDark = `/pirailWhite.png`;

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

// user icon - represents the user's location (by a train gif)
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
  /* user location and alt */
  const [config, setConfig] = useState(null);
  const [enabled, setEnabled] = useState(true);
  const [userLocation, setUserLocation] = useState(null);
  const [altitude, setAltitude] = useState(null);
  const [userSpeed, setSpeed] = useState(null);
  const [userDistance, setDistance] = useState(null);
  const [pois, setPois] = usePoi();
  const [zoom] = useState(16);
  const [showModal, setShowModal] = useState(false);
  const [poiDescription, setPoiDescription] = useState('');
  const [editingIndex, setEditingIndex] = useState(null);
  /* delete confirmation modal */
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteIndex, setDeleteIndex] = useState(null);
  /* handle dark/light mode */
  const { isDarkMode } = useTheme();
  /* ref for map instance */
  const mapRef = useRef(null);
  /* track the current time */
  const [currentTime, setCurrentTime] = useState(false);
  /* toggling info tab (mobile!) */
  const [isInfoTabOpen, setIsInfoTabOpen] = useState(false);
  const [startY, setStartY] = useState(0);
  /* tracking map centering - and if lock mode is active */
  const [isCentering, setIsCentering] = useState(true);
  const [mapLayer, setMapLayer] = useState("light");
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);
  /* check if the user is online/offline */
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  
  /* toggle map centering */
  const handleCenterMap = () => {
    setIsCentering((prev) => !prev); // toggle based on last state
  };

  /* toggle the info tab, this for mobile drag up */
  const toggleInfoTab = () => {
    setIsInfoTabOpen((prev) => !prev);
  
    // move the buttons based on the tab state */
    const buttons = document.querySelectorAll('.center-map-button, .add-poi-button');
    buttons.forEach((button) => {
      if (!isInfoTabOpen) {
        button.classList.add('move-up');
      } else {
        button.classList.remove('move-up');
      }
    });
  };

  /* handle touch start for info tab */
  const handleTouchStart = (e) => {
    setStartY(e.touches[0].clientY);
  };
  
  /* handle touch move for info tab */
  const handleTouchMove = (e) => {
    const deltaY = e.touches[0].clientY - startY;

    if (deltaY > 30) {
      setIsInfoTabOpen(false);
      document.querySelectorAll('.center-map-button, .add-poi-button').forEach((button) => {
        button.classList.remove('move-up');
      });
    } else if (deltaY < -30) {
      setIsInfoTabOpen(true);
      document.querySelectorAll('.center-map-button, .add-poi-button').forEach((button) => {
        button.classList.add('move-up');
      });
    }
  };
  
  /* touch end */
  const handleTouchEnd = () => {
    setStartY(0);
  };

  /* check if the user is online/offline - handle switching */
  useEffect(() => {
    const goOnline = () => setIsOnline(true);
    const goOffline = () => setIsOnline(false);
  
    window.addEventListener('online', goOnline);
    window.addEventListener('offline', goOffline);
  
    return () => {
      window.removeEventListener('online', goOnline);
      window.removeEventListener('offline', goOffline);
    };
  }, []);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 768);
    };
  
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  

  /* switch the map layers based on the dark/light mode */
  useEffect(() => {
    setMapLayer(isDarkMode ? "dark" : "light");
  }, [isDarkMode]);

  useEffect(() => {
    fetch('/config')
      .then((res) => res.json())
      .then((data) => {
        setConfig(data);
        setEnabled(Boolean(data.gps?.enable) || Boolean(data.sim?.enable));
        console.log('Config fetched');
      })
      .catch((err) => {
        console.error('Error fetching config:', err);
    });

    if (enabled) {
      // Initialize SSE connection to gps_stream
      const gpsStream = new EventSource("/packets?count=1000");
        gpsStream.addEventListener("pirail_TPV", handleDataUpdate);
      
        gpsStream.onopen = function() {
          console.log("gps connection opened");
        };

        gpsStream.onerror = function() {
          console.log("gps connection error");
        };

        return () => {
          gpsStream.close();
        };
    }
  }, []);

  const handleDataUpdate = (event) => {
    //console.log(event);
    var tpv = JSON.parse(event.data);
    //console.log(tpv)

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
      // if speed greater than the error, must be moving
      if (tpv.speed > tpv.eps) {
        setSpeed(Math.round(tpv.speed*ms_to_mph))
      } else {
        setSpeed(0)
      }
    } else {
      setSpeed(-1)
    }
    // Odometer
    if (tpv.odometer != undefined) {
      setDistance(tpv.odometer.toFixed(3))
    }
    // Time
    if (tpv.time != undefined) {
      if (tpv.simulated) {
        setCurrentTime(tpv.time.replace('T', ' ').split('.')[0])
      } else {
        setCurrentTime(tpv.time.split('T')[1].split('.')[0])
      }
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

  /* submit poi data - whether editing or adding */
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

  /* editing a POI - activate modal */
  const handleEditPoi = (index) => {
    setEditingIndex(index);
    setPoiDescription(pois[index].description);
    setShowModal(true);
  };

  /* delete a POI - activate modal */
  const handleDeletePoi = (index) => {
    setDeleteIndex(index);
    setShowDeleteModal(true);
  };

  /* confirm delete POI */
  const confirmDeletePoi = () => {
    if (deleteIndex !== null) {
      const updatedPois = pois.filter((_, i) => i !== deleteIndex);
      setPois(updatedPois);
      setShowDeleteModal(false);
      setDeleteIndex(null);
    }
  };

  /* close the modal containing the POI form */
  const handleModalClose = () => {
    setPoiDescription('');
    setShowModal(false);
  };

  const lightLayer = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"; /* link to light map */
  const darkLayer = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"; /* link to dark map */

  return (
    <div className={isDarkMode ? 'home-container dark-mode' : 'home-container'}>
      {/* new fullscreen map! this is using OSM and ORM */}
      {enabled ? <MapContainer
        center={userLocation || { lat: 0, lng: 0 }}
        zoom={zoom}
        className="map-container"
        attributionControl={false}
        whenCreated={(map) => (mapRef.current = map)}
      >
        {/* layers control for map - this is necessary to change map sources */}
        <LayersControl position="topright">
          <LayersControl.BaseLayer checked name="OpenStreetMap">
            <TileLayer
              url={
                isOnline // check if online or offline
                  ? (
                      mapLayer === "dark" // check if dark mode is enabled
                        ? "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" // online dark map
                        : "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" // online light map
                    )
                  : (
                      mapLayer === "dark" // check if dark mode is enabled
                        ? "/tiles/dark/{z}/{x}/{y}.png" // offline dark map
                        : "/tiles/light/{z}/{x}/{y}.png" // offline light map
                    )
              }
              attribution='&copy; OpenStreetMap contributors & CartoDB'
            />
          </LayersControl.BaseLayer>
          {/* ORM overlay */}
          <LayersControl.Overlay checked name="Railways (OpenRailwayMap)">
            <TileLayer
              url="https://{s}.tiles.openrailwaymap.org/standard/{z}/{x}/{y}.png"
              attribution='&copy; OpenRailwayMap contributors'
              opacity={0.7}
            />
          </LayersControl.Overlay>
        </LayersControl>

        {/* user's current location marker - uses the centering/lock functionality */}
        {userLocation && (
          <RecenterMap 
            center={userLocation} 
            isCentering={isCentering} 
            setIsCentering={setIsCentering} 
          />
        )}
        {userLocation && (
          <Marker position={userLocation} icon={userIcon}>
            <Popup>You are here!</Popup>
          </Marker>
        )}

        {/* need to render the POI markers */}
        {pois.map((poi, index) => (
          <Marker key={index} position={{ lat: poi.lat, lng: poi.lng }} icon={poiIcon}>
            <Popup>
              <strong>Description:</strong> {poi.description} <br />
              <strong>Latitude:</strong> {poi.lat.toFixed(5)} <br />
              <strong>Longitude:</strong> {poi.lng.toFixed(5)} <br />
              <button onClick={() => handleEditPoi(index)}>Edit</button>
              <button onClick={() => handleDeletePoi(index)}>Delete</button>
            </Popup>
          </Marker>
        ))}
      </MapContainer> : <div id="map-disabled">GPS disabled - turn on in settings</div>}
  

      {/* mobile info tab - swipe up to view */}
      {isMobile && (
        <div 
          className={`info-tab-container ${isInfoTabOpen ? 'open' : ''}`} 
          onTouchStart={handleTouchStart}
          onTouchMove={handleTouchMove}
          onTouchEnd={handleTouchEnd}
        >
          <div className="info-tab-header" onClick={toggleInfoTab}>
            <div className="tab-handle"></div>
          </div>

          <div className="info-tab-content">
            <div className="info-grid">
              <div className="info-item">
	        Speed: {userSpeed >= 0 ? `${userSpeed} mph` : 'Loading...'}
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
                Altitude: {altitude ? altitude : 'Loading...'}
              </div>
              <div className="info-item">
                Time: {currentTime ? `${currentTime}` : 'Loading...'}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* info section - this time it is for desktop! */}
      <div className="info-box">
        <div className="info-grid">
          <div className="info-item">
            Speed: {userSpeed >= 0 ? `${userSpeed} mph` : 'Loading...'}
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
      </div>

      {/* button to recenter/lock the map */}
      <button
        className={`center-map-button ${isInfoTabOpen ? 'move-up' : ''}`}
        onClick={handleCenterMap}
        title={isCentering ? 'Enable Free Scroll' : 'Enable GPS Lock'}
      >
        <img
          src={
            isDarkMode
              ? isCentering
                ? `/navigationicon_darkEnabled.png`
                : `/navigationicon_darkDisabled.png`
              : isCentering
                ? `/navigationicon_lightEnabled.png`
                : `/navigationicon_lightDisabled.png`
          }
          alt={isCentering ? 'GPS Lock Enabled' : 'Free Scroll Enabled'}
          className="center-map-icon"
        />
      </button>

      {/* button to add a POI */}
      <button 
        className={`add-poi-button ${isInfoTabOpen ? 'move-up' : ''}`} 
        onClick={handleAddPoi}
        title="Add POI"
      >
        <img 
          src={`/${isDarkMode ? 'addPOIDARK.png' : 'addPOILIGHT.png'}`} 
          alt="Add POI" 
          className="add-poi-icon" 
        />
      </button>

      <div className="network-status">
        {isOnline ? "🛰️ Online Map" : "📦 Offline Map"}
      </div>

      {/* modal for adding/editing POI */}
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

      {/* delete confirmation modal */}
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

      {/* footer - not sure if i need this anymore? going to keep for now. */}
      <Footer />
    </div>
  );
};

export default Home;
